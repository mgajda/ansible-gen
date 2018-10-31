data "aws_availability_zones" "available" {}

resource "aws_vpc" "ecs_vpc" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
}

resource "aws_subnet" "ecs_subnet" {
  count             = "${var.az_qty}"
  cidr_block        = "${cidrsubnet(aws_vpc.ecs_vpc.cidr_block, 8, count.index)}"
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"
  vpc_id            = "${aws_vpc.ecs_vpc.id}"
}

resource "aws_internet_gateway" "ecs_internet_gateway" {
    vpc_id = "${aws_vpc.ecs_vpc.id}"
}

resource "aws_route_table" "ecs_route_table" {
    vpc_id = "${aws_vpc.ecs_vpc.id}"
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = "${aws_internet_gateway.ecs_internet_gateway.id}"
    }
}

resource "aws_route_table_association" "ecs_route_table_association" {
  count          = "${var.az_qty}"
  subnet_id      = "${element(aws_subnet.ecs_subnet.*.id, count.index)}"
  route_table_id = "${aws_route_table.ecs_route_table.id}"
}


resource "aws_security_group" "lb_sg" {
  description = "Application can access from all world"
  vpc_id = "${aws_vpc.ecs_vpc.id}"
  name   = "app-lb-sg"

  ingress {
    protocol    = "tcp"
    from_port   = "${var.app_port}"
    to_port     = "${var.app_port}"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
}

resource "aws_security_group" "ecs_sg" {
    name = "ecs-lb-sg"
    description = "Allows specific traffic"
    vpc_id = "${aws_vpc.ecs_vpc.id}"

    # keep ssh port open for debugging ECS instance
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
    	cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = "${var.app_port}"
        to_port = "${var.app_port}"
        protocol = "tcp"
	security_groups = [
      		"${aws_security_group.lb_sg.id}",
    	]
    }
    
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}
