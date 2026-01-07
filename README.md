# GCP Cloud Build POC: AWS to GCP Migration
**Project ID:** `project-045a9bc2-2b2f-428e-9c0`  
**Goal:** Replace AWS CodeBuild/ECR/S3 pipeline with GCP Cloud Build, Artifact Registry, and Cloud Run.

---

## 1. Architecture Mapping (AWS → GCP)
| AWS Component    | GCP Replacement         | Purpose                        |
| :---             | :---                    | :---                           |
| **CodeBuild**    | **Cloud Build**         | Serverless CI/CD Pipeline      |
| **Amazon ECR**   | **Artifact Registry**   | Container Image Management     |
| **Amazon S3**    | **Cloud Storage (GCS)** | Artifact & Config Storage      |
| **ECS**          | **Cloud Run**           | Serverless Container Execution |

---

## 2. Prerequisites & Setup
Run these commands in the Google Cloud Shell to initialize the environment.

### A. Enable APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com

# GCP Cloud Build POC: AWS to GCP Migration
**Project ID:** `project-045a9bc2-2b2f-428e-9c0`  
**Goal:** Replace AWS CodeBuild/ECR/S3 pipeline with GCP Cloud Build, Artifact Registry, and Cloud Run.

---

## 1. Architecture Mapping (AWS → GCP)
| AWS Component | GCP Replacement | Purpose |
| :--- | :--- | :--- |
| **CodeBuild** | **Cloud Build** | Serverless CI/CD Pipeline |
| **Amazon ECR** | **Artifact Registry** | Container Image Management |
| **Amazon S3** | **Cloud Storage (GCS)** | Artifact & Config Storage |
| **ECS / App Runner**| **Cloud Run** | Serverless Container Execution |

---

## 2. Prerequisites & Setup
Run these commands in the Google Cloud Shell to initialize the environment.

### A. Enable APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com

B. Create Artifact Registry
Bash
gcloud artifacts repositories create demo-repo \
  --repository-format=docker \
  --location=us-east1 \
  --description="POC Docker repo for dev/staging/prod"

C. Create Artifact Bucket
Bash
gsutil mb gs://demo-build-artifacts'

3. IAM & PermissionsThe Cloud Build Service Account requires permissions to push images, upload artifacts, and deploy to Cloud Run.
Service Account: 461170443612@cloudbuild.gserviceaccount.com

Bash
# Grant Artifact Registry Access
gcloud projects add-iam-policy-binding project-045a9bc2-2b2f-428e-9c0 \
  --member=serviceAccount:461170443612@cloudbuild.gserviceaccount.com \
  --role=roles/artifactregistry.writer

# Grant Storage Access for Artifacts
gcloud projects add-iam-policy-binding project-045a9bc2-2b2f-428e-9c0 \
  --member=serviceAccount:461170443612@cloudbuild.gserviceaccount.com \
  --role=roles/storage.objectAdmin

# Grant Cloud Run Admin & Service Account User (Required for Deployment)
gcloud projects add-iam-policy-binding project-045a9bc2-2b2f-428e-9c0 \
  --member=serviceAccount:461170443612@cloudbuild.gserviceaccount.com \
  --role=roles/run.admin

gcloud iam service-accounts add-iam-policy-binding \
  461170443612-compute@developer.gserviceaccount.com \
  --member=serviceAccount:461170443612@cloudbuild.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

4. Pipeline StructureThe repository follows a multi-environment strategy using dedicated YAML files.

QA-app/
├── Dockerfile           # App Containerization
├── app.py               # Demo Python Application
├── requirements.txt     # Dependencies
├── cloudbuild-dev.yaml  # Development Pipeline
├── cloudbuild-staging.yaml
└── cloudbuild-prod.yaml

**Environment Details
Environment     Service Name  Image Name        URL Path
Dev           qa-be-dev         qa-be            /
Staging       qa-be-staging     qa-be-staging    /
Prod          qa-be-prod        qa-be-prod       /**

5. Deployment Guide
Manual Deployment (from Cloud Shell)

For automatic trigger, update deployment step(step-3) with 'update-env-vars' flag:
e.g.
# Step 3: Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    id: 'Deploy'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image'
      - '${_REPOSITORY_URI}:${_IMAGE_TAG}'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
**      - '--update-env-vars'
      - 'ENV=dev,IMAGE_TAG=${_IMAGE_TAG}'**

Navigate to the app directory:
Bash
cd ~/CloudBuild-GCS-QA-POC/QA-app

Run the specific environment build:

Bash
# DEV (manual testing/CLI)
gcloud builds submit --config cloudbuild-dev.yaml --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .

Automatic trigger- gcloud builds submit --config cloudbuild-dev.yaml .

# STAGING (manual testing/CLI)
gcloud builds submit --config cloudbuild-staging.yaml --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .

Automatic trigger- gcloud builds submit --config cloudbuild-staging.yaml .

# PROD
gcloud builds submit --config cloudbuild-prod.yaml --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .

Automatic trigger- gcloud builds submit --config cloudbuild-prod.yaml .

Note: When using automated GitHub Triggers, the $SHORT_SHA is injected automatically by GCP.

6. Dynamic Versioning (The $SHORT_SHA)
Each build injects the Git Commit Hash into the Cloud Run environment.

How it works:
Cloud Build captures $SHORT_SHA from the commit.
The cloudbuild.yaml uses --update-env-vars IMAGE_TAG=${_IMAGE_TAG}.
The app retrieves this via os.getenv("IMAGE_TAG").

7. VerificationImages:
gcloud artifacts docker images list us-east1-docker.pkg.dev/project-045a9bc2-2b2f-428e-9c0/demo-repo

Artifacts: gsutil ls gs://demo-build-artifactsCloud

Run: Check the Revisions tab in the console to see the updated IMAGE_TAG environment variable.
