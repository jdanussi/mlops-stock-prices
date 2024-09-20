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
  template = "${file("${path.module}/userdata_joao.sh")}"
  vars = {
    DB_ENDPOINT  = aws_db_instance.mlops_rds.endpoint
    db_password  = "${var.db_password}"
    AWS_ID       = "${var.AWS_ID}"
    AWS_KEY      = "${var.AWS_KEY}"
  }
}
