import os
import pytest
from unittest.mock import patch, MagicMock
from src.sarinfer.config.mongo_config import MongoDBConfig

# Test MongoDBConfig initialization with authentication
@patch('src.sarinfer.config.mongo_config.MongoClient')
def test_mongo_db_config_initialization(mock_mongo_client):
    """Test the MongoDBConfig initialization with authentication support."""

    # Create a mock MongoClient instance and set up mock database access
    mock_db = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db

    # Mock environment variables
    with patch.dict(os.environ, {
        'MONGO_USER': 'testuser',
        'MONGO_PASSWORD': 'testpass',
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': '27017',
        'MONGO_DB_NAME': 'sarinfer_db',
        'MONGO_AUTH_DB': 'admin'
    }):
        # Initialize MongoDBConfig
        mongo_config = MongoDBConfig()

        # Ensure MongoClient is called with correct URI
        expected_uri = "mongodb://testuser:testpass@localhost:27017/admin?authSource=admin"
        mock_mongo_client.assert_called_once_with(expected_uri)

        # Verify the database name is set correctly
        assert mongo_config.db_name == 'sarinfer_db'

        # Ensure MongoClient accesses the correct database
        mock_mongo_client.return_value.__getitem__.assert_called_once_with('sarinfer_db')

# Test MongoDBConfig initialization without authentication
@patch('src.sarinfer.config.mongo_config.MongoClient')
def test_mongo_db_config_no_auth(mock_mongo_client):
    """Test the MongoDBConfig initialization without authentication."""

    # Create a mock MongoClient instance and set up mock database access
    mock_db = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db

    # Mock environment variables without user and password
    with patch.dict(os.environ, {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': '27017',
        'MONGO_DB_NAME': 'sarinfer_db'
    }):
        # Initialize MongoDBConfig
        mongo_config = MongoDBConfig()

        # Ensure MongoClient is called with correct URI (no auth)
        expected_uri = "mongodb://localhost:27017/"
        mock_mongo_client.assert_called_once_with(expected_uri)

        # Ensure MongoClient accesses the correct database
        mock_mongo_client.return_value.__getitem__.assert_called_once_with('sarinfer_db')

# Test get_collection method of MongoDBConfig
@patch('src.sarinfer.config.mongo_config.MongoClient')
def test_get_collection(mock_mongo_client):
    """Test the get_collection method of MongoDBConfig."""

    # Create a mock MongoClient instance and set up mock database and collection access
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_mongo_client.return_value.__getitem__.return_value = mock_db

    # Mock environment variables
    with patch.dict(os.environ, {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': '27017',
        'MONGO_DB_NAME': 'sarinfer_db'
    }):
        # Initialize MongoDBConfig
        mongo_config = MongoDBConfig()

        # Call get_collection method
        collection = mongo_config.get_collection("test_collection")

        # Ensure the correct collection is accessed
        mock_db.__getitem__.assert_called_once_with("test_collection")
        assert collection == mock_db.__getitem__.return_value
