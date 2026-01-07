AWS CodeBuild → GCP Cloud Build
POC (Dev / Staging / Prod)

1️. DEPENDENT SERVICES
Enable once per project.
Project
project-045a9bc2-2b2f-428e-9c0

Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com

These replace:
AWS CodeBuild


Amazon ECR


Amazon S3 (artifacts)


2️. REQUIRED GCP RESOURCES
A. Artifact Registry (Docker)
Replacement for Amazon ECR
Single repository used for all environments.
 Environment separation is done via image names, same as AWS.
gcloud artifacts repositories create demo-repo \
  --repository-format=docker \
  --location=us-east1 \
  --description="POC Docker repo for dev/staging/prod"

Important
Region: us-east1


Docker hostname must match:


us-east1-docker.pkg.dev

B. GCS Bucket (Artifacts Replacement for CodeBuild)
Replacement for CodeBuild → S3 artifacts
gsutil mb gs://demo-build-artifacts

Used to store:
imagedefinitions.json


C. Cloud Build Service Account Permissions
Cloud Build executes using the service account:
461170443612@cloudbuild.gserviceaccount.com

(461170443612 = project number of project-045a9bc2-2b2f-428e-9c0)
Grant minimum required roles:
gcloud projects add-iam-policy-binding project-045a9bc2-2b2f-428e-9c0 \
  --member=serviceAccount:461170443612@cloudbuild.gserviceaccount.com \
  --role=roles/artifactregistry.writer

gcloud projects add-iam-policy-binding project-045a9bc2-2b2f-428e-9c0 \
  --member=serviceAccount:461170443612@cloudbuild.gserviceaccount.com \
  --role=roles/storage.objectAdmin

3️. PLACEHOLDERS
Item
Value Used
Project ID
project-045a9bc2-2b2f-428e-9c0
Artifact Registry Repo
demo-repo
Artifact Registry Region
us-east1
GCS Bucket
demo-build-artifacts

Final Docker repo format
us-east1-docker.pkg.dev/project-045a9bc2-2b2f-428e-9c0/demo-repo/<IMAGE_NAME>

4️. ENVIRONMENT-SPECIFIC IMAGE NAMES
This mirrors your AWS ECR setup exactly.
Environment
Image Name
Dev
qa-be
Staging
qa-be-staging
Prod
qa-be-prod


Tags applied:
latest
<SHORT_SHA>


5️. SOURCE REPOSITORY STRUCTURE
GitHub Repo:
https://github.com/Dhiraj-Shivade/CloudBuild-GCS-QA-POC.git

Directory used by Cloud Build:
QA-app/
├── Dockerfile
├── app.py
├── requirements.txt
├── cloudbuild-dev.yaml
├── cloudbuild-staging.yaml
└── cloudbuild-prod.yaml

Dockerfile was verified locally:
docker build -t qa-be-test .

6️. HOW EACH CLOUD BUILD FILE WORKS (AWS → GCP MAPPING)
🔹 PRE-BUILD (Implicit in Cloud Build)
AWS CodeBuild
GCP Cloud Build
$CODEBUILD_RESOLVED_SOURCE_VERSION
$SHORT_SHA
ECR login
Automatic via IAM
Shell env vars
YAML substitutions + built-ins

Cloud Build automatically:
Injects $SHORT_SHA


Authenticates Docker to Artifact Registry



🔹 BUILD PHASE
For each environment:
Builds Docker image for:

 linux/amd64


Uses Dockerfile in QA-app/


Tags image twice:

 :<SHORT_SHA>
:latest


Equivalent AWS behavior:
docker build --no-cache
docker tag <commit>
docker tag latest


🔹 POST-BUILD PHASE
Pushes both tags to Artifact Registry


Generates ECS-compatible artifact file:


[
  {
    "name": "<env-service-name>",
    "imageUri": "<artifact-registry-image>:<SHORT_SHA>"
  }
]

This exactly matches AWS imagedefinitions.json.


🔹 ARTIFACTS
Uploads imagedefinitions.json to:


gs://demo-build-artifacts

Acts as:
Direct replacement for CodeBuild → S3 artifacts

7️. RUNNING THE POC (MANUAL TRIGGERS)
All builds are run from Cloud Shell. For automatic triggers from github remove --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .
DEV
cd ~/CloudBuild-GCS-QA-POC/QA-app

gcloud builds submit --config cloudbuild-dev.yaml --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .


STAGING
gcloud builds submit --config cloudbuild-staging.yaml --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .

PROD
gcloud builds submit --config cloudbuild-prod.yaml --substitutions=_IMAGE_TAG=$(git rev-parse --short HEAD) .


8️. POC VERIFICATION CHECKLIST
Artifact Registry
gcloud artifacts docker images list \
  us-east1-docker.pkg.dev/project-045a9bc2-2b2f-428e-9c0/demo-repo

Expected images:
qa-be
qa-be-staging
qa-be-prod

Each image has:
latest
<short-sha>


GCS Artifacts
gsutil ls gs://demo-build-artifacts

Expected:
imagedefinitions.json


✔ Image Pull Validation
docker pull \
us-east1-docker.pkg.dev/project-045a9bc2-2b2f-428e-9c0/demo-repo/qa-be-prod:latest

Confirms:
Image pushed correctly
Artifact Registry access works



