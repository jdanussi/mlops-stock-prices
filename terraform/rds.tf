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
  engine_version               = "14"
  instance_class               = "db.t3.micro"
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
