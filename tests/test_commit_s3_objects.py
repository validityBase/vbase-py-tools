"""
Tests of validityBase (vBase) commitments for one or more S3 objects.
These tests use Pit Labs' AWS data by default.
If you wish to run these tests, you will have to modify AWS parameters.
These test rely on the vBase connection and AWS settings stored in the .env file.
"""

import logging
import pprint
import unittest
from dotenv import dotenv_values

from vbase import (
    get_default_logger,
    VBaseClient,
)

from tools.commit_s3_objects import (
    build_argument_parser,
    commit_s3_objects,
)


_LOG = get_default_logger(__name__)
_LOG.setLevel(logging.INFO)


class TestCommitS3Objects(unittest.TestCase):
    """
    Test S3 object commitments.
    """

    def setUp(self):
        """
        Set up the tests.
        """
        self.vbc = VBaseClient.create_instance_from_env(".env")
        self.env_vars = dotenv_values(".env")

    def test_commit_test_1(self):
        """
        Test a commitment of "test_1.txt"
        using default bucket settings.
        """
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                "--dataset_name=test",
                "--bucket=pitlabs-c2-test",
                "--key=commit_s3_objects/test_1.txt",
                "--use_aws_access_key",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        commitment_receipt = commit_s3_objects(args, self.env_vars)[0]
        assert self.vbc.verify_user_object(
            commitment_receipt["user"],
            commitment_receipt["objectCid"],
            commitment_receipt["timestamp"],
        )

    def test_commit_test_1_verbose(self):
        """
        Test a commitment of "test_1.txt"
        using default bucket settings.
        """
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                "--dataset_name=test",
                "--bucket=pitlabs-c2-test",
                "--key=commit_s3_objects/test_1.txt",
                "--use_aws_access_key",
                "--verbose",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        commitment_receipt = commit_s3_objects(args, self.env_vars)[0]
        assert self.vbc.verify_user_object(
            commitment_receipt["user"],
            commitment_receipt["objectCid"],
            commitment_receipt["timestamp"],
        )

    def test_commit_key_prefix(self):
        """
        Test a commitment of the "commit_s3_objects" key_prefix
        using default bucket settings.
        """
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                "--dataset_name=test",
                "--bucket=pitlabs-c2-test",
                "--key_prefix=commit_s3_objects/",
                "--use_aws_access_key",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        commitment_receipts = commit_s3_objects(args, self.env_vars)
        for commitment_receipt in commitment_receipts:
            assert self.vbc.verify_user_object(
                commitment_receipt["user"],
                commitment_receipt["objectCid"],
                commitment_receipt["timestamp"],
            )

    def test_commit_key_pattern(self):
        """
        Test a commitment of the "commit_s3_objects" key_pattern
        using default bucket settings.
        """
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                "--dataset_name=test",
                "--bucket=pitlabs-c2-test",
                "--key_pattern=commit_s3_objects/*.txt",
                "--use_aws_access_key",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        commitment_receipts = commit_s3_objects(args, self.env_vars)
        for commitment_receipt in commitment_receipts:
            assert self.vbc.verify_user_object(
                commitment_receipt["user"],
                commitment_receipt["objectCid"],
                commitment_receipt["timestamp"],
            )

    def test_commit_key_pattern_verbose(self):
        """
        Test a commitment of the "commit_s3_objects" key_pattern
        using default bucket settings and verbose output.
        """
        parser = build_argument_parser()
        args = parser.parse_args(
            [
                "--dataset_name=test",
                "--bucket=pitlabs-c2-test",
                "--key_pattern=commit_s3_objects/*.txt",
                "--use_aws_access_key",
                "--verbose",
            ]
        )
        _LOG.info(f"Testing args:\n{pprint.pformat(vars(args))}")
        commitment_receipts = commit_s3_objects(args, self.env_vars)
        for commitment_receipt in commitment_receipts:
            assert self.vbc.verify_user_object(
                commitment_receipt["user"],
                commitment_receipt["objectCid"],
                commitment_receipt["timestamp"],
            )


if __name__ == "__main__":
    unittest.main()
