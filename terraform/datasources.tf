data "aws_ami" "server_ami" {
  most_recent = true

  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}


/* Terraform LocalStack example
data "aws_ami" "server_ami" {
  most_recent      = true

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
} */

data "aws_ec2_instance_types" "this" {
  filter {
    name   = "burstable-performance-supported"
    values = ["true"]
  }

  filter {
    name   = "current-generation"
    values = ["true"]
  }

  filter {
    name   = "memory-info.size-in-mib"
    values = ["1024"]
  }

  filter {
    name   = "processor-info.supported-architecture"
    values = ["arm64"]
  }
}

data "aws_ec2_instance_type" "this" {
  instance_type = data.aws_ec2_instance_types.this.instance_types.0
}

data "aws_ssm_parameter" "this" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-${data.aws_ec2_instance_type.this.supported_architectures.0}"

  with_decryption = false
}

data "aws_iam_policy_document" "mlops_ec2_policy_doc" {
  statement {

    sid = "1"

    effect = "Allow"

    actions = [
      "rds:*",
      "s3:*",
      "sns:*",
      "ssm:*"
    ]

    resources = ["*"]
  }
}

data "template_file" "airflow_user_data" {
  template = "${file("${path.module}/userdata_airflow.sh")}"
  vars = {
    DB_ENDPOINT  = aws_db_instance.mlops_rds.endpoint
    db_password  = "${var.db_password}"
    BUCKET  = "${var.bucket}"
    MLFLOW_INSTANCE = aws_instance.mlflow_node.public_dns
    AWS_ID       = "${var.AWS_ID}"
    AWS_KEY      = "${var.AWS_KEY}"
  }
}

data "template_file" "mlflow_user_data" {
  template = "${file("${path.module}/userdata_mlflow.sh")}"
  vars = {
    DB_ENDPOINT  = aws_db_instance.mlops_rds.endpoint
    db_password  = "${var.db_password}"
    S3_BUCKET  = "${var.bucket}"
    AWS_ID       = "${var.AWS_ID}"
    AWS_KEY      = "${var.AWS_KEY}"
  }
}
