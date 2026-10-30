# Deployment and rollback runbook

## Repository configuration

Set repository Actions variables (not long-lived AWS keys):

| Variable | Purpose |
| --- | --- |
| `AWS_ROLE_ARN` | The Terraform-created deployment role |
| `SITE_BUCKET` | Existing static website bucket |
| `DISTRIBUTION_ID` | Existing CloudFront distribution |
| `SITE_URL` | Public HTTPS URL with trailing slash |

The IAM trust policy permits only this repository's exact **main branch** subject and the STS audience. Workflow dispatch on another branch cannot assume the role. Actions are pinned to full commit SHAs. A concurrency group shared by deployment and rollback prevents overlapping promotions; in-progress operations are not cancelled.

## Publish

1. Make source changes and open a pull request.
2. Review the code and require the validation job to pass before merging. This runbook does not imply that a GitHub branch protection rule has been configured.
3. A push to main validates, builds and uploads the immutable release, promotes the entry page, invalidates root paths and checks every file over public HTTPS against its SHA-256 digest.
4. Inspect the job summary and `deployment-proof-<run-id>` artifact. Confirm the expected release SHA appears in the root HTML `portfolio-release` meta tag.

A failed asset upload must not promote the entry page. A failure after entry promotion requires checking the live release marker and running the rollback workflow if needed; automatic rollback is intentionally not assumed.

## Roll back

Run **Roll back portfolio** on main with a previously verified full 40-character commit SHA. The workflow downloads the saved manifest and all saved files, verifies their identity/hashes, promotes that saved entry page, invalidates CloudFront root paths and compares the public responses with the saved manifest. The original release assets must still exist.

```bash
gh workflow run rollback.yml --repo DeanAsadi/aws-cloud-portfolio \
  --ref main -f release_sha=PREVIOUS_FULL_COMMIT_SHA
```

Inputs enter the shell through an environment variable and must match a strict SHA pattern. The rollback target is an existing release, not an arbitrary branch or URL.

To recover from a rollback, deploy main again using **Portfolio CI and deployment**. Saved releases remain available; nothing is deleted by either workflow.

## Verify and diagnose

- Check workflow job steps and the deployment JSON artifact.
- The public HTML release marker identifies the entry page. Static assets point to `/releases/<sha>/` so previous browser caches cannot mix two revisions.
- Public files should return 200, HTTP should redirect to HTTPS, and unauthenticated direct S3 access should return 403.
- `AccessDenied` during OIDC login: compare the repository's actual subject/audience with Terraform inputs. Never print the OIDC token or STS credentials.
- Immutable-file conflict: investigate why the same commit produced different bytes; do not grant delete permission to bypass it.
- Do not invalidate every immutable asset routinely. Normal release/rollback invalidations cover `/` and `/index.html` only.
