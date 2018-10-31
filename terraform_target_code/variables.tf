variable "aws_access_key" {
    description = "The AWS access key."
}

variable "aws_secret_key" {
    description = "The AWS secret key."
}

variable "region" {
    description = "The AWS region."
    default = "eu-west-1"
}

variable "az_qty" {
  description = "Number of AZs to cover in a given AWS region"
  default     = "2"
}

variable "ecs_cluster_name" {
    description = "Name of the Amazon ECS cluster."
    default = "app_cluster"
}

variable "amis" {
    description = "Hardcoded ami in eu-west-1."
    default = {
        eu-west-1 = "ami-066826c6a40879d75"
    }
}

variable "instance_type" {
    description = "Small instance for POC"
    default = "t2.micro"
}

variable "key_name" {
    description = "Key for ECS instance"
    default = "rep"
}

#Adding apps here
 
variable "app_port" {
  description = "app port"
  default     = "8000"
}

variable "app_name" {
  description = "app name"
  default     = "app"
}
