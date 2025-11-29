# Data source for latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 Instance
resource "aws_instance" "main" {
  ami           = var.ami_id != "" ? var.ami_id : data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = var.vpc_security_group_ids
  associate_public_ip_address = var.associate_public_ip

  key_name             = var.key_name != "" ? var.key_name : null
  iam_instance_profile = var.iam_instance_profile != "" ? var.iam_instance_profile : null

  user_data = var.user_data

  monitoring = var.enable_monitoring

  root_block_device {
    volume_size           = var.root_volume_size
    volume_type           = var.root_volume_type
    delete_on_termination = true
    encrypted             = true

    tags = merge(
      {
        Name        = "${var.instance_name}-root"
        Environment = var.environment
      },
      var.tags
    )
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required" # IMDSv2
    http_put_response_hop_limit = 1
  }

  tags = merge(
    {
      Name        = var.instance_name
      Environment = var.environment
      Project     = var.project_name
    },
    var.tags
  )

  lifecycle {
    ignore_changes = [
      ami,
      user_data,
    ]
  }
}

# Additional EBS Volumes
resource "aws_ebs_volume" "additional" {
  count             = length(var.additional_ebs_volumes)
  availability_zone = aws_instance.main.availability_zone
  size              = var.additional_ebs_volumes[count.index].volume_size
  type              = var.additional_ebs_volumes[count.index].volume_type
  encrypted         = true

  tags = merge(
    {
      Name        = "${var.instance_name}-${var.additional_ebs_volumes[count.index].device_name}"
      Environment = var.environment
    },
    var.tags
  )
}

resource "aws_volume_attachment" "additional" {
  count       = length(var.additional_ebs_volumes)
  device_name = var.additional_ebs_volumes[count.index].device_name
  volume_id   = aws_ebs_volume.additional[count.index].id
  instance_id = aws_instance.main.id
}

