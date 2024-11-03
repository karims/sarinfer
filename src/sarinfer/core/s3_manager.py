import boto3
import os

from botocore.exceptions import ClientError

from sarinfer.logger import get_logger
from sarinfer.utils.exceptions import S3BucketNotFoundException, GenericS3Exception

# Load S3 bucket and credentials from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Get logger for this module
logger = get_logger(__name__)

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def upload_model_folder_to_s3(folder_path: str, bucket_name: str, s3_prefix: str = ''):
    """
    Uploads all files in a folder to the specified S3 bucket.
    :param folder_path: Path to the local folder to be uploaded.
    :param bucket_name: Name of the target S3 bucket.
    :param s3_prefix: (Optional) The S3 key prefix under which to store the folder content.
    """
    # Check if the bucket exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            raise S3BucketNotFoundException(f"The bucket {bucket_name} does not exist (404).")
        else:
            raise GenericS3Exception(f"An error occurred: {e}")

    try:
        # Walk through the folder recursively
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Full local path of the file
                local_file_path = os.path.join(root, file)

                # Create the S3 key by joining the prefix and relative file path
                relative_path = os.path.relpath(local_file_path, folder_path)
                s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")  # Convert to Unix-style path

                # Upload file to S3
                logger.info(f"Uploading {local_file_path} to s3://{bucket_name}/{s3_key}")
                s3_client.upload_file(local_file_path, bucket_name, s3_key)

        logger.info(f"Folder {folder_path} uploaded successfully to s3://{bucket_name}/{s3_prefix}")

    except Exception as e:
        logger.error(f"Failed to upload folder to S3: {e}")


def restore_model_folder_from_s3(bucket_name: str, s3_prefix: str, local_folder_path: str):
    """
    Restores all files in a folder from the specified S3 bucket and key prefix.
    :param bucket_name: Name of the S3 bucket.
    :param s3_prefix: The S3 key prefix where the folder is stored.
    :param local_folder_path: Path to the local folder where the content will be restored.
    """
    try:
        # Ensure local folder path exists
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)

        # List all objects with the specified prefix in S3
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)

        if "Contents" not in response:
            logger.info(f"No files found under s3://{bucket_name}/{s3_prefix}")
            return

        # Iterate over all files in the S3 folder and download them
        for obj in response.get("Contents", []):
            # Get the relative path within the S3 prefix
            s3_key = obj['Key']
            relative_path = os.path.relpath(s3_key, s3_prefix)

            # Construct the full local path for the file
            local_file_path = os.path.join(local_folder_path, relative_path)

            # Ensure local directory exists for the file
            local_dir = os.path.dirname(local_file_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            # Download the file from S3
            logger.info(f"Downloading s3://{bucket_name}/{s3_key} to {local_file_path}")
            s3_client.download_file(bucket_name, s3_key, local_file_path)

        logger.info(f"Folder restored successfully to {local_folder_path}.")

    except Exception as e:
        logger.error(f"Failed to restore folder from S3: {e}")
