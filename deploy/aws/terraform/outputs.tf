output "public_url" {
  description = "Where the dashboard is served; the API is under /api."
  value       = local.public_url
}

output "public_ip" {
  value = aws_eip.app.public_ip
}

output "instance_id" {
  description = "Pass as the EC2_INSTANCE_ID GitHub variable, or let the workflow look it up by the Name tag."
  value       = aws_instance.app.id
}

output "ecr_repository_url" {
  description = "Image name for docker push and for the ECR_REPOSITORY GitHub variable."
  value       = aws_ecr_repository.app.repository_url
}

output "github_deploy_role_arn" {
  description = "Set as the AWS_DEPLOY_ROLE_ARN GitHub variable."
  value       = aws_iam_role.github_deploy.arn
}

output "log_group" {
  value = aws_cloudwatch_log_group.app.name
}

output "session_manager_command" {
  description = "Shell on the instance without SSH."
  value       = "aws ssm start-session --region ${var.region} --target ${aws_instance.app.id}"
}

output "region" {
  value = var.region
}
