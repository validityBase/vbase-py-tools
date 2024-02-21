"""
Common validityBase (vBase) tools code
"""

import logging
import sys
from typing import Any
import boto3

from tools import (
    get_default_logger,
    C2,
    Web3HTTPCommitmentService,
    Web3HTTPCommitmentTestService,
)


_LOG = get_default_logger(__name__)
_LOG.setLevel(logging.INFO)


def check_env_var(env_vars_dict: dict[str, str | None], env_var_name: str):
    """
    Checks that an environment variable is defined.

    :param env_vars_dict: The environment variable dictionary.
    :param env_var_name: The environment variable that must be defined.
    """
    if env_var_name not in env_vars_dict:
        _LOG.error("The required %s .env variable is not set.", env_var_name)
        sys.exit(1)


def get_s3_handle(
    use_aws_access_key: bool = False, env_vars: dict[str, str | None] = None
) -> Any:
    """
    Constructs and returns an S3 handle for given settings.

    :param use_aws_access_key: True if AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        env_vars should be used; False otherwise.
    :param env_vars: The environment variable dictionary.
        Used iff use_aws_access_key is True.
    """
    # Verify the access settings and create the S3 client.
    if use_aws_access_key:
        # Get Set AWS credentials from .env
        # and set them up as environment variables.
        check_env_var(env_vars, "AWS_ACCESS_KEY_ID")
        check_env_var(env_vars, "AWS_SECRET_ACCESS_KEY")
        return boto3.client(
            "s3",
            aws_access_key_id=env_vars["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=env_vars["AWS_SECRET_ACCESS_KEY"],
        )
    assert env_vars is None
    return boto3.client("s3")


def get_c2_handle(test: bool = False, env_vars: dict[str, str | None] = None) -> C2:
    """
    Constructs and returns a vBase handle for given settings.

    :param test: True is the test commitment service should be used;
        False otherwise.
    :param env_vars: The environment variable dictionary.
    """
    check_env_var(env_vars, "ENDPOINT_URL")
    check_env_var(env_vars, "C2C_ADDRESS")
    if test:
        c2_class = Web3HTTPCommitmentTestService
    else:
        c2_class = Web3HTTPCommitmentService
    return C2(
        c2_class(
            endpoint_url=env_vars["ENDPOINT_URL"],
            c2c_address=env_vars["C2C_ADDRESS"],
            private_key=env_vars["PRIVATE_KEY"] if "PRIVATE_KEY" in env_vars else None,
            inject_geth_poa_middleware=bool(env_vars["INJECT_GETH_POA_MIDDLEWARE"])
            if "INJECT_GETH_POA_MIDDLEWARE" in env_vars
            else False,
        )
    )


def get_all_matching_objects(
    s3: Any, bucket: str, key_prefix: str = None
) -> list[dict]:
    """
    Worker function that retrieves all objects from a bucket,
    possibly using a key prefix.

    :param s3: The AWS S3 boto client object.
    :param bucket: The S3 bucket containing the object.
    :param key_prefix: The key prefix if matching using the prefix.
    :returns: The list of objects.
    """
    paginator = s3.get_paginator("list_objects_v2")
    if key_prefix is not None:
        operation_parameters = {"Bucket": bucket, "Prefix": key_prefix}
    else:
        operation_parameters = {"Bucket": bucket}
    page_iterator = paginator.paginate(**operation_parameters)
    all_objects = []
    for page in page_iterator:
        if "Contents" in page:
            all_objects.extend(page["Contents"])
    # Keep non-trivial objects.
    all_objects = [obj for obj in all_objects if obj["Size"] > 0]
    return all_objects


def read_s3_object(
    s3: Any,
    bucket: str,
    key: str,
    version_id: str | None = None,
) -> str:
    """
    Worker function returning a single S3 object.

    :param s3: The AWS S3 boto client object.
    :param bucket: The S3 bucket containing the object.
    :param key: The key for the object to be read.
    :param version_id: The version for the object to be read.
    :returns: The read object contents.
    """

    # Read the file from the S3 bucket
    file_content = ""
    try:
        _LOG.debug(
            "s3.get_object(): Bucket=%s, Key=%s, VersionId=%s", bucket, key, version_id
        )
        if version_id is not None:
            response = s3.get_object(Bucket=bucket, Key=key, VersionId=version_id)
        else:
            response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response["Body"].read().decode("utf-8")
        _LOG.debug("Characters read: %d", len(file_content))
    except Exception as e:
        _LOG.error("Error reading the object: %s", str(e))

    if len(file_content) == 0:
        _LOG.error("Empty object")

    return file_content
