output "alb_hostname" {
  value = "${aws_alb.ecs_alb.dns_name}"
}
