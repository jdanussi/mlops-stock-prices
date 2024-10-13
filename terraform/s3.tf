resource "aws_s3_bucket" "s3b-mlops-mlflow" {
  bucket = var.bucket
  tags = {
    Name        = "mlops-mlflow"
    Environment = "production"
  }
}

resource "aws_s3_bucket_public_access_block" "mlops_public_access" {
  bucket = aws_s3_bucket.s3b-mlops-mlflow.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# resource "aws_s3_bucket_acl" "mlops_bucket_acl" {
#   bucket = aws_s3_bucket.s3b-mlops-mlflow.id
#   acl    = "public-read"
# }
