# Terraform adoption and state

The five existing hosting resources were imported with **zero infrastructure additions, changes or deletions**. The import blocks are retained as documentation of adoption. `hosting.tf` was generated from actual provider reads and reviewed; `prevent_destroy` guards the imported resources. Account-specific inputs are ignored local files, not secrets embedded in committed configuration.

## Current environment

The approved bootstrap and state migration are complete. Copy `backend.hcl.example` to ignored `backend.hcl`, set the actual existing private state bucket and initialize with `terraform init -backend-config=backend.hcl`. Supply the ignored operator variable values separately. Run a refreshed plan before proposing any change.

## Initial adoption sequence

Use a local operator session that is authorized to manage the named hosting and IAM resources. Do not export credentials into files or paste them into the repository.

The following sequence records the one-time adoption process. For a fresh bootstrap, the backend declaration must be temporarily omitted until its bucket exists. Do not rerun bootstrap against the live environment.

1. Review `terraform.tfvars.example` and create ignored `deployment.auto.tfvars` with the existing WAF ARN, a unique state bucket, and the exact GitHub main-branch OIDC subject. New GitHub repositories can use immutable owner/repository IDs in the subject; do not assume the legacy format.
2. Initialize without a remote backend during first adoption. For an existing environment, review the import plan before applying it.
3. Review the automation plan. It adds the private encrypted/versioned state bucket and its access controls, the OIDC provider and the deployment role/policy. It must not replace or change the existing hosting resources.
4. Apply only the reviewed saved plan with the user's cost/security authorization.
5. Add `backend "s3" {}` in the Terraform block, configure ignored `backend.hcl` using the example, and run `terraform init -migrate-state -backend-config=backend.hcl`. Approve state copying only after confirming the destination is private and encrypted.
6. Confirm state and its `.tflock` path work, then run a normal refreshed plan. The final verification should report no changes.

The backend uses S3 native locking (`use_lockfile = true`), SSE-S3 encryption and bucket versioning. No DynamoDB table or paid KMS key is created. Backend versions are not automatically deleted.

## Operator changes

```bash
terraform init -backend-config=backend.hcl
terraform fmt -check
terraform validate
terraform plan -out=reviewed.tfplan
# Review all changes. Apply only the reviewed plan.
terraform apply reviewed.tfplan
```

GitHub CI validates configuration but **does not apply Terraform**. Infrastructure changes remain an operator-reviewed step. The website deployment role has neither state access nor infrastructure modification permissions.

Never publish `.terraform/`, `*.tfstate*`, `*.tfplan`, local `*.auto.tfvars` or `backend.hcl`. State contains security configuration and account metadata even when it contains no passwords. Keep operator backups outside public source control.

Reference: [HashiCorp S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3), [GitHub AWS OIDC](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
