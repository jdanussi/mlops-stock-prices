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
