"""
Configures vbase's .env settings.
Asks user a series of questions to prepare the .env configuration file.
"""

import os
import secrets
import sys
from eth_account import Account


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
        print(".env file not found.")
        sys.exit(1)

    # Read the content of the .env file.
    with open(file_path, encoding="utf-8") as file:
        lines = file.readlines()

    if ask_yes_no_question("\nDo you want to generate a new private key?", "yes"):
        private_key = "0x" + secrets.token_hex(32)
        # The following line creates overactive warning
        # because of difficulties with a decorated declaration:
        # No value for argument 'private_key' in unbound method call (no-value-for-parameter)
        # pylint: disable=E1120
        account = Account.from_key(private_key=private_key)
        # Update .env with the new private key and account.
        print(f"\nGenerated key for a new account: {account.address}")
        print("Please share this account with PIT Labs.")
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
