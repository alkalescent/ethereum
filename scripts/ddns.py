"""Dynamic DNS updater for Route53."""

import os
from time import sleep

import boto3
import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv("config.env"))

TTL = 3600


def get_ip() -> str | None:
    """Fetch the current public IP address."""
    response = requests.get("https://4.ident.me", timeout=10)
    if response.ok:
        return response.text
    return None


def update_ddns(ip: str) -> dict:
    """Update the Route53 A record with the current IP.

    Args:
        ip: The IP address to set.

    Returns:
        The Route53 API response.
    """
    client = boto3.client("route53")
    response = client.change_resource_record_sets(
        ChangeBatch={
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": "eth.forcepu.sh",
                        "ResourceRecords": [
                            {
                                "Value": ip,
                            },
                        ],
                        "TTL": TTL,
                        "Type": "A",
                    },
                },
            ],
            "Comment": "DDNS",
        },
        HostedZoneId=os.environ["HOSTED_ZONE"],
    )
    return response


if __name__ == "__main__":
    while True:
        current_ip = get_ip()
        if current_ip:
            update_ddns(current_ip)
        sleep(TTL)
