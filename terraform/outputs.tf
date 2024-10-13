# Generate output of IAM role name
output "iam_instance_profile_name" {
  value       = aws_iam_instance_profile.mlops_ec2_profile.name
  description = "IAM role name"
}

output "ec2_instance_airflow_node_public_dns" {
  value       = aws_instance.airflow_node.public_dns
  description = "ec2 instance airflow_node public_dns"
}

output "ec2_instance_mlflow_node_public_dns" {
  value       = aws_instance.mlflow_node.public_dns
  description = "ec2 instance mlflow_node public_dns"
}

output "rds_instance_mlops_rds" {
  value       = aws_db_instance.mlops_rds.endpoint
  description = "The endpoint of the RDS instance."
}
