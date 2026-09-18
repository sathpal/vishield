variable "region" {
  description = "AWS region. ap-south-1 (Mumbai) keeps latency low for a team in India."
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Name used for every resource and tag."
  type        = string
  default     = "vishield"
}

variable "instance_type" {
  description = "EC2 instance type. t3.small (2 vCPU, 2 GB) is enough for API + dashboard + proxy with the mock STT."
  type        = string
  default     = "t3.small"
}

variable "root_volume_gb" {
  description = "Root disk size in GB (Docker images plus the SQLite metadata database)."
  type        = number
  default     = 20
}

variable "domain" {
  description = "Optional DNS name pointing at the Elastic IP. When set, Caddy serves HTTPS automatically. Leave empty for plain HTTP on the IP."
  type        = string
  default     = ""
}

variable "allowed_ingress_cidrs" {
  description = "CIDR blocks allowed to reach ports 80 and 443. Narrow this to the college network for a private review."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "github_repo" {
  description = "GitHub repository (owner/name) allowed to deploy through OIDC."
  type        = string
  default     = "sathpal/vishield"
}

variable "deploy_branch" {
  description = "Branch whose GitHub Actions runs may assume the deploy role."
  type        = string
  default     = "cloud/aws"
}

variable "create_github_oidc_provider" {
  description = "Set to false if the account already has the token.actions.githubusercontent.com OIDC provider."
  type        = bool
  default     = true
}

variable "budget_limit_usd" {
  description = "Monthly cost ceiling for the budget alarm."
  type        = number
  default     = 20
}

variable "budget_email" {
  description = "Email that receives the budget alarm at 80 % of the limit. Empty disables the budget."
  type        = string
  default     = ""
}

variable "log_retention_days" {
  description = "CloudWatch log retention."
  type        = number
  default     = 14
}
