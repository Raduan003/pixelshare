import azure.functions as func
import logging
import uuid
import json
import os
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient

# ── App ────────────────────────────────────────────────────────
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ── Config ─────────────────────────────────────────────────────
STORAGE_CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
BLOB_CONTAINER_NAME       = os.environ.get("BLOB_CONTAINER_NAME", "media-uploads")
COSMOS_ENDPOINT           = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY                = os.environ["COSMOS_KEY"]
COSMOS_DB_NAME            = os.environ.get("COSMOS_DB_NAME", "pixelshare-db")
COSMOS_CONTAINER_NAME     = os.environ.get("COSMOS_CONTAINER_NAME", "media-metadata")


def get_blob_service_client():
    return BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)


def get_cosmos_container():
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db = client.get_database_client(COSMOS_DB_NAME)
    return db.get_container_client(COSMOS_CONTAINER_NAME)


# ── 1. Upload Media ────────────────────────────────────────────
@app.route(route="UploadMedia", methods=["POST"])
def UploadMedia(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("UploadMedia triggered")
    try:
        file_data = req.files.get("file")
        title     = req.form.get("title", "").strip()
        tags_raw  = req.form.get("tags", "")

        if not file_data or not title:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'file' or 'title'"}),
                status_code=400, mimetype="application/json"
            )

        tags         = [t.strip() for t in tags_raw.split(",") if t.strip()]
        file_bytes   = file_data.read()
        content_type = file_data.content_type or "application/octet-stream"
        media_type   = "video" if content_type.startswith("video") else "image"
        media_id     = str(uuid.uuid4())
        extension    = file_data.filename.rsplit(".", 1)[-1] if "." in file_data.filename else "bin"
        blob_name    = f"{media_id}.{extension}"

        blob_client = get_blob_service_client().get_blob_client(
            container=BLOB_CONTAINER_NAME, blob=blob_name
        )
        blob_client.upload_blob(file_bytes, content_settings={"content_type": content_type})
        blob_url = blob_client.url

        document = {
            "id": media_id, "userId": "default-user",
            "title": title, "tags": tags,
            "blobUrl": blob_url, "blobName": blob_name,
            "mediaType": media_type, "contentType": content_type,
            "moderationStatus": "pending",
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
        }
        get_cosmos_container().create_item(body=document)

        return func.HttpResponse(
            json.dumps(document), status_code=201, mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logging.error(f"UploadMedia error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")


# ── 2. Get All Media ───────────────────────────────────────────
@app.route(route="GetAllMedia", methods=["GET"])
def GetAllMedia(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("GetAllMedia triggered")
    try:
        items = list(get_cosmos_container().query_items(
            query="SELECT * FROM c ORDER BY c.uploadedAt DESC",
            enable_cross_partition_query=True
        ))
        return func.HttpResponse(
            json.dumps(items), status_code=200, mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logging.error(f"GetAllMedia error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")


# ── 3. Get Media By ID ─────────────────────────────────────────
@app.route(route="GetMediaById/{id}", methods=["GET"])
def GetMediaById(req: func.HttpRequest) -> func.HttpResponse:
    media_id = req.route_params.get("id")
    logging.info(f"GetMediaById triggered: {media_id}")
    try:
        items = list(get_cosmos_container().query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": media_id}],
            enable_cross_partition_query=True
        ))
        if not items:
            return func.HttpResponse(json.dumps({"error": "Not found"}), status_code=404, mimetype="application/json")
        return func.HttpResponse(
            json.dumps(items[0]), status_code=200, mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logging.error(f"GetMediaById error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")


# ── 4. Update Media ────────────────────────────────────────────
@app.route(route="UpdateMedia/{id}", methods=["PUT"])
def UpdateMedia(req: func.HttpRequest) -> func.HttpResponse:
    media_id = req.route_params.get("id")
    logging.info(f"UpdateMedia triggered: {media_id}")
    try:
        body = req.get_json()
    except Exception:
        return func.HttpResponse(json.dumps({"error": "Invalid JSON"}), status_code=400, mimetype="application/json")
    try:
        container = get_cosmos_container()
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": media_id}],
            enable_cross_partition_query=True
        ))
        if not items:
            return func.HttpResponse(json.dumps({"error": "Not found"}), status_code=404, mimetype="application/json")
        doc = items[0]
        if "title" in body:
            doc["title"] = body["title"]
        if "tags" in body:
            tags = body["tags"]
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            doc["tags"] = tags
        if "moderationStatus" in body:
            doc["moderationStatus"] = body["moderationStatus"]
        container.upsert_item(body=doc)
        return func.HttpResponse(
            json.dumps(doc), status_code=200, mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logging.error(f"UpdateMedia error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")


# ── 5. Delete Media ────────────────────────────────────────────
@app.route(route="DeleteMedia/{id}", methods=["DELETE"])
def DeleteMedia(req: func.HttpRequest) -> func.HttpResponse:
    media_id = req.route_params.get("id")
    logging.info(f"DeleteMedia triggered: {media_id}")
    try:
        container = get_cosmos_container()
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": media_id}],
            enable_cross_partition_query=True
        ))
        if not items:
            return func.HttpResponse(json.dumps({"error": "Not found"}), status_code=404, mimetype="application/json")
        doc = items[0]
        blob_name = doc.get("blobName")
        if blob_name:
            get_blob_service_client().get_blob_client(
                container=BLOB_CONTAINER_NAME, blob=blob_name
            ).delete_blob(delete_snapshots="include")
        container.delete_item(item=doc["id"], partition_key=doc.get("userId", "default-user"))
        return func.HttpResponse(
            status_code=204,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        logging.error(f"DeleteMedia error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")
