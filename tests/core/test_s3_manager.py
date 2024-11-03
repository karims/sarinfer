import boto3
import pytest
import os

from moto import mock_aws

from sarinfer.core.s3_manager import (upload_model_folder_to_s3,
                                      restore_model_folder_from_s3)
import tempfile
import shutil

from sarinfer.utils.exceptions import S3BucketNotFoundException


@pytest.fixture
def setup_local_folder():
    """
    Setup a temporary local folder for testing.
    Create some test files in it to simulate folder content.
    """
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    subfolder_path = os.path.join(temp_dir, "subfolder")
    os.makedirs(subfolder_path)

    # Create dummy files
    with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
        f.write("File 1 content")

    with open(os.path.join(subfolder_path, "file2.txt"), "w") as f:
        f.write("File 2 content")

    yield temp_dir
    shutil.rmtree(temp_dir)  # Clean up after the test


@mock_aws
def test_upload_folder_to_s3(setup_local_folder):
    """
    Test uploading a folder to S3 using Moto to mock S3 client interactions.
    """
    # Setup Moto mock S3 environment
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket="test-bucket")

    # Call the upload_folder_to_s3 function
    folder_path = setup_local_folder
    upload_model_folder_to_s3(folder_path, bucket_name="test-bucket", s3_prefix="models/llama_70b")

    # List objects in the bucket to verify uploads
    result = s3_client.list_objects_v2(Bucket="test-bucket", Prefix="models/llama_70b")

    # Verify that the two files were uploaded
    assert len(result.get("Contents", [])) == 2
    uploaded_keys = [obj['Key'] for obj in result['Contents']]
    assert "models/llama_70b/file1.txt" in uploaded_keys
    assert "models/llama_70b/subfolder/file2.txt" in uploaded_keys


@mock_aws()
def test_restore_folder_from_s3(setup_local_folder):
    """
    Test restoring a folder from S3 using Moto to mock S3 client interactions.
    """
    # Setup Moto mock S3 environment
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket="test-bucket")

    # Mock S3 files to simulate folder structure in S3
    s3_client.put_object(Bucket="test-bucket", Key="models/llama_70b/file1.txt", Body="File 1 content")
    s3_client.put_object(Bucket="test-bucket", Key="models/llama_70b/subfolder/file2.txt", Body="File 2 content")

    # Local folder where files will be restored
    local_folder_path = setup_local_folder

    # Call the restore_folder_from_s3 function
    restore_model_folder_from_s3(bucket_name="test-bucket", s3_prefix="models/llama_70b",
                                 local_folder_path=local_folder_path)

    # Verify that the files were restored locally
    assert os.path.exists(os.path.join(local_folder_path, "file1.txt"))
    assert os.path.exists(os.path.join(local_folder_path, "subfolder/file2.txt"))

    # Verify file contents
    with open(os.path.join(local_folder_path, "file1.txt"), "r") as f:
        assert f.read() == "File 1 content"

    with open(os.path.join(local_folder_path, "subfolder/file2.txt"), "r") as f:
        assert f.read() == "File 2 content"


@pytest.fixture
def setup_local_folder_empty():
    """
    Setup a temporary local folder for testing.
    """
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory

    # Print the contents of the folder immediately after creation
    print("Initial contents of temp folder:", os.listdir(temp_dir))

    yield temp_dir
    shutil.rmtree(temp_dir)  # Clean up after the test


@mock_aws()
def test_upload_empty_folder_to_s3(setup_local_folder_empty):
    """
    Test uploading an empty folder to S3. No files should be uploaded.
    """
    # Setup Moto mock S3 environment
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket="test-bucket")

    # Call the upload_folder_to_s3 function with an empty folder
    folder_path = setup_local_folder_empty
    upload_model_folder_to_s3(folder_path, bucket_name="test-bucket", s3_prefix="models/empty_folder")

    # List objects in the bucket to verify no uploads
    result = s3_client.list_objects_v2(Bucket="test-bucket", Prefix="models/empty_folder")

    # Verify that no objects are uploaded
    assert result["KeyCount"] == 0


def count_visible_files(directory):
    for f in os.listdir(directory):
        print(os.path.abspath(f))
    return len([f for f in os.listdir(directory) if not f.startswith('.')])


@mock_aws()
def test_restore_empty_folder_from_s3(setup_local_folder_empty):
    """
    Test restoring an empty folder from S3. No files should be restored.
    """
    # Setup Moto mock S3 environment
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket="test-bucket")

    # No files in the mock S3 bucket under the specified prefix

    # Call the restore_folder_from_s3 function
    local_folder_path = setup_local_folder_empty
    restore_model_folder_from_s3(bucket_name="test-bucket", s3_prefix="models/empty_folder",
                                 local_folder_path=local_folder_path)

    # Verify that the local folder is empty, ignoring hidden files
    assert count_visible_files(local_folder_path) == 0


@mock_aws()
def test_upload_folder_to_non_existent_bucket():
    """
    Test uploading a folder to a non-existent S3 bucket.
    The function should raise an error.
    """
    # No bucket created in mock S3

    with pytest.raises(S3BucketNotFoundException):
        upload_model_folder_to_s3("/path/to/folder", bucket_name="non-existent-bucket",
                                  s3_prefix="models/folder")
