# Validation record

## Preparation confirmed

- Five existing AWS hosting resources imported into Terraform: 0 additions, 0 changes, 0 deletions.
- Proposed automation plan: 8 additions, 0 changes, 0 deletions to existing hosting.
- Eight local release tests passed: deterministic build, versioned asset references, tamper detection, unsafe path/SHA rejection, failed-upload promotion guard, saved-byte rollback, immutable overwrite protection and entry-page ordering.

## CI and permission checks

[GitHub validation run 41136351560](https://github.com/DeanAsadi/aws-cloud-portfolio/actions/runs/41136351560) passed Terraform formatting/initialization/validation, all eight release tests, release packaging and JavaScript syntax checks. Deployment was intentionally skipped because the AWS role is not activated.

AWS IAM policy simulation passed seven action/resource checks: site entry/release writes and this distribution’s invalidation allowed; object deletion, state reads, distribution updates and IAM role creation denied. This is policy simulation, not a live OIDC session.

## Live verification

AWS automation provisioning, GitHub OIDC deployment, live rollback and final no-change Terraform plan are pending until their recorded runs are attached here. Prepared workflows and local simulations are not evidence of a successful cloud deployment.
