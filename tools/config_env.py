"""
Configures vbase's .env settings.
Asks user a series of questions to prepare the .env configuration file.
"""

import os
import secrets
from eth_account import Account


DEFAULT_ENV_CONTENTS = """
# Forwarder Configuration
# URL of the production vBase forwarder service.
# Users should not change this value.
FORWARDER_ENDPOINT_URL="https://api.vbase.com/forwarder/"
# User API key for accessing the vBase forwarder service.
# Users should set this value to the API key they received from vBase.
FORWARDER_API_KEY="USER_VBASE_API_KEY"

# User Private Key
# The private key for making stamps/commitments.
# This key signs and controls all operations -- it must be kept secret.
# vBase will never request this value.
PRIVATE_KEY="USER_PRIVATE_KEY"
"""


def ask_yes_no_question(question: str, default: str) -> bool:
    """
    Asks user a yes/no question.

    :param question: The question to ask the user.
    :param default: The default response value.
    :returns: The user response conversed to a boolean.
    """
    while True:
        answer = input(f"{question} (y/n) [{default}]: ").strip()
        if not answer:
            answer = default
        if answer in ["yes", "y"]:
            return True
        if answer in ["no", "n"]:
            return False
        print("Invalid input. Please enter yes/no or y/n.")


def ask_string_question(question: str, default=None):
    """
    Asks user a string question.

    :param question: The question to ask the user.
    :param default: The default response value.
    :returns: The user response.
    """
    while True:
        answer = input(f"{question} [{default}]: ").strip()
        if not answer:
            if default is not None:
                return default
            print("Invalid input. Please enter a non-empty string.")
        else:
            return answer


def main():
    """
    Main function for the tool.
    """
    print(
        "This tool will ask a series of questions to configure settings stored in the .env file."
    )

    file_path = ".env"
    # Check that the file to be configured exists.
    if not os.path.exists(file_path):
        with open(".env", "w") as file:
            file.write(DEFAULT_ENV_CONTENTS.strip())
        print("\nCreated a default .env file.")

    # Read the content of the .env file.
    with open(file_path, encoding="utf-8") as file:
        lines = file.readlines()

    if ask_yes_no_question(
        "\nDo you want to configure the vBase API key?\n",
        "yes",
    ):
        vbase_api_key = ask_string_question(
            "Please enter the vBase API key"
        )
        for i, line in enumerate(lines):
            if "FORWARDER_API_KEY" in line:
                lines[i] = f'FORWARDER_API_KEY = "{vbase_api_key}"\n'

    if ask_yes_no_question("\nDo you want to generate a new private key?", "yes"):
        private_key = "0x" + secrets.token_hex(32)
        # The following line creates overactive warning
        # because of difficulties with a decorated declaration:
        # No value for argument 'private_key' in unbound method call (no-value-for-parameter)
        # pylint: disable=E1120
        account = Account.from_key(private_key=private_key)
        # Update .env with the new private key and account.
        print(f"\nGenerated private key for a new account: {account.address}")
        # Find the line containing the PRIVATE_KEY and update it
        for i, line in enumerate(lines):
            if "PRIVATE_KEY" in line:
                lines[i] = f'PRIVATE_KEY = "{private_key}"\n'

    if ask_yes_no_question(
        "\nDo you want to configure AWS access keys?\n"
        "(These are the environment variables used to configure the AWS CLI\n"
        "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)\n",
        "yes",
    ):
        aws_access_key_id = ask_string_question("\nPlease enter the AWS_ACCESS_KEY_ID")
        aws_secret_access_key = ask_string_question(
            "Please enter the AWS_SECRET_ACCESS_KEY"
        )
        for i, line in enumerate(lines):
            if "AWS_ACCESS_KEY_ID" in line:
                lines[i] = f'AWS_ACCESS_KEY_ID = "{aws_access_key_id}"\n'
            if "AWS_SECRET_ACCESS_KEY" in line:
                lines[i] = f'AWS_SECRET_ACCESS_KEY = "{aws_secret_access_key}"\n'

    # Write the updated content back to the .env file.
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)

    print("\nThe .env file has been updated.")


if __name__ == "__main__":
    main()
