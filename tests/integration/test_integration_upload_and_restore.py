import boto3
import os
import tempfile
import shutil
import pytest
from sarinfer.core.s3_manager import upload_model_folder_to_s3, restore_model_folder_from_s3, s3_client


def empty_bucket(s3_client, bucket_name):
    # List and delete all objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)

    if 'Contents' in response:
        objects = [{'Key': obj['Key']} for obj in response['Contents']]
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})


def empty_bucket_versions(s3_client, bucket_name):
    # If versioning is enabled, list and delete all versions of objects in the bucket
    response = s3_client.list_object_versions(Bucket=bucket_name)

    if 'Versions' in response:
        versions = [{'Key': v['Key'], 'VersionId': v['VersionId']} for v in response['Versions']]
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': versions})

    if 'DeleteMarkers' in response:
        delete_markers = [{'Key': d['Key'], 'VersionId': d['VersionId']} for d in response['DeleteMarkers']]
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_markers})


def delete_s3_bucket(s3_client, bucket_name):
    # Empty the bucket (objects and versions)
    empty_bucket(s3_client, bucket_name)
    empty_bucket_versions(s3_client, bucket_name)

    # Now delete the bucket
    s3_client.delete_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' deleted successfully.")

@pytest.fixture
def setup_real_s3_bucket():
    """
    Create a real S3 bucket for integration testing.
    """
    bucket_name = "integration-test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name
    # Clean up: delete all objects and the bucket after the test
    delete_s3_bucket(s3_client, bucket_name)


@pytest.fixture
def setup_local_folder():
    """
    Setup a temporary local folder for testing.
    Create some test files in it to simulate folder content.
    """
    temp_dir = tempfile.mkdtemp()
    subfolder_path = os.path.join(temp_dir, "subfolder")
    os.makedirs(subfolder_path)

    # Create dummy files
    with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
        f.write("File 1 content")

    with open(os.path.join(subfolder_path, "file2.txt"), "w") as f:
        f.write("File 2 content")

    yield temp_dir
    shutil.rmtree(temp_dir)  # Clean up after the test


@pytest.mark.integration
def test_integration_upload_and_restore(setup_real_s3_bucket, setup_local_folder):
    """
    Integration test for uploading and restoring folders from S3.
    """
    bucket_name = setup_real_s3_bucket
    folder_path = setup_local_folder
    s3_prefix = "models/test_model"

    # Upload folder to real S3
    upload_model_folder_to_s3(folder_path, bucket_name=bucket_name, s3_prefix=s3_prefix)

    # Create a new local folder for restoration
    restore_folder = tempfile.mkdtemp()

    # Restore folder from real S3
    restore_model_folder_from_s3(bucket_name=bucket_name, s3_prefix=s3_prefix, local_folder_path=restore_folder)

    # Verify that files are restored correctly
    assert os.path.exists(os.path.join(restore_folder, "file1.txt"))
    assert os.path.exists(os.path.join(restore_folder, "subfolder/file2.txt"))

    with open(os.path.join(restore_folder, "file1.txt"), "r") as f:
        assert f.read() == "File 1 content"

    with open(os.path.join(restore_folder, "subfolder/file2.txt"), "r") as f:
        assert f.read() == "File 2 content"

    # Clean up restored folder
    shutil.rmtree(restore_folder)
