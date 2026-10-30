# Existing hosting imported without replacement. Preserve the current WAF and cache behavior.

# __generated__ by Terraform from "dean-cloud-portfolio"
resource "aws_s3_bucket_policy" "site" {
  lifecycle { prevent_destroy = true }
  bucket = "dean-cloud-portfolio"
  policy = jsonencode({
    Id = "PolicyForCloudFrontPrivateContent"
    Statement = [{
      Action = "s3:GetObject"
      Condition = {
        ArnLike = {
          "AWS:SourceArn" = "${aws_cloudfront_distribution.site.arn}"
        }
      }
      Effect = "Allow"
      Principal = {
        Service = "cloudfront.amazonaws.com"
      }
      Resource = "arn:aws:s3:::dean-cloud-portfolio/*"
      Sid      = "AllowCloudFrontServicePrincipal"
    }]
    Version = "2008-10-17"
  })
  region = "us-east-1"
}

# __generated__ by Terraform from "EEJ6OFX1KRCZX"
resource "aws_cloudfront_origin_access_control" "site" {
  lifecycle { prevent_destroy = true }
  description                       = "Created by CloudFront"
  name                              = "oac-dean-cloud-portfolio.s3.us-east-1.amazonaws.com-muxhn8zvwcx"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# __generated__ by Terraform from "dean-cloud-portfolio"
resource "aws_s3_bucket_public_access_block" "site" {
  lifecycle { prevent_destroy = true }
  block_public_acls       = true
  block_public_policy     = true
  bucket                  = "dean-cloud-portfolio"
  ignore_public_acls      = true
  region                  = "us-east-1"
  restrict_public_buckets = true
  skip_destroy            = null
}

# __generated__ by Terraform from "E2L43LROTAGIFZ"
resource "aws_cloudfront_distribution" "site" {
  lifecycle { prevent_destroy = true }
  aliases             = []
  anycast_ip_list_id  = null
  comment             = null
  default_root_object = "index.html"
  enabled             = true
  http_version        = "http2"
  is_ipv6_enabled     = true
  price_class         = "PriceClass_All"
  retain_on_delete    = false
  staging             = false
  tags = {
    Name = "dean-cloud-portfolio"
  }
  tags_all = {
    Name = "dean-cloud-portfolio"
  }
  wait_for_deployment = true
  web_acl_id          = var.existing_web_acl_arn
  default_cache_behavior {
    allowed_methods            = ["GET", "HEAD"]
    cache_policy_id            = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    default_ttl                = 0
    field_level_encryption_id  = null
    max_ttl                    = 0
    min_ttl                    = 0
    origin_request_policy_id   = null
    realtime_log_config_arn    = null
    response_headers_policy_id = null
    smooth_streaming           = false
    target_origin_id           = "dean-cloud-portfolio.s3.us-east-1.amazonaws.com-muxhddienzv"
    trusted_key_groups         = []
    trusted_signers            = []
    viewer_protocol_policy     = "redirect-to-https"
    grpc_config {
      enabled = false
    }
  }
  origin {
    connection_attempts         = 3
    connection_timeout          = 10
    domain_name                 = "dean-cloud-portfolio.s3.us-east-1.amazonaws.com"
    origin_access_control_id    = "EEJ6OFX1KRCZX"
    origin_id                   = "dean-cloud-portfolio.s3.us-east-1.amazonaws.com-muxhddienzv"
    origin_path                 = null
    response_completion_timeout = 0
  }
  restrictions {
    geo_restriction {
      locations        = []
      restriction_type = "none"
    }
  }
  viewer_certificate {
    acm_certificate_arn            = null
    cloudfront_default_certificate = true
    iam_certificate_id             = null
    minimum_protocol_version       = "TLSv1"
    ssl_support_method             = null
  }
}

# __generated__ by Terraform from "dean-cloud-portfolio"
resource "aws_s3_bucket" "site" {
  lifecycle { prevent_destroy = true }
  bucket              = "dean-cloud-portfolio"
  bucket_namespace    = "global"
  force_destroy       = false
  object_lock_enabled = false
  region              = "us-east-1"
  tags                = {}
  tags_all            = {}
}
