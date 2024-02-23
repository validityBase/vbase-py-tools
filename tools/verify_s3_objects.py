"""
Verifies validityBase (vBase) commitments for one or more S3 objects.
"""

import argparse
import fnmatch
import json
import logging
import pprint
from typing import Dict, List, Optional
from dotenv import dotenv_values
import pandas as pd

from vbase import (
    get_default_logger,
    VBaseClient,
    VBaseDataset,
    VBaseStringObject,
    Web3HTTPIndexingService,
)

from tools.utils import (
    get_s3_handle,
    get_all_matching_objects,
    read_s3_object,
)


_LOG = get_default_logger(__name__)
_LOG.setLevel(logging.INFO)


def build_argument_parser() -> argparse.ArgumentParser:
    """
    Define the ArgumentParser object and parameters.

    :return parser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        description="""
Verify validityBase (vBase) dataset commitments for S3 objects. 
Verifies timestamped signatures (commitments) for one or more S3 objects. 
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
        help="vBase dataset to verify",
    )
    parser.add_argument(
        "--bucket",
        type=str,
        required=True,
        help="S3 bucket name containing dataset records",
    )
    parser.add_argument(
        "--key_prefix",
        type=str,
        required=False,
        help="""
S3 object key prefix: 
If supplied, objects matching the prefix will be used to verify commitments. 
    """,
    )
    parser.add_argument(
        "--key_pattern",
        type=str,
        required=False,
        help="""
S3 object key pattern: 
If supplied, objects matching the wildcard pattern will be used to verify commitments.  
    """,
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
    # TODO: Add examples once the tool matures.
    parser.epilog = """
examples:
"""

    return parser


def verify_s3_objects(
    args: argparse.Namespace,
    env_vars: Dict[str, Optional[str]],
) -> (bool, List[str]):
    """
    Worker function processing the args to execute the task.
    Factoring out the worker allows easier unit tests with test args.

    :param args: The command arguments.
    :param env_vars: The environment variables containing static configuration.
    :returns: A tuple comprising the status and the log:
        True if verification succeeded; False otherwise.
        A list of verification messages if any failures were encountered.
    """
    print(f"Verifying S3 objects: {json.dumps(vars(args))}")

    if args.verbose:
        _LOG.setLevel(logging.DEBUG)

    # Verify the key settings.
    if (
        sum(
            [
                args.key_prefix is not None,
                args.key_pattern is not None,
            ]
        )
        != 1
    ):
        _LOG.error(
            "Exactly one of the arguments --key_prefix or --key_pattern must be provided."
        )

    # Static configuration such as S3 credentials and vBase access parameters
    # are stored in the .env file.
    s3 = get_s3_handle(args.use_aws_access_key, env_vars)
    vbc = VBaseClient.create_instance_from_env(".env")

    set_cid = VBaseDataset.get_set_cid_for_dataset(args.dataset_name)

    # Verify the dataset.
    user_address = vbc.get_default_user()
    assert user_address is not None

    # Record verification failure messages into a log to return to the caller.
    status = False
    validation_log = []

    # Check if the dataset commitment exists.
    if not vbc.user_set_exists(user_address, set_cid):
        _LOG.debug(
            "Dataset commitment does not exist: user = %s, "
            "dataset_name = %s, set_cid = %s",
            user_address,
            args.dataset_name,
            set_cid,
        )
        return status, validation_log

    # Process all dataset commitments and reconcile them against the objects.
    # Retrieve the S3 objects.
    assert args.key_prefix or args.key_pattern
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
        objs = [obj for obj in objs if fnmatch.fnmatch(obj["Key"], args.key_pattern)]

    # Sort the objects by time.
    objs.sort(key=lambda x: x["LastModified"])
    _LOG.debug("s3.list_objects_v2(): objects = %s", pprint.pformat(objs))

    # Get object hashes.
    hashes = []
    ts = []
    for obj in objs:
        data = read_s3_object(s3=s3, bucket=args.bucket, key=obj["Key"])
        hashes.append(VBaseStringObject.get_cid_for_data(data))
        ts.append(pd.Timestamp(obj["LastModified"]))

    # Query all commitments and sort by time.
    # TODO: Add support for forwarder indexing service.
    # Currently, the tool requires a direct Web3 node connection to query for events.
    commitment_receipts = (
        Web3HTTPIndexingService.create_instance_from_env_json_descriptor(
            ".env"
        ).find_user_set_objects(
            user=vbc.get_default_user(),
            set_cid=VBaseDataset.get_set_cid_for_dataset(args.dataset_name),
        )
    )

    # Objects and commitments should match 1-1.
    if len(hashes) != len(commitment_receipts):
        validation_log.append(
            f"Mismatched numbers of objects and commitments: objects = {len(hashes)}, "
            f"commitments = {len(commitment_receipts)}"
        )
        return status, validation_log
    for i, obj in enumerate(objs):
        _LOG.debug("Validating: key = %s", obj["Key"])
        # Verify that there is a commitment with object data that follows the object timestamp.
        if commitment_receipts[i]["objectCid"] != hashes[i]:
            validation_log.append(
                f"Mismatched entry: index = {i}, S3 object hash = {hashes[i]}, "
                f'commitment object hash = {commitment_receipts[i]["objectCid"]}'
            )
        if pd.Timestamp(commitment_receipts[i]["timestamp"]) - ts[i] < pd.Timedelta(
            "0 days"
        ):
            validation_log.append(
                f"Mismatched entry timestamps: index = {i}, S3 object timestamp = {ts[i]}, "
                f'commitment object timestamp = {commitment_receipts[i]["timestamp"]}'
            )

    # If we found no mismatches, the check succeeded.
    if len(validation_log) == 0:
        status = True

    return status, validation_log


def main():
    """
    Main function for the tool.
    """
    parser = build_argument_parser()
    args = parser.parse_args()
    verify_s3_objects(args, dotenv_values(".env"))


if __name__ == "__main__":
    main()
