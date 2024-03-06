# Setup

## Install vbase-py

Install the vBase Python SDK:
```commandline
pip install git+https://github.com/validityBase/vbase-py.git
```

## Install vbase-py-tools

Clone the `vbase-py-tools` repository `https://github.com/validityBase/vbase-py-tools.git`.

`vbase-py-tools` is a set of common Python tools for high-level data science operations. 
This guide assumes the repository has been cloned to the local path `~/validityBase/vbase-py-tools`.

Install requirements:
```commandline
pip3 install -r requirements.txt
```
Command-line tools can now be run from the `~/validityBase/vbase-py-tools` working directory.

## Configure vbase-py-tools

vBase tools can be configured using an automatic configuration script or manually.
We recommend an automatic configuration for the initial setup.

### Use the automatic configuration script

Run the following script to automatically configure settings stored in the .env file.  
The script will ask a few questions and initialize the appropriate environment variables.

```commandline
cd ~/validityBase/vbase-py-tools
python3 -m tools.config_env
```

You will be asked the following questions to configure the settings:

```text
Do you want to configure the vBase API key? (y/n) [yes]:
```
Press `yes` to enter the API key provided to you by vBase. 
This should typically be done once upon the initial configuration. 
The vBase API key and access to the API server are not required
to use vBase libraries, tools, and commitment services. They provide
simple and convenient abstractions of the underlying complexities of accessing
blockchains and managing cryptocurrencies.

```text
Do you want to generate a new private key? (y/n) [yes]:
```
Press `yes` if you wish to generate a new private key and address. 
This should typically be done once upon the initial configuration. 
You should not share the private key.
The script will print the address associated with the private key.

```text
Do you want to configure AWS access keys?
```
This is the option to configure the environment variables used for AWS access.
These are the same access keys as those used in AWS CLI tools 
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)
If you do not plan to use AWS integration tools, you can skip this option.

### Manually configure .env

- Configure the environment variables for `vbase-py-tools` by editing `~/validityBase/vbase-py-tools/.env`:
```python
# Forwarder Configuration
# URL of the production vBase forwarder service.
# Users should not change this value.
FORWARDER_ENDPOINT_URL="https://api.vbase.com/forwarder/"
# User API key for accessing the vBase forwarder service.
# Users should set this value to the API key they received from vBase.
FORWARDER_API_KEY = "FORWARDER_API_KEY"
...
# User Private Key
# The private key for making stamps/commitments.
# This key signs and controls all operations -- it must be kept secret.
# vBase will never request this value.
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
...
# AWS configuration:
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
```
- Below are additional details on the environment variables:
  - `FORWARDER_API_KEY` is the private API key for accessing the vBase API service.
  - `PRIVATE_KEY` is the (private) cryptographic key suitable for signing Ethereum transactions.
  It can be generated using any of the mature key generation tools (https://ethereum.org/en/developers/docs/accounts/#account-creation, https://support.metamask.io/hc/en-us/articles/360015289632-How-to-export-an-account-s-private-key). 
  Please keep the key private and do not disclose it to PitLabs or anyone else.
  Only the public address associated with the key is required for validation.
  The private key secures your access to vBase.
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` must be defined for AWS operations such as S3 object commitment and validation.

## Test Configuration
Test vBase connectivity and basic functionality:
```commandline
cd ~/validityBase/vbase-py-tools
python3 -m tests.test_vbase_basics
```

## Run vbase-py-tools

vBase Python tools are now installed and configured. You can run them from the command line:
```commandline
cd ~/validityBase/vbase-py-tools
python3 -m tools.commit_s3_objects --h
```
