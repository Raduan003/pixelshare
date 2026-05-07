# PixelShare 📷
**Scalable Serverless Multimedia Sharing Platform**
COM682 Cloud Native Development – Coursework 2
Student: Raduan Islam | B00974562

---

## Project Structure

```
pixelshare/
├── index.html                  ← Frontend (GitHub Pages)
├── frontend/
│   └── index.html              ← Frontend copy
├── functions/
│   ├── function_app.py         ← All 5 CRUD Azure Functions
│   ├── host.json               ← Function App config
│   └── requirements.txt        ← Python dependencies
├── logicapps/
│   ├── ai-tagging-logicapp.json
│   └── content-moderation-logicapp.json
└── .github/
    └── workflows/
        └── deploy.yml          ← CI/CD GitHub Actions
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


