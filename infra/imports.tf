import {
  to = aws_s3_bucket.site
  id = "dean-cloud-portfolio"
}

import {
  to = aws_s3_bucket_public_access_block.site
  id = "dean-cloud-portfolio"
}

import {
  to = aws_s3_bucket_policy.site
  id = "dean-cloud-portfolio"
}

import {
  to = aws_cloudfront_origin_access_control.site
  id = "EEJ6OFX1KRCZX"
}

import {
  to = aws_cloudfront_distribution.site
  id = "E2L43LROTAGIFZ"
}
