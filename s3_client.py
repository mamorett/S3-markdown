import os
import boto3
import streamlit as st
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env if present (for local dev)
load_dotenv()

def get_config(key, default=None):
    """
    Retrieves configuration from environment variables or Streamlit secrets.
    Priority: env vars > st.secrets > default
    """
    # Check environment variables first (populated by .env)
    val = os.getenv(key)
    if val is not None:
        return val

    # Fallback to Streamlit secrets
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        pass

    return default

@st.cache_resource
def get_s3_client():
    """Returns a cached boto3 S3 client configured from environment variables or secrets."""
    endpoint_url = get_config("S3_ENDPOINT_URL")
    access_key = get_config("S3_ACCESS_KEY_ID")
    secret_key = get_config("S3_SECRET_ACCESS_KEY")
    region_name = get_config("S3_REGION_NAME", "us-east-1")

    if not all([access_key, secret_key]):
        raise EnvironmentError("S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY must be set.")

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url if endpoint_url else None,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
    )

@st.cache_data(ttl=60)
def list_markdown_files(_client, bucket_name: str) -> list[str]:
    """
    Returns a sorted list of S3 object keys (strings) for all .md files
    found in the given bucket. Handles pagination automatically.
    """
    if not bucket_name:
        return []

    keys = []
    try:
        paginator = _client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name):
            if "Contents" in page:
                for obj in page["Contents"]:
                    if obj["Key"].lower().endswith(".md"):
                        keys.append(obj["Key"])
    except ClientError as e:
        st.error(f"Error listing files in bucket '{bucket_name}': {e}")
        return []
    
    return sorted(keys)

def fetch_file_content(_client, bucket_name: str, key: str) -> str:
    """
    Downloads and returns the UTF-8 decoded text content of the S3 object
    identified by the given key.
    """
    try:
        response = _client.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read().decode("utf-8")
    except ClientError as e:
        st.error(f"Error fetching file '{key}': {e}")
        return ""
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ""
