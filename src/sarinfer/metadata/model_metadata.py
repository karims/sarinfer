import uuid
from datetime import datetime

class ModelMetadata:
    # Class variable to auto-increment the version
    version_counter = 0

    def __init__(self, model_name: str, size: float, location: str, model_id=None, version=None):
        # Autogenerate model_id if not provided
        if model_id is None:
            model_id = self._generate_model_id()

        # Mandatory fields
        if not model_name or not size or not location:
            raise ValueError("model_name, size, and location are mandatory fields.")

        # Assign the auto-incremented version if not provided
        if version is None:
            version = self._get_next_version()

        self.model_id = model_id
        self.model_name = model_name
        self.version = version
        self.size = size
        self.location = location
        self.load_status = "unloaded"  # default value
        self.last_loaded = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @staticmethod
    def _generate_model_id():
        """Generates a unique model_id using UUID."""
        return str(uuid.uuid4())

    @classmethod
    def _get_next_version(cls):
        """Handles version auto-incrementation."""
        cls.version_counter += 1
        return f"v{cls.version_counter}"

    def to_dict(self):
        """Converts the object to a dictionary."""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "version": self.version,
            "size": self.size,
            "location": self.location,
            "load_status": self.load_status,
            "last_loaded": self.last_loaded,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Recreates a ModelMetadata object from a dictionary."""
        return cls(
            model_id=data.get("model_id"),
            model_name=data["model_name"],
            version=data.get("version"),
            size=data["size"],
            location=data["location"]
        )
