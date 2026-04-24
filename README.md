# S3 Markdown Viewer

A Streamlit-based web application to view and render Markdown files stored in any S3-compatible object storage (AWS S3, OCI Object Storage, MinIO, etc.).

## Features

- **S3-Compatible:** Works with any S3 API endpoint.
- **Markdown Rendering:** Beautifully renders Markdown with GitHub-Flavored Markdown support.
- **Folder Tree View:** Navigate through your S3 bucket's folder structure.
- **Search/Filter:** Quickly find files by name.
- **Raw Source Toggle:** Switch between rendered Markdown and raw code view.
- **Caching:** Efficiently caches file lists and client connections.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory (use `.env.example` as a template):

```dotenv
S3_ENDPOINT_URL=https://<namespace>.compat.objectstorage.<region>.oraclecloud.com
S3_ACCESS_KEY_ID=your-access-key-id
S3_SECRET_ACCESS_KEY=your-secret-access-key
S3_BUCKET_NAME=your-bucket-name
S3_REGION_NAME=us-east-1
```

### 3. Run the App

```bash
streamlit run app.py
```

## Security

- Credentials should **never** be hardcoded.
- Use the `.env` file for local development and Streamlit Secrets for cloud deployment.
- Ensure your S3 credentials have read-only access to the target bucket.
