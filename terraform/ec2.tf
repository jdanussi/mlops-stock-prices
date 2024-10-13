resource "aws_iam_policy" "mlops_ec2_policy" {
  name   = "mlops_ec2_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.mlops_ec2_policy_doc.json
}

resource "aws_iam_role" "mlops_ec2_role" {
  name = "mlops_ec2_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    tag-key = "mlops_ec2_role"
  }
}

resource "aws_iam_role_policy_attachment" "mlops_ec2_policy_attach" {
  role       = aws_iam_role.mlops_ec2_role.name
  policy_arn = aws_iam_policy.mlops_ec2_policy.arn
}

resource "aws_iam_instance_profile" "mlops_ec2_profile" {
  name = "mlops_ec2_profile"
  role = aws_iam_role.mlops_ec2_role.name
}

resource "aws_key_pair" "mlops_key" {
  key_name   = "mlopskey"
  public_key = file("~/.ssh/mlopskey.pub")
}

resource "aws_instance" "airflow_node" {
  ami                    = "ami-0a5c3558529277641"
  instance_type          = "t3.large"
  key_name               = aws_key_pair.mlops_key.id
  vpc_security_group_ids = [aws_security_group.mlops_ec2_sg.id]
  subnet_id              = aws_subnet.mlops_public_subnet.id
  iam_instance_profile   = aws_iam_instance_profile.mlops_ec2_profile.name
  #user_data              = file("userdata_joao.sh")
  user_data              = data.template_file.airflow_user_data.rendered
  user_data_replace_on_change = true
  depends_on             = [aws_instance.airflow_node, aws_db_instance.mlops_rds]

  root_block_device {
    volume_size = 30
  }

  tags = {
    Name        = "mlops-airflow"
    Environment = "production"
  }

  provisioner "local-exec" {
    command = templatefile("linux-ssh-config.tpl", {
      hostname     = self.public_ip,
      user         = "ec2-user",
      identityfile = "~/.ssh/mlopskey"
    })
    interpreter = ["bash", "-c"]
  }

}

resource "aws_instance" "mlflow_node" {
  ami                         = data.aws_ssm_parameter.this.value
  iam_instance_profile        = aws_iam_instance_profile.mlops_ec2_profile.name
  instance_type               = data.aws_ec2_instance_type.this.id
  key_name                    = aws_key_pair.mlops_key.id
  subnet_id                   = aws_subnet.mlops_public_subnet.id
  vpc_security_group_ids      = [aws_security_group.mlops_ec2_sg.id]
  user_data                   = data.template_file.mlflow_user_data.rendered
  user_data_replace_on_change = true

  root_block_device {
    encrypted = true
  }

  tags = {
    Name        = "mlops-mlflow"
    Environment = "production"
  }

  provisioner "local-exec" {
    command = templatefile("linux-ssh-config.tpl", {
      hostname     = self.public_ip,
      user         = "ec2-user",
      identityfile = "~/.ssh/mlopskey"
    })
    interpreter = ["bash", "-c"]
  }

  lifecycle {
    ignore_changes = [ami]
  }
}



