# Verified deployment and rollback results

All runs below executed against the live public portfolio on **October 30, 2026**. Each successful deployment or rollback verified all 12 public files against the saved SHA-256 manifest after CloudFront invalidation completed.

| Step | Saved release | Result | GitHub evidence |
| --- | --- | --- | --- |
| Deploy A | `b10d36c51a7763dc606502998350e52e1a3b3dcf` | 12/12 files matched | [Run 41140822874](https://github.com/DeanAsadi/aws-cloud-portfolio/actions/runs/41140822874) |
| Deploy B | `da191d3b3affcff4ba3558d9f7f0f0f79282fc56` | 12/12 files matched | [Run 41141016170](https://github.com/DeanAsadi/aws-cloud-portfolio/actions/runs/41141016170) |
| Roll back B to A | A | Saved A entry page and all file hashes restored | [Run 41141202518](https://github.com/DeanAsadi/aws-cloud-portfolio/actions/runs/41141202518) |
| Redeploy main B | B | 12/12 files matched again | [Run 41141353474](https://github.com/DeanAsadi/aws-cloud-portfolio/actions/runs/41141353474) |

The independent observer checked the live root HTML release marker after A, B, rollback to A, and recovery to B. The downloaded workflow artifacts confirm that rollback hashes equal the original A hashes and recovery hashes equal the original B hashes. The A and B entry-page hashes differ, so this was a real content-version transition.

## Terraform and security

- Imported five existing hosting resources with **0 additions, 0 changes and 0 deletions** during adoption.
- Applied the approved automation plan: **8 added, 0 changed, 0 destroyed**. The additions were state-bucket controls and the OIDC deployment identity; the existing CloudFront, WAF association and site bucket were preserved.
- Migrated state into a separate private SSE-S3-encrypted, versioned bucket with native S3 locking. A refreshed remote-backed plan returned exit code 0 and **No changes**. The lock object was released after the plan.
- GitHub's live OIDC login succeeded. Repository variables contain identifiers, not AWS access keys. The role trust is restricted to the exact main-branch repository subject and STS audience.
- Seven IAM policy simulation checks passed: site entry/release writes and distribution invalidation allowed; object deletion, state reads, distribution updates and IAM role creation denied. The deployment identity has no access to the Terraform backend.
- Public HTTPS file checks passed. Direct unauthenticated S3 access remains denied and HTTP redirects to HTTPS.

## Release tests and safeguards

Eight tests passed locally and in GitHub CI: deterministic packaging, immutable asset references, checksum tamper detection, unsafe path/SHA rejection, failure before entry-page promotion, saved-byte rollback, immutable overwrite rejection and entry-page ordering.

The initial Linux CI validation exposed a platform checksum gap in the Terraform lock file. Fetching and verifying the provider for both `darwin_arm64` and `linux_amd64` fixed it; [run 41136351560](https://github.com/DeanAsadi/aws-cloud-portfolio/actions/runs/41136351560) subsequently passed. Integrity checking remained enabled.

## Scope

This verifies deployment, content promotion, saved-release rollback and recovery for a small static website. It does not establish an uptime SLA, load capacity, multi-region recovery or automatic rollback on failure. Terraform applies remain operator-reviewed; website deployment is automatic. GitHub branch protection and a custom domain are not claimed.

The `evidence/` folder contains sanitized downloaded run reports and summarized state/policy checks. It contains no Terraform state, credentials, payment data or personal email records. Later main-branch deployments publish updated documentation and resume files through the same tested pipeline.
