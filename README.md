# List Spot Instances Pricing in all regions

This tool allow for getting the prices of spot instances in all AWS regions, for the current time.

Instances types can be configured by changing the list `INSTANCE_LIST` in the `list_spot_pricing.py` file.

## Requirements

- Python 2.7
- Boto3

## Usage

Run as `python2 list_spot_pricing.py --profile [PROFILE NAME] [-o output_file_name]`