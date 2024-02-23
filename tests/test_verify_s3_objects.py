"""
Tests of validityBase (vBase) commitment verification for one or more S3 objects.
These tests use Pit Labs' AWS data by default.
If you wish to run these tests, you will have to modify AWS parameters.
These test rely on the vBase connection and AWS settings stored in the .env file.
"""

import logging
import pprint
import unittest
import secrets
from dotenv import dotenv_values
import pandas as pd

from vbase import (
    get_default_logger,
    VBaseClientTest,
    VBaseDataset,
    VBaseStringObject,
)

from tools.utils import (
    get_s3_handle,
    get_all_matching_objects,
    read_s3_object,
)
from tools.verify_s3_objects import (
    build_argument_parser,
    verify_s3_objects,
)


_LOG = get_default_logger(__name__)
_LOG.setLevel(logging.INFO)

_BUCKET_NAME = "pitlabs-c2-test"
_KEY_PREFIX = "verify_s3_objects/"


class TestVerifyS3Objects(unittest.TestCase):
    """
    Test S3 object commitment verification.
    """

    def setUp(self):
        """
        Set up the tests.
        """
        # The verification tests require a test C2C contract to create test commitments.
        self.vbc = VBaseClientTest.create_instance_from_env(".env")
        self.env_vars = dotenv_values(".env")
        self.s3 = get_s3_handle(True, self.env_vars)

    def test_verify_key_prefix(self):
        """
        Test verification of objects with the verify_s3_objects() key_prefix option
        using default bucket settings.
        """
        # Use a random dataset name so that events do not clash between tests.
        # This allows us to run multiple tests without restarting a local node
        # or using a public testnet.
        dataset_name = "test_" + secrets.token_hex(32)

        # Create the dataset and the test dataset objects.
        ds = VBaseDataset(self.vbc, dataset_name, VBaseStringObject)
        objs = get_all_matching_objects(
            s3=self.s3, bucket=_BUCKET_NAME, key_prefix=_KEY_PREFIX
        )
        for obj in objs:
            data = read_s3_object(self.s3, _BUCKET_NAME, obj["Key"])
            t = pd.Timestamp(obj["LastModified"])
            ds.add_record_with_timestamp(record_data=data, timestamp=t)

        # Set up the test validate call for the above objects.
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                f"--dataset_name={dataset_name}",
                f"--bucket={_BUCKET_NAME}",
                f"--key_prefix={_KEY_PREFIX}",
                "--use_aws_access_key",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        status, validation_log = verify_s3_objects(args, self.env_vars)
        assert status

    def test_verify_key_prefix_missing_commitment(self):
        """
        Test verification of objects with the verify_s3_objects() key_prefix option
        using default bucket settings and a missing commitment.
        """
        dataset_name = "test_" + secrets.token_hex(32)
        ds = VBaseDataset(self.vbc, dataset_name, VBaseStringObject)
        objs = get_all_matching_objects(
            s3=self.s3, bucket=_BUCKET_NAME, key_prefix=_KEY_PREFIX
        )
        for obj in objs[:-1]:
            data = read_s3_object(self.s3, _BUCKET_NAME, obj["Key"])
            t = pd.Timestamp(obj["LastModified"])
            ds.add_record_with_timestamp(record_data=data, timestamp=t)
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                f"--dataset_name={dataset_name}",
                f"--bucket={_BUCKET_NAME}",
                f"--key_prefix={_KEY_PREFIX}",
                "--use_aws_access_key",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        status, validation_log = verify_s3_objects(args, self.env_vars)
        assert not status
        assert validation_log == [
            "Mismatched numbers of objects and commitments: objects = 3, commitments = 2"
        ]


if __name__ == "__main__":
    unittest.main()
