"""
Common validityBase (vBase) tools code
"""

import logging
import sys
from typing import Any, Dict, Optional, List
import boto3

from vbase import get_default_logger


_LOG = get_default_logger(__name__)
_LOG.setLevel(logging.INFO)


def check_env_var(env_vars_dict: Dict[str, Optional[str]], env_var_name: str):
    """
    Checks that an environment variable is defined.

    :param env_vars_dict: The environment variable dictionary.
    :param env_var_name: The environment variable that must be defined.
    """
    if env_var_name not in env_vars_dict:
        _LOG.error("The required %s .env variable is not set.", env_var_name)
        sys.exit(1)


def get_s3_handle(
    use_aws_access_key: bool = False, env_vars: Dict[str, Optional[str]] = None
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


def get_all_matching_objects(
    s3: Any, bucket: str, key_prefix: str = None
) -> List[dict]:
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
    version_id: Optional[str] = None,
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
    # pylint: disable=broad-except
    except Exception as e:
        _LOG.error("Error reading the object: %s", str(e))

    if len(file_content) == 0:
        _LOG.error("Empty object")

    return file_content
