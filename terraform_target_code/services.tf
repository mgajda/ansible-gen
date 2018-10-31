resource "aws_ecs_task_definition" "app" {
    family = "app"
    container_definitions = "${file("task-definitions/app.json")}"
}

resource "aws_ecs_service" "app_service" {
    name = "app_service"
    cluster = "${aws_ecs_cluster.ecs_app_cluster.id}"
    task_definition = "${aws_ecs_task_definition.app.arn}"
    desired_count = 1

    load_balancer {
      target_group_arn = "${aws_alb_target_group.ecs_alb_target_group.id}"
      container_name   = "${var.app_name}"
      container_port   = "${var.app_port}"
    }

    depends_on = [
      "aws_alb_listener.ecs_alb_listener",
    ]
}
