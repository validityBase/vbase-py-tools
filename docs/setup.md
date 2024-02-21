# Setup

## Install the c2-py library

- Clone the `c2-py` repository `https://github.com/pit-labs/c2-py.git`.
  - `c2-py` is the Python library for interacting with the validityBase (vBase) environment. 
  It is required by most command-line tools and data science workflows.
  - At the time of this limited release, the repository is private. 
  It can be cloned using GitHub Desktop or another authenticated solution.
  - This guide assumes the repository has been cloned to the local path `~/c2/c2-py`.
- Install the `c2py` Python package from the cloned repository:
```commandline
pip install ~/c2/c2-py
```

## Install c2-py-tools

- Clone the `c2-py-tools` repository `https://github.com/pit-labs/c2-py-tools.git`.
  - `c2-py-tools` is a set of common Python APIs and command-line wrappers for high-level
  data science operations.
  - At the time of this limited release, the repository is private. 
  It can be cloned using GitHub Desktop or another authenticated solution.
  - This guide assumes the repository has been cloned to the local path `~/c2/c2-py-tools`.
- Install requirements:
```commandline
pip3 install -r requirements.txt
```
- Command-line tools can be run from the `~/c2/c2-py-tools` working directory.
- Test vBase connectivity and basic functionality:
```commandline
cd ~/c2/c2-py-tools
python3 -m c2tools.tests.test_c2_basics
```

## Configure c2-py-tools

vBase tools can be configured using an automatic configuration script or manually.
We recommend an automatic configuration for the initial setup.

### Use the automatic configuration script

Run the following script to automatically configure settings stored in the .env file.  
The script will ask a few questions and initialize the appropriate environment variables.

```commandline
cd ~/c2/c2-py-tools
python3 -m c2tools.tools.config_env
```

```text
Do you want to generate a new private key? (y/n) [yes]:
```
Press `yes` if you wish to generate a new private key and address. 
This should typically be done once upon the initial configuration. 
You should not share the private key.
The script will print the address associated with the private key.

**You should share the generated address with PIT Labs for monitoring 
and funding the network transaction fee coss.** 

```text
Do you want to configure AWS access keys?
```
This is the option to configure the environment variables used for AWS access.
These are the same access keys as those used in AWS CLI tools 
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)


### Manually configure .env

- Configure the environment variables for `c2-py-tools` by editing `~/c2/c2-py-tools/.env`:
```python
# Private key for accessing vBase services:
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
...
# AWS configuration:
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
```
- Below are additional details on the environment variables: 
  - `PRIVATE_KEY` is the (private) cryptographic key suitable for signing Ethereum transactions.
  It can be generated using any of the mature key generation tools (https://ethereum.org/en/developers/docs/accounts/#account-creation, https://support.metamask.io/hc/en-us/articles/360015289632-How-to-export-an-account-s-private-key). 
  Please keep the key private and do not disclose it to PitLabs or anyone else.
  Only the public address associated with the key is required for validation.
  The private key secures your access to vBase.
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` must be defined for AWS operations such as S3 object commitment and validation.

## Run c2-py-tools

vBase Python tools are now installed and configured. You can run them from the command line:
```commandline
cd ~/c2/c2-py-tools
python3 -m c2tools.tools.commit_s3_objects --h
```
