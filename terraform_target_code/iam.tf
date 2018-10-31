resource "aws_iam_role" "ecs_host_role" {
    name = "ecs_host_role"
    assume_role_policy = "${file("policies/ecs-role.json")}"
}

resource "aws_iam_role_policy" "ecs_instance_role_policy" {
    name = "ecs_instance_role_policy"
    policy = "${file("policies/ecs-instance-role-policy.json")}"
    role = "${aws_iam_role.ecs_host_role.id}"
}

resource "aws_iam_role_policy_attachment" "ecr-access" {
    role = "${aws_iam_role.ecs_host_role.id}"
    policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

resource "aws_iam_instance_profile" "ecs_iam_instance_profile" {
    name = "ecs-instance-profile"
    path = "/"
    roles = ["${aws_iam_role.ecs_host_role.name}"]
}
