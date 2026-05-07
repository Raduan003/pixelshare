# PixelShare – CW2 Azure Setup Guide
# Follow these steps IN ORDER

---

## STEP 1 – Create Resource Group

1. Go to portal.azure.com
2. Search "Resource groups" → Create
3. Name: `pixelshare-rg`
4. Region: UK South (or your nearest)
5. Click Review + Create → Create

---

## STEP 2 – Create Storage Account + Blob Container

1. Search "Storage accounts" → Create
2. Resource group: `pixelshare-rg`
3. Name: `pixelshare<yourinitials>` (must be globally unique, e.g. pixelshareri)
4. Region: Same as above | Redundancy: LRS
5. Click Review + Create → Create

### After creating:
6. Open the Storage Account → Left menu: "Containers"
7. Click "+ Container"
8. Name: `media-uploads` | Access level: **Blob (anonymous read access)**
9. Click Create

### Get your connection string:
10. Left menu → "Access keys" → Copy "Connection string" (key1)
    → Save this — you'll need it for Functions

---

## STEP 3 – Create Cosmos DB

1. Search "Azure Cosmos DB" → Create
2. Choose: **Azure Cosmos DB for NoSQL**
3. Resource group: `pixelshare-rg`
4. Account name: `pixelshare-cosmos`
5. Location: Same region | Capacity: Serverless (cheapest)
6. Review + Create → Create (takes ~5 mins)

### After creating:
7. Open Cosmos DB account → Left menu: "Data Explorer"
8. Click "New Database"
   - Database ID: `pixelshare-db`
9. Click "New Container"
   - Database: `pixelshare-db`
   - Container ID: `media-metadata`
   - Partition key: `/userId`
10. Left menu → "Keys" → Copy PRIMARY KEY and URI
    → Save both — needed for Functions

---

## STEP 4 – Create Azure SQL Database

1. Search "SQL databases" → Create
2. Resource group: `pixelshare-rg`
3. Database name: `pixelshare-sql`
4. Server → Create new:
   - Name: `pixelshare-server`
   - Auth: SQL authentication
   - Admin login: `sqladmin` | Password: (save this!)
5. Compute: Basic (cheapest)
6. Review + Create → Create

### Run the SQL schema:
7. Open the SQL database → Left menu: "Query editor"
8. Log in with your admin credentials
9. Paste and run the contents of: `docs/azure-sql-schema.sql`

---

## STEP 5 – Create Function App

1. Search "Function App" → Create
2. Resource group: `pixelshare-rg`
3. Function App name: `pixelshare-functions` (globally unique)
4. Runtime: **Python** | Version: 3.11
5. Region: Same | Hosting: Consumption (Serverless)
6. Review + Create → Create

### Deploy your functions:
Option A – VS Code (recommended):
  - Install "Azure Functions" VS Code extension
  - Open the `functions/` folder
  - Click Azure icon → Functions → Deploy to Function App
  - Select `pixelshare-functions`

Option B – Azure CLI:
  ```
  cd functions
  func azure functionapp publish pixelshare-functions
  ```

### Set Application Settings (Environment Variables):
7. Open Function App → Left menu: "Configuration" → Application settings
8. Add these settings (click "+ New application setting" for each):

   | Name                  | Value                              |
   |-----------------------|------------------------------------|
   | AzureWebJobsStorage   | (your storage connection string)   |
   | BLOB_CONTAINER_NAME   | media-uploads                      |
   | COSMOS_ENDPOINT       | (your Cosmos DB URI)               |
   | COSMOS_KEY            | (your Cosmos DB primary key)       |
   | COSMOS_DB_NAME        | pixelshare-db                      |
   | COSMOS_CONTAINER_NAME | media-metadata                     |

9. Click Save → Restart the Function App

### Enable CORS:
10. Left menu → "CORS"
11. Add: `*` (allow all origins for coursework)
12. Save

### Enable Application Insights:
13. Left menu → "Application Insights" → Turn On
14. Create new → Name: `pixelshare-insights`
15. Apply — this gives you live monitoring!

---

## STEP 6 – Create Azure Static Web App (Frontend + CI/CD)

1. First: Create a GitHub repo called `pixelshare`
2. Push your project folder to it:
   ```
   git init
   git add .
   git commit -m "Initial PixelShare commit"
   git remote add origin https://github.com/YOUR-USERNAME/pixelshare.git
   git push -u origin main
   ```

3. Search "Static Web Apps" → Create
4. Resource group: `pixelshare-rg`
5. Name: `pixelshare-web`
6. Plan: Free
7. Source: GitHub → Authorise → Select your repo + `main` branch
8. App location: `frontend` | Output: (leave blank)
9. Review + Create → Create

   This automatically creates the GitHub Actions workflow and deploys your site!

### Update the API URL in frontend:
10. Open `frontend/index.html`
11. Find: `const API_BASE = window.PIXELSHARE_API || 'https://YOUR-FUNCTION-APP...'`
12. Replace URL with your actual Function App URL
13. Commit and push → GitHub Actions auto-deploys!

---

## STEP 7 – Create Logic Apps

### Logic App 1: AI Vision Auto-Tagging
1. Search "Logic Apps" → Create
2. Resource group: `pixelshare-rg`
3. Name: `pixelshare-ai-tagging` | Type: Consumption
4. Review + Create → Create
5. Open → "Logic app designer" → "Blank Logic App"
6. Add trigger: "When a blob is added or modified (V2)"
   - Connect to your Storage Account
   - Container: `media-uploads`
   - Interval: 1 Minute
7. Add action: "HTTP" (to call Azure AI Vision)
   - Method: POST
   - URI: `https://YOUR-AI-VISION-ENDPOINT/vision/v3.2/analyze?visualFeatures=Tags`
   - Headers: `Ocp-Apim-Subscription-Key` = your AI Vision key
8. Add action: "HTTP" (call your UpdateMedia function with the tags)
9. Save

### Logic App 2: Content Moderation
1. Create another Logic App: `pixelshare-content-moderation`
2. Trigger: "When a HTTP request is received"
   - This generates a URL — copy it (this is your Logic App URI to show in video!)
3. Add action: "HTTP" → call Content Moderator API
4. Add condition: if IsImageAdultClassified = true → call UpdateMedia with rejected status
5. Save

### Create AI Vision resource (for Logic App 1):
- Search "Computer Vision" → Create → Same resource group
- After creating: copy Endpoint + Key1

---

## STEP 8 – Create Azure Front Door (Advanced Feature)

1. Search "Front Door and CDN profiles" → Create
2. Choose: "Azure Front Door" → Custom create
3. Resource group: `pixelshare-rg`
4. Name: `pixelshare-frontdoor`
5. Add an endpoint → Add a route:
   - Origin: your Static Web App
6. Review + Create

---

## STEP 9 – Verify Everything Works

Test each function URL in your browser or Postman:
- GET  https://pixelshare-functions.azurewebsites.net/api/GetAllMedia
- POST https://pixelshare-functions.azurewebsites.net/api/UploadMedia (use Postman)
- PUT  https://pixelshare-functions.azurewebsites.net/api/UpdateMedia/{id}
- DELETE https://pixelshare-functions.azurewebsites.net/api/DeleteMedia/{id}

Check Application Insights → Live Metrics — you should see requests coming in!

---

## STEP 10 – Video Checklist

Before recording, make sure you can demo all of this:
[ ] Upload an image via the frontend
[ ] View it in the gallery
[ ] Edit its title/tags
[ ] Delete it
[ ] Show Azure Portal → pixelshare-rg with all resources
[ ] Show Function App → Functions list with URLs
[ ] Show Logic Apps (both)
[ ] Show GitHub repo + Actions tab (successful deployment)
[ ] Show Application Insights live metrics
[ ] Mention Content Moderator + AI Vision as advanced features
