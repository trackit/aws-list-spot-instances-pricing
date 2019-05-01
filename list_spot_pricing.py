#!/bin/env python2

import boto3
import botocore
import csv
import pprint
import argparse
import ConfigParser
import os
import datetime

INSTANCES_LIST = ['g2.2xlarge', 'g2.8xlarge', 'p2.xlarge', 'p2.8xlarge', 'p2.16xlarge', 'p3.2xlarge', 'p3.8xlarge', 'p3.16xlarge', 'p3dn.24xlarge']

def get_spot_pricing(session, regions, account):
    res = []
    for region in regions:
        client = session.client('ec2', region_name=region)
        try:
            pricing_history = client.describe_spot_price_history(
                InstanceTypes=INSTANCES_LIST,
                ProductDescriptions=["Linux/UNIX (Amazon VPC)"],
                StartTime=datetime.datetime.now(),
                EndTime=datetime.datetime.now()
            )
            for spot in pricing_history["SpotPriceHistory"]:
                res.append({
                    "Price": spot["SpotPrice"],
                    "Instance Type": spot["InstanceType"],
                    "Region": region,
                    "Availability Zone": spot["AvailabilityZone"]
                })
        except Exception as e:
            print (e)
    return res

def get_regions(session):
    client = session.client('ec2')
    regions = client.describe_regions()
    return [
        region['RegionName']
        for region in regions['Regions']
    ]

def generate_csv(data, args, header_name):
    filename = "report.csv"
    if args['o']:
        filename = args['o']
    with open(filename, 'wb') as file:
        writer = csv.DictWriter(file, header_name)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def init():
    config_path = os.environ.get('HOME') + "/.aws/credentials"
    parser = ConfigParser.ConfigParser()
    parser.read(config_path)
    if parser.sections():
        return parser.sections()
    return []

def main():
    data = []
    parser = argparse.ArgumentParser(description="Get spot instances pricing for all regions for specified instances types")
    parser.add_argument("--profile", nargs="+", help="Specify AWS profile(s) (stored in ~/.aws/credentials) for the program to use")
    parser.add_argument("-o", nargs="?", help="Specify output csv file")
    parser.add_argument("--profiles-all", nargs="?", help="Run it on all profile")
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION')
    args = vars(parser.parse_args())
    if 'profiles-all' in args:
        keys = init()
    elif 'profile' in args and args['profile']:
        keys = args['profile']
    else:
        keys = init()
    for key in keys:
        print 'Processing %s...' % key
        try:
            if aws_access_key and aws_secret_key and aws_region:
                session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)
            else:
                session = boto3.Session(profile_name=key)
            regions = get_regions(session)
            data += get_spot_pricing(session, regions, key)
        except botocore.exceptions.ClientError, error:
            print error
    pprint.pprint(data)
    generate_csv(data, args, ['Region', 'Availability Zone', 'Instance Type', 'Price'])


if __name__ == '__main__':
    main()
