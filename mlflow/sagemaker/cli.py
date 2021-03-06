from __future__ import print_function

import os

import click

import mlflow
import mlflow.sagemaker
from mlflow.sagemaker import DEFAULT_IMAGE_NAME as IMAGE
from mlflow.utils import cli_args


@click.group("sagemaker")
def commands():
    """Serve models on SageMaker."""
    pass


@commands.command("deploy")
@click.option("--app-name", "-a", help="Application name.", required=True)
@cli_args.MODEL_PATH
@click.option("--execution-role-arn", "-e", default=None, help="SageMaker execution role")
@click.option("--bucket", "-b", default=None, help="S3 bucket to store model artifacts")
@cli_args.RUN_ID
@click.option("--image-url", "-i", default=None, help="ECR URL for the Docker image")
@click.option("--region-name", "-r", default="us-west-2", help="region name")
def deploy(app_name, model_path, execution_role_arn, bucket, run_id, image_url, region_name):
    """
    Deploy model on Sagemaker as a REST API endpoint. Current active AWS account needs to have correct permissions setup.
    """
    mlflow.sagemaker.deploy(app_name=app_name, model_path=model_path,
                            execution_role_arn=execution_role_arn, bucket=bucket, run_id=run_id,
                            image_url=image_url, region_name=region_name)


@commands.command("run-local")
@cli_args.MODEL_PATH
@cli_args.RUN_ID
@click.option("--port", "-p", default=5000, help="Server port. [default: 5000]")
@click.option("--image", "-i", default=IMAGE, help="Docker image name")
def run_local(model_path, run_id, port, image):
    """
    Serve model locally running in a Sagemaker-compatible Docker container.
    """
    mlflow.sagemaker.run_local(model_path=model_path, run_id=run_id, port=port, image=image)


@commands.command("build-and-push-container")
@click.option("--build/--no-build", default=True, help="Build the container if set.")
@click.option("--push/--no-push", default=True, help="Push the container to amazon ecr if set.")
@click.option("--container", "-c", default=IMAGE, help="image name")
@cli_args.MLFLOW_HOME
def build_and_push_container(build, push, container, mlflow_home):
    """
    Build new MLflow Sagemaker image, assign it given name and push to ECR.

    This function builds an MLflow Docker image.
    The image is built locally and it requires Docker to run.
    The image is pushed to ECR under current active AWS account and to current active aws region.
    """
    if not (build or push):
        print("skipping both build nad push, have nothing to do!")
    if build:
        mlflow.sagemaker.build_image(container,
                                     mlflow_home=os.path.abspath(mlflow_home) if mlflow_home
                                     else None)
    if push:
        mlflow.sagemaker.push_image_to_ecr(container)
