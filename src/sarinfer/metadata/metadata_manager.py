from datetime import datetime

from pymongo.errors import DuplicateKeyError

from sarinfer.config.mongo_config import MongoDBConfig
from sarinfer.metadata.model_metadata import ModelMetadata


class ModelMetadataManager:
    def __init__(self):
        self.db_config = MongoDBConfig()  # Connect using project-level configuration
        self.collection = self.db_config.get_collection("model_metadata")

        # Ensure model_id is unique
        self.collection.create_index("model_id", unique=True)

    def add_model(self, model_metadata: ModelMetadata):
        """Adds new model metadata to MongoDB."""
        try:
            self.collection.insert_one(model_metadata.to_dict())
        except DuplicateKeyError:
            print(f"Model with ID {model_metadata.model_id} already exists.")
            return None
        return model_metadata.model_id

    def get_model_metadata(self, model_id: str):
        """Retrieves metadata for a specific model."""
        data = self.collection.find_one({"model_id": model_id})
        if data:
            return ModelMetadata.from_dict(data)
        return None

    def update_model_metadata(self, model_id: str, updates: dict):
        """Updates model metadata with new values."""
        updates['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {"model_id": model_id},
            {"$set": updates}
        )
        return result.modified_count

    def delete_model_metadata(self, model_id: str):
        """Deletes a model's metadata."""
        result = self.collection.delete_one({"model_id": model_id})
        return result.deleted_count

    def list_all_models(self):
        """Returns a list of all model metadata."""
        data = self.collection.find()
        return [ModelMetadata.from_dict(item) for item in data]


# # src/sarinfer/metadata/metadata_manager.py
#
# import json
# import os
# from datetime import datetime
#
# # File path for the model metadata registry (can be changed)
# METADATA_FILE_PATH = os.path.dirname(__file__) + "/model_registry.json"
#
#
#
# def load_metadata():
#     """
#     Load the metadata from the JSON file.
#     If the file doesn't exist, it creates an empty structure.
#     """
#     if not os.path.exists(METADATA_FILE_PATH):
#         return {"models": []}
#
#     with open(METADATA_FILE_PATH, 'r') as f:
#         return json.load(f)
#
#
# def save_metadata(metadata):
#     """
#     Save the metadata to the JSON file.
#     """
#     with open(METADATA_FILE_PATH, 'w') as f:
#         json.dump(metadata, f, indent=4)
#
#
# def get_model_metadata(model_name: str):
#     """
#     Retrieve metadata for a specific model by name.
#     """
#     metadata = load_metadata()
#     for model in metadata['models']:
#         if model['name'] == model_name:
#             return model
#     return None
#
#
# def update_model_metadata(model_name: str, model_metadata: dict):
#     """
#     Update the metadata for a specific model.
#     If the model doesn't exist, it adds it.
#     """
#     metadata = load_metadata()
#     for model in metadata['models']:
#         if model['name'] == model_name:
#             model.update(model_metadata)
#             break
#     else:
#         metadata['models'].append(model_metadata)
#
#     save_metadata(metadata)
#
#
# def list_models():
#     """
#     List all available models in the registry.
#     """
#     metadata = load_metadata()
#     return metadata['models']
#
#
# def sync_s3_metadata():
#     """
#     Synchronize metadata between local registry and S3.
#     This is a placeholder function for future implementation with actual S3 sync logic.
#     """
#     # Placeholder for future S3 sync implementation
#     print("Syncing metadata with S3 (to be implemented)...")
#
# def update_model_metadata_for_s3(model_name: str, backup_status: bool):
#     """
#     Update the model metadata to reflect its backup status in S3.
#     """
#     metadata = load_metadata()
#     for model in metadata["models"]:
#         if model["name"] == model_name:
#             model["s3_backup"] = backup_status
#             save_metadata(metadata)
#             return
#     print(f"Model {model_name} not found in metadata.")
