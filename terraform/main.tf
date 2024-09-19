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

resource "aws_vpc" "mlops_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "mlops-vpc"
    Environment = "production"
  }
}

resource "aws_subnet" "mlops_public_subnet" {
  vpc_id                  = aws_vpc.mlops_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"

  tags = {
    Name        = "mlops-pub_subnet"
    Environment = "production"
  }
}

resource "aws_subnet" "mlops_private_subnet" {
  vpc_id            = aws_vpc.mlops_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name        = "mlops-pri_subnet"
    Environment = "production"
  }
}

resource "aws_internet_gateway" "mlops_igw" {
  vpc_id = aws_vpc.mlops_vpc.id

  tags = {
    Name        = "mlops-igw"
    Environment = "production"
  }
}

resource "aws_route_table" "mlops_public_rt" {
  vpc_id = aws_vpc.mlops_vpc.id

  tags = {
    Name        = "mlops-pub_rt"
    Environment = "production"
  }
}

resource "aws_route" "public_route" {
  route_table_id         = aws_route_table.mlops_public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.mlops_igw.id
}

resource "aws_route_table_association" "mlops_public_assoc" {
  subnet_id      = aws_subnet.mlops_public_subnet.id
  route_table_id = aws_route_table.mlops_public_rt.id
}

resource "aws_security_group" "mlops_ec2_sg" {
  name        = "mlops-ec2_sg"
  description = "mlops security group for ec2 instance"
  vpc_id      = aws_vpc.mlops_vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "mlops-ec2_sg"
    Environment = "production"
  }
}

resource "aws_security_group" "mlops_rds_sg" {
  name        = "mlops-rds_sg"
  description = "mlops security group for rds instance"
  vpc_id      = aws_vpc.mlops_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.mlops_ec2_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "mlops-rds_sg"
    Environment = "production"
  }
}

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

resource "aws_key_pair" "mlops_key" {
  key_name   = "mlopskey"
  public_key = file("~/.ssh/mlopskey.pub")
}

resource "aws_instance" "airflow_node" {
  ami                    = data.aws_ami.server_ami.id
  ami                    = "ami-0a5c3558529277641"
  instance_type          = "t3.large"
  key_name               = aws_key_pair.mlops_key.id
  vpc_security_group_ids = [aws_security_group.mlops_ec2_sg.id]
  subnet_id              = aws_subnet.mlops_public_subnet.id
  iam_instance_profile   = aws_iam_instance_profile.mlops_ec2_profile.name
  user_data              = file("userdata-joao.sh")

  root_block_device {
    volume_size = 30
  }

  tags = {
    Name        = "mlops-ec2"
    Environment = "production"
  }

  provisioner "local-exec" {
    command = templatefile("linux-ssh-config.tpl", {
      hostname     = self.public_ip,
      user         = "ubuntu",
      identityfile = "~/.ssh/mlopskey"
    })
    interpreter = ["bash", "-c"]
  }
}

resource "aws_db_subnet_group" "mlops_db_subnet" {
  name       = "mlops_db_subnet"
  subnet_ids = [aws_subnet.mlops_private_subnet.id, aws_subnet.mlops_public_subnet.id]

  tags = {
    Name        = "db_subnet_group"
    Environment = "production"
  }
}

resource "aws_db_instance" "mlops_rds" {
  identifier                   = "mlops-rds-instance"
  allocated_storage            = 20
  db_subnet_group_name         = aws_db_subnet_group.mlops_db_subnet.id
  db_name                      = "airflow"
  username                     = "airflow"
  password                     = "${var.db_password}"
  engine                       = "postgres"
  engine_version               = "16.3"
  instance_class               = "db.t3.micro"
  parameter_group_name         = "default.postgres16"
  multi_az                     = false
  publicly_accessible          = true
  max_allocated_storage        = 100
  storage_encrypted            = true
  storage_type                 = "gp2"
  performance_insights_enabled = false
  backup_retention_period      = 1
  skip_final_snapshot          = true
  allow_major_version_upgrade  = false
  auto_minor_version_upgrade   = true
  vpc_security_group_ids       = [aws_security_group.mlops_rds_sg.id]
  delete_automated_backups     = true
  apply_immediately            = true

  tags = {
    Name        = "mlops-rds"
    Environment = "production"
  }
}
