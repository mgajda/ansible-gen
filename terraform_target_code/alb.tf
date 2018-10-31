resource "aws_alb" "ecs_alb" {
  name            = "ecs-alb"
  subnets         = ["${aws_subnet.ecs_subnet.*.id}"]
  security_groups = ["${aws_security_group.lb_sg.id}"]
}

resource "aws_alb_target_group" "ecs_alb_target_group" {
  name        = "alb-target-group"
  port        = "${var.app_port}"
  protocol    = "HTTP"
  vpc_id      = "${aws_vpc.ecs_vpc.id}"
}

resource "aws_alb_listener" "ecs_alb_listener" {
  load_balancer_arn = "${aws_alb.ecs_alb.id}"
  port              = "${var.app_port}"
  protocol          = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.ecs_alb_target_group.id}"
    type             = "forward"
  }
}
