# PixelShare 📷
**Scalable Serverless Multimedia Sharing Platform**
COM682 Cloud Native Development – Coursework 2
Student: Raduan Islam | B00974562

---

## Project Structure

```
pixelshare/
├── frontend/
│   └── index.html              ← Static Web App (HTML/JS frontend)
├── functions/
│   ├── host.json               ← Function App config
│   ├── requirements.txt        ← Python dependencies
│   ├── local.settings.json     ← Local dev env vars (DO NOT COMMIT)
│   ├── shared/
│   │   └── config.py           ← Shared Azure clients
│   ├── UploadMedia/
│   │   └── __init__.py         ← POST  /api/UploadMedia
│   ├── GetAllMedia/
│   │   └── __init__.py         ← GET   /api/GetAllMedia
│   ├── GetMediaById/
│   │   └── __init__.py         ← GET   /api/GetMediaById/{id}
│   ├── UpdateMedia/
│   │   └── __init__.py         ← PUT   /api/UpdateMedia/{id}
│   └── DeleteMedia/
│       └── __init__.py         ← DELETE /api/DeleteMedia/{id}
├── logicapps/
│   ├── ai-tagging-logicapp.json          ← Logic App: AI Vision auto-tagging
│   └── content-moderation-logicapp.json  ← Logic App: Content Moderator
├── docs/
│   ├── AZURE-SETUP-GUIDE.md    ← Step-by-step Azure setup
│   └── azure-sql-schema.sql    ← Azure SQL Users table
└── .github/
    └── workflows/
        └── deploy.yml          ← CI/CD: GitHub Actions → Static Web App
```

## Azure Resources Used

| Resource | Name | Purpose |
|---|---|---|
| Resource Group | pixelshare-rg | Contains all resources |
| Storage Account | pixelshare[initials] | Blob storage for media files |
| Cosmos DB | pixelshare-cosmos | NoSQL metadata storage |
| Azure SQL | pixelshare-sql | Relational user data |
| Function App | pixelshare-functions | REST API (5 CRUD endpoints) |
| Static Web App | pixelshare-web | Frontend hosting + CI/CD |
| Logic App | pixelshare-ai-tagging | AI Vision auto-tagging |
| Logic App | pixelshare-content-moderation | Content moderation |
| Computer Vision | pixelshare-vision | Azure AI Vision service |
| Application Insights | pixelshare-insights | Monitoring + telemetry |
| Front Door | pixelshare-frontdoor | CDN + global routing |

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/UploadMedia | Upload media file + metadata |
| GET | /api/GetAllMedia | Get all media items |
| GET | /api/GetMediaById/{id} | Get single media item |
| PUT | /api/UpdateMedia/{id} | Update title/tags |
| DELETE | /api/DeleteMedia/{id} | Delete media + blob |

## Setup
See `docs/AZURE-SETUP-GUIDE.md` for full step-by-step instructions.
