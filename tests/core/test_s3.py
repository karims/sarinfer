# JjW4AdGJS29j44Kybeqi
import os

import boto3

# AWS_ACCESS_KEY_ID = "JjW4AdGJS29j44Kybeqi"
# AWS_SECRET_ACCESS_KEY = "QDSzBv8n81FfSOdMUT5NEtiNJQjRW2tSEFBb3zuE"

AWS_ACCESS_KEY_ID = "minioadmin"
AWS_SECRET_ACCESS_KEY = "minioadmin"

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

s3_client.list_objects_v2(Bucket="testllm")
