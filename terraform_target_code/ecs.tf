resource "aws_ecs_cluster" "ecs_app_cluster" {
    name = "${var.ecs_cluster_name}"
}

resource "aws_autoscaling_group" "ecs_autoscaling_group" {
    name = "autoscaling ${var.ecs_cluster_name}"
    min_size = "1"
    max_size = "1"
    desired_capacity = "1"
    health_check_type = "EC2"
    launch_configuration = "${aws_launch_configuration.ecs_launch_configuration.name}"
    vpc_zone_identifier  = ["${aws_subnet.ecs_subnet.*.id}"]

}

resource "aws_launch_configuration" "ecs_launch_configuration" {
    name = "launch configuration ${var.ecs_cluster_name}"
    image_id = "${lookup(var.amis, var.region)}"
    instance_type = "${var.instance_type}"
    security_groups = ["${aws_security_group.ecs_sg.id}"]
    iam_instance_profile = "${aws_iam_instance_profile.ecs_iam_instance_profile.name}"
    key_name = "${var.key_name}"
    associate_public_ip_address = true
    user_data = "#!/bin/bash\necho ECS_CLUSTER='${var.ecs_cluster_name}' > /etc/ecs/ecs.config"
}
