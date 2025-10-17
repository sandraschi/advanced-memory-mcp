# Infrastructure as Code (IaC)

Infrastructure as Code manages and provisions infrastructure through machine-readable definition files rather than manual configuration.

## Core Principles

- [definition] IaC: Managing infrastructure using code and version control
- [principle] **Declarative over Imperative**: Describe what you want, not how to create it
- [principle] **Idempotent**: Running multiple times produces same result
- [principle] **Version Controlled**: Infrastructure changes tracked in Git

## Benefits

1. **Reproducibility**: Create identical environments reliably
2. **Speed**: Provision infrastructure in minutes
3. **Documentation**: Code is self-documenting
4. **Collaboration**: Team can review infrastructure changes
5. **Disaster Recovery**: Rebuild infrastructure from code

## Popular IaC Tools

### Terraform

```hcl
# Configure provider
provider "aws" {
  region = "us-west-2"
}

# Define resources
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"

  tags = {
    Name = "WebServer"
    Environment = "Production"
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-app-data-bucket"

  versioning {
    enabled = true
  }
}

# Output values
output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

- [tool] Terraform: Cloud-agnostic IaC tool
- [benefit] Works with AWS, Azure, GCP, and 100+ providers
- [feature] Plan before apply to preview changes

### Terraform Workflow
```bash
# Initialize
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy
```

### CloudFormation (AWS)

```yaml
Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t3.micro
      Tags:
        - Key: Name
          Value: WebServer

  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-app-data-bucket
      VersioningConfiguration:
        Status: Enabled

Outputs:
  InstanceIP:
    Value: !GetAtt WebServer.PublicIp
```

- [tool] CloudFormation: AWS-specific IaC service
- [benefit] Deep AWS integration
- [feature] Automatic rollback on errors

## State Management

### Terraform State
- [concept] State file tracks real infrastructure
- [best-practice] Store state remotely (S3, Terraform Cloud)
- [warning] Never manually edit state file
- [security] Encrypt state (may contain secrets)

```hcl
# Remote state configuration
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-west-2"
    encrypt = true
  }
}
```

## Modules and Reusability

```hcl
# Module definition (modules/web-server/main.tf)
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

resource "aws_instance" "server" {
  ami           = var.ami_id
  instance_type = var.instance_type
}

# Using module
module "web_server" {
  source        = "./modules/web-server"
  instance_type = "t3.small"
}
```

- [best-practice] Create reusable modules for common patterns
- [benefit] DRY (Don't Repeat Yourself) principle
- [organization] Separate modules for different components

## Relations
- builds_on [[DevOps Culture]]
- uses [[Terraform]]
- uses [[CloudFormation]]
- enables [[Immutable Infrastructure]]
- related_to [[Configuration Management]]

## Best Practices

1. **Version Control Everything**
   - All IaC code in Git
   - Review infrastructure changes via PRs
   - Tag releases

2. **Separate Environments**
   - Different state files per environment
   - Use workspaces or separate configurations
   - Never share state between environments

3. **Security**
   - Encrypt state files
   - Use secrets management (AWS Secrets Manager, Vault)
   - Least privilege IAM policies
   - Scan for security issues

4. **Testing**
   - Validate syntax before apply
   - Test in dev environment first
   - Use terraform plan extensively
   - Automated compliance checks

5. **Documentation**
   - README for each module
   - Variable descriptions
   - Output documentation
   - Architecture diagrams

*Treat infrastructure like code - version it, test it, review it.*
