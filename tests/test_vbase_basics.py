"""
Tests basic validityBase (vBase) connectivity.
"""

import unittest

from vbase import (
    VBaseClient,
    Web3HTTPCommitmentService,
    Web3HTTPCommitmentServiceTest,
    ForwarderCommitmentService,
    ForwarderCommitmentServiceTest,
)


class TestVBaseBasics(unittest.TestCase):
    def test_package_installed(self):
        try:
            import vbase
        except ImportError:
            self.fail("Package 'vbase' is not installed correctly.")

    def test_commitment_service_connection(self):
        # Connect to the service using the local environment variables
        # and verify the connection.
        vbc = VBaseClient.create_instance_from_env(".env")
        # Verify connectivity appropriately for various service types.
        if isinstance(vbc.commitment_service, Web3HTTPCommitmentService) or isinstance(
            vbc.commitment_service, Web3HTTPCommitmentServiceTest
        ):
            assert vbc.commitment_service.w3.is_connected()
        else:
            assert isinstance(
                vbc.commitment_service, ForwarderCommitmentService
            ) or isinstance(vbc.commitment_service, ForwarderCommitmentServiceTest)
            # We can verify the connection by getting signature data for the current user.
            signature_data = vbc.commitment_service._call_forwarder_api(
                "signature-data"
            )
            assert len(signature_data) > 0


if __name__ == "__main__":
    unittest.main()
