variable "existing_web_acl_arn" {
  description = "Existing CloudFront WAF association; preserved, not managed here."
  type        = string
}
variable "state_bucket_name" {
  description = "Dedicated private Terraform state bucket."
  type        = string
}
variable "github_subject" {
  description = "Exact GitHub OIDC subject observed for the main branch."
  type        = string
}
data "aws_caller_identity" "current" {}
