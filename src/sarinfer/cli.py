"""Console script for sarinfer."""

import typer

from sarinfer.core.inference import start_inference_system
from sarinfer.core.s3_manager import upload_model_folder_to_s3, restore_model_folder_from_s3
from sarinfer.metadata.metadata_manager import list_models, update_model_metadata_for_s3
from sarinfer.models.model_loader import load_model

app = typer.Typer()


@app.command()
def start():
    """
    Start the Sarinfer application for inference tasks.
    This will initialize the system, load models, and prepare the environment.
    """
    typer.echo("Starting Sarinfer...")
    start_inference_system()
    typer.echo("Sarinfer is running.")


@app.command()
def load_model_cli(model_name: str):
    """
    Load a specific model into Sarinfer.
    """
    typer.echo(f"Loading model: {model_name}...")
    load_model(model_name)
    typer.echo(f"Model {model_name} loaded successfully.")


@app.command()
def list_models_cli():
    """
    List all models in the registry.
    """
    typer.echo("Listing models....")
    models = list_models()
    for model in models:
        typer.echo(f"Model: {model['name']}, Version: {model['version']}, Status: {model['status']}")


@app.command()
def backup_model_to_s3(model_name: str, model_file_path: str):
    """
    Backup a model to S3.
    """
    typer.echo(f"Backing up model {model_name} to S3...")
    upload_model_folder_to_s3(model_name, model_file_path)
    update_model_metadata_for_s3(model_name, backup_status=True)
    typer.echo(f"Model {model_name} backed up to S3.")


@app.command()
def restore_model_from_s3_cli(model_name: str, restore_path: str):
    """
    Restore a model from S3 to the local disk.
    """
    typer.echo(f"Restoring model {model_name} from S3...")
    restore_model_folder_from_s3(model_name, restore_path)
    typer.echo(f"Model {model_name} restored from S3.")


if __name__ == "__main__":
    app()
