"""
Saves validityBase (vBase) commitments for one or more S3 objects.
"""

import argparse
import fnmatch
import json
import logging
import pprint
from typing import Any, Dict, Optional
from dotenv import dotenv_values

from tools import (
    get_default_logger,
    C2,
    C2StringSeries,
)

from tools.utils import (
    get_c2_handle,
    get_s3_handle,
    get_all_matching_objects,
    read_s3_object,
)


_LOG = get_default_logger(__name__)
_LOG.setLevel(logging.INFO)

# Batch size when committing batches of objects.
_COMMIT_OBJECT_BATCH_SIZE = 20


def build_argument_parser() -> argparse.ArgumentParser:
    """
    Define the ArgumentParser object and parameters.

    :return parser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        description="""
Create validityBase (vBase) dataset commitments for S3 objects. 
Records timestamped signatures (commitments) for one or more S3 objects. 
A commitment proves that an object was known to a user at a given point-in-time
and belonged to a given dataset.
Such commitments establish provenance and PIT accuracy of datasets and its records.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        required=True,
        help="vBase dataset to receive commitments",
    )
    parser.add_argument("--bucket", type=str, required=True, help="S3 bucket name")
    parser.add_argument(
        "--key",
        type=str,
        required=False,
        help="""
S3 object key: 
If supplied, a single object will be committed. 
--key, --key_prefix, or --key_pattern argument must be provided.
""",
    )
    parser.add_argument(
        "--key_prefix",
        type=str,
        required=False,
        help="""
S3 object key prefix: 
If supplied, objects matching the prefix will be committed. 
--key, --key_prefix, or --key_pattern argument must be provided.
    """,
    )
    parser.add_argument(
        "--key_pattern",
        type=str,
        required=False,
        help="""
S3 object key pattern: 
If supplied, objects matching the wildcard pattern will be committed.  
--key, --key_prefix, or --key_pattern argument must be provided.
    """,
    )
    parser.add_argument(
        "--version",
        type=str,
        required=False,
        choices=["latest", "version_id"],
        default="latest",
        help="""
S3 object version: 
If latest is specified, the latest object will be committed. 
If version_id is specified, --version_id argument must be provided, 
and the version specified by version_id will be committed.
The version_id option is only compatible with single object (--key argument) commitments. 
""",
    )
    parser.add_argument(
        "--version_id", type=str, required=False, help="S3 object version ID to commit"
    )
    parser.add_argument(
        "--use_aws_access_key",
        required=False,
        action="store_true",
        help="""
use AWS authentication: If specified, AWS Access Key defined in .env will be used. 
In this case, .env must define AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY variables.
""",
    )
    parser.add_argument(
        "--verbose", required=False, action="store_true", help="verbose output"
    )
    parser.add_argument(
        "--test", required=False, action="store_true", help="use a test vBase contract"
    )

    # Add usage examples to the help message
    parser.epilog = """
examples:
    python3 -m tools.commit_s3_objects --dataset_name=test --bucket=pitlabs-c2-test \
--key=commit_s3_objects/test_1.txt --use_aws_access_key
    python3 -m tools.commit_s3_objects --dataset_name=test --bucket=pitlabs-c2-test \
--key_prefix=commit_s3_objects/ --use_aws_access_key
    python3 -m tools.commit_s3_objects --dataset_name=test --bucket=pitlabs-c2-test \
--key_pattern=commit_s3_objects/*.txt --use_aws_access_key --verbose
"""

    return parser


def commit_s3_object_list(
    c2: C2, dataset_name: str, s3: Any, bucket: str, objs: list[dict]
) -> list[dict]:
    """
    Worker function processing the args to execute the task.
    Factoring out the worker allows easier unit tests with test args.

    :param c2: The vBase object.
    :param dataset_name: Name of the vBase set to receive the object hashes.
    :param s3: The AWS S3 boto client object.
    :param bucket: The S3 bucket containing the object.
    :param objs: The S3 objects to commit.
    :returns: The list of commitment receipt dictionaries.
    """
    set_hash = C2StringSeries.get_set_hash_for_dataset(dataset_name)

    # Commit objects batches.
    commitment_receipts = []
    for i in range(0, len(objs), _COMMIT_OBJECT_BATCH_SIZE):
        batch = objs[i : i + _COMMIT_OBJECT_BATCH_SIZE]
        # Build object hashes.
        object_hashes = []
        for obj in batch:
            # Get object hash for the object contents.
            key = obj["Key"]
            print(f"Committing object: {key}")
            file_content = read_s3_object(s3, bucket, key)
            object_hash = C2StringSeries.get_object_hash_for_dataset_record(
                dataset_name, file_content
            )
            object_hashes.append(object_hash)

        # Commit all hashes for the batch.
        commitment_receipt = {}
        try:
            commitment_receipt = c2.add_set_objects_batch(
                set_hash=set_hash,
                object_hashes=object_hashes,
            )
        except Exception as e:
            _LOG.error("Error posting commitment: %s", str(e))
        commitment_receipts += commitment_receipt
    return commitment_receipts


def commit_s3_objects(
    args: argparse.Namespace,
    env_vars: Dict[str, Optional[str]],
) -> list[dict]:
    """
    Worker function processing the args to execute the task.
    Factoring out the worker allows easier unit tests with test args.

    :param args: The command arguments.
    :param env_vars: The environment variables containing static configuration.
    :returns: The list of commitment receipt dictionaries.
    """
    print(f"Committing S3 objects: {json.dumps(vars(args))}")

    if args.verbose:
        _LOG.setLevel(logging.DEBUG)

    # Verify the version id settings.
    # If committing a specific version, the version_id argument should be present.
    if args.version == "version_id" and args.version_id is None:
        _LOG.error(
            'The --version_id argument is required when --version is set to "version_id".'
        )

    # Verify the key settings.
    provided_count = sum(
        [
            args.key is not None,
            args.key_prefix is not None,
            args.key_pattern is not None,
        ]
    )
    if provided_count != 1:
        _LOG.error(
            "Exactly one of the arguments --key, --key_prefix, or --key_pattern must be provided."
        )
    if (args.key_prefix or args.key_pattern) and args.version == "version_id":
        _LOG.error(
            "--key_prefix and --key_pattern arguments are not compatible with "
            '--version="version_id".'
        )

    # Static configuration such as S3 credentials and vBase access parameters
    # are stored in the .env file.
    s3 = get_s3_handle(args.use_aws_access_key, env_vars)
    c2 = get_c2_handle(args.test, env_vars)

    set_hash = C2StringSeries.get_set_hash_for_dataset(args.dataset_name)

    # Commit the dataset (set), if necessary.
    user_address = c2.get_default_user()
    assert user_address is not None
    if not c2.user_set_exists(user_address, set_hash):
        cl = c2.add_set(set_hash)
        assert cl == {
            "user": user_address,
            "setHash": set_hash,
        }

    commitment_receipts = []
    if args.key:
        # Commit a single object.
        assert not args.key_prefix
        print(f"Committing object: {args.key}")

        # Get object hash for the contents.
        file_content = read_s3_object(s3, args.bucket, args.key, args.version_id)
        object_hash = C2StringSeries.get_object_hash_for_dataset_record(
            args.dataset_name, file_content
        )

        # Post the object commitment.
        # Since we are merely adding a record to a dataset,
        # we just need to create a writable dataset
        # that receives the new record commitment.
        commitment_receipt = {}
        try:
            commitment_receipt = c2.add_set_object(
                set_hash=set_hash,
                object_hash=object_hash,
            )
        except Exception as e:
            _LOG.error("Error posting commitment: %s", str(e))
        commitment_receipts.append(commitment_receipt)

    elif args.key_prefix or args.key_pattern:
        # Commit all matching objects.
        assert args.version == "latest"

        if args.key_prefix:
            # List the S3 objects with the given prefix.
            objs = get_all_matching_objects(
                s3=s3, bucket=args.bucket, key_prefix=args.key_prefix
            )
        else:
            assert args.key_pattern
            # List all S3 objets in the bucket.
            objs = get_all_matching_objects(s3=s3, bucket=args.bucket)
            # Match the pattern.
            objs = [
                obj for obj in objs if fnmatch.fnmatch(obj["Key"], args.key_pattern)
            ]

        # Sort the results alphabetically.
        objs.sort(key=lambda x: x["Key"])
        _LOG.debug("s3.list_objects_v2(): objects = %s", pprint.pformat(objs))

        commitment_receipts = commit_s3_object_list(
            c2=c2, dataset_name=args.dataset_name, s3=s3, bucket=args.bucket, objs=objs
        )
    else:
        # Invalid object batch settings.
        assert args.key or args.key_prefix or args.key_pattern

    dataset_info = {
        "owner": commitment_receipts[0]["user"],
        "name": args.dataset_name,
        "hash": set_hash,
    }
    print("Successfully posted commitment.")
    print(f"Dataset: {json.dumps(dataset_info)}")
    print(f"Commitment receipts: {json.dumps(commitment_receipts)}")

    return commitment_receipts


def main():
    """
    Main function for the tool.
    """
    parser = build_argument_parser()
    args = parser.parse_args()
    commit_s3_objects(args, dotenv_values(".env"))


if __name__ == "__main__":
    main()
