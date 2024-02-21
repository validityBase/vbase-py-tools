"""
Tests basic validityBase (vBase) connectivity.
"""

from dotenv import dotenv_values
import unittest

vBaseimport Web3HTTPCommitmentService

from tools.utils import check_env_var


class TestVBaseBasics(unittest.TestCase):
    def test_package_installed(self):
        try:
            import c2
        except ImportError:
            self.fail("Package 'c2' is not installed correctly.")

    def test_commitment_service_connection(self):
        env_vars = dotenv_values(".env")
        check_env_var(env_vars, "ENDPOINT_URL")
        check_env_var(env_vars, "C2C_ADDRESS")
        check_env_var(env_vars, "PRIVATE_KEY")
        check_env_var(env_vars, "INJECT_GETH_POA_MIDDLEWARE")
        commitment_service = Web3HTTPCommitmentService(
            **Web3HTTPCommitmentService.get_dotenv_init_args()
        )
        assert commitment_service.w3.is_connected()


if __name__ == "__main__":
    unittest.main()
