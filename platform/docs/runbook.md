# Runbook — Notes API (staging)

Operational guide for deploying, checking, and recovering the Notes API on ECS Fargate.

## Service at a glance

- App: Notes API (FastAPI + Postgres), running as a container on ECS Fargate behind an ALB
- Region: us-east-1
- ECS cluster / service: notes-staging-cluster / notes-staging-service
- Image registry: ECR repo notes-staging (tags: latest, and the git commit SHA)
- Database: RDS Postgres (notes-staging-db) in private subnets
- Config/secret: DATABASE_URL stored in SSM Parameter Store at /notes-staging/database-url, injected into the task at runtime
- Logs: CloudWatch log group /ecs/notes-staging
- Infrastructure: Terraform in platform/terraform/environments/staging (state in S3)

## Bring the environment up

This environment is created and destroyed per session to control cost.

1. From platform/terraform/environments/staging, run `terraform apply`.
2. The ECR repo is empty after a destroy, so push an image: trigger the pipeline (push to main, or re-run the latest GitHub Actions run).
3. The pipeline builds, pushes the image, and deploys it automatically.

## Tear the environment down

From the same folder, run `terraform destroy`. This removes the ALB, ECS service, RDS, and ECR repo with its images. Code, pipeline, and Terraform config are untouched.

## Deploy a change

- Normal: push to main. The pipeline runs tests and security scans, builds and pushes the image, then deploys to ECS automatically.
- Manual redeploy (re-pull the latest image):
  `aws ecs update-service --cluster notes-staging-cluster --service notes-staging-service --force-new-deployment --region us-east-1`

## Check health

- Endpoint: GET <app-url>/health should return {"status":"ok"}.
- ECS: cluster -> service -> Tasks: one task RUNNING, and the target group target healthy.
- Logs: CloudWatch log group /ecs/notes-staging. Healthy traffic shows repeated `GET /health ... 200 OK`.
- Get the URL: `terraform output app_url`.

## Roll back

Each image is tagged with its commit SHA, so a known-good version is always identifiable.

1. Find the previous good commit SHA tag in ECR.
2. Set image_tag to that SHA in variables.tf and run `terraform apply`.
3. Confirm a new task reaches RUNNING and /health is green.

## Common issues

- CannotPullContainerError: ... not found — the tag the task definition expects isn't in ECR. Usually the repo is empty after a destroy/apply; re-run the pipeline to push the image, or correct the tag in variables.tf.
- Tasks crash-loop / "Deprovisioning" — open the most recent task and read the Stopped reason plus the Logs tab. Empty logs mean the container never started (image or secret problem); a traceback in the logs means an app problem (often database connectivity).
- ResourceInitializationError: unable to pull secrets — the task execution role can't read the SSM parameter; verify its ssm:GetParameters and kms:Decrypt permissions.
- Terraform state lock / checksum mismatch — usually an apply was interrupted by a network drop. Wait and retry; if it persists, clear the stale "-md5" digest item in the DynamoDB lock table, or run `terraform state push errored.tfstate`.
- EntityAlreadyExists on apply — a resource was created but not saved to state. Delete the orphan and re-apply, or import it. Account-wide resources like the GitHub OIDC provider should be referenced with a data source, not created.