from google.cloud import storage

BUCKET_NAME = "menu_logger_bucket"  # Replace with your actual bucket name

def list_pdfs():
    """List all PDF files in Google Cloud Storage bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()

    pdf_files = [blob.name for blob in blobs if blob.name.endswith(".pdf")]
    print("Uploaded PDFs in GCS:", pdf_files)

list_pdfs()
