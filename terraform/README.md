# Azure Web App Service with App Service Environment (ASE) - Terraform Module

This Terraform module deploys a complete Azure Web App Service infrastructure with App Service Environment (ASEv3), including all supporting services for enterprise deployments.

## Features

### Core Infrastructure
- ✅ **App Service Environment v3 (ASEv3)** - Isolated, dedicated infrastructure
- ✅ **ILB ASE Support** - Internal Load Balancer for private-only deployments (ideal for hub-spoke)
- ✅ **App Service Plans** - Isolated SKUs (I1V2, I2V2, I3V2)
- ✅ **Web Apps** - Windows or Linux runtime support
- ✅ **Virtual Network Integration** - Full VNet integration with subnets
- ✅ **Network Security Groups** - Pre-configured NSGs for ASE

### Security & Secrets
- ✅ **Managed Identity** - System-assigned managed identity for web apps
- ✅ **Azure Key Vault** - Centralized secrets management
- ✅ **Private Endpoints** - Private endpoints for web apps
- ✅ **HTTPS Only** - Forced HTTPS configuration

### Monitoring & Logging
- ✅ **Application Insights** - Application performance monitoring
- ✅ **Log Analytics** - Centralized logging workspace
- ✅ **Diagnostic Settings** - HTTP and console log streaming
- ✅ **Metrics & Alerts** - Built-in alerting capabilities

### High Availability
- ✅ **Auto-Scaling** - Automatic scaling based on CPU metrics
- ✅ **Zone Redundancy** - Multi-zone deployment support
- ✅ **Multi-Frontend Instances** - Highly available front-end infrastructure
- ✅ **Backup Configuration** - Automated backups for web apps

### DNS & Networking
- ✅ **Private DNS Zones** - For ILB ASE internal DNS resolution
- ✅ **VNet Integration** - Regional VNet integration
- ✅ **Network Isolation** - Complete network segmentation

## Architecture

### Hub-Spoke with ILB ASE
```
┌─ On-Premises (via ExpressRoute)
│
└─ Hub VNet (10.0.0.0/16)
   └─ ExpressRoute Gateway
   └─ (VNet Peering)
      │
      └─ Spoke VNet (10.3.0.0/16)
         ├─ ASE Subnet (10.3.1.0/24)
         │  └─ App Service Environment (ILB)
         │     └─ App Service Plans (Isolated SKU)
         │        └─ Web Apps
         │
         ├─ Private Endpoints Subnet (10.3.2.0/24)
         │  ├─ Web App Private Endpoint
         │  ├─ Key Vault Private Endpoint
         │  ├─ Storage Private Endpoint
         │  └─ SQL Database Private Endpoint
         │
         └─ NSGs (Network Security Groups)
            ├─ ASE NSG
            └─ Private Endpoints NSG

         Private DNS Zone: internal.company.com
         └─ DNS Records for ILB ASE
```

## Prerequisites

### Required
- Terraform >= 1.0
- Azure CLI
- Azure Subscription
- Service Principal with Contributor role

### Optional
- Azure Defender (for security scanning)
- Azure Bastion (for secure VM access)
- Application Gateway (for external ASE with WAF)

## Quick Start

### 1. Clone and Setup
```bash
cd terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

### 2. Authenticate with Azure
```bash
# Option A: Using CLI
az login
az account set --subscription "Your-Subscription-ID"

# Option B: Using Service Principal Environment Variables
export ARM_SUBSCRIPTION_ID="your-subscription-id"
export ARM_CLIENT_ID="your-client-id"
export ARM_CLIENT_SECRET="your-client-secret"
export ARM_TENANT_ID="your-tenant-id"
```

### 3. Deploy
```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Apply deployment
terraform apply tfplan
```

### 4. Verify
```bash
# View all outputs
terraform output

# Check resources
az resource list --resource-group rg-webapp-prod --output table
```

## Module Outputs

The module provides comprehensive outputs for your deployed infrastructure:

| Output | Description |
|--------|-------------|
| `resource_group_name` | Name of the resource group |
| `ase_id` | App Service Environment ID |
| `ase_name` | ASE name |
| `ase_kind` | ASE type (ILBASEv3 or ASEv3) |
| `ase_internal_ip_address` | Internal IP of ILB ASE |
| `app_service_plan_name` | App Service Plan name |
| `web_app_name` | Web app name |
| `web_app_default_hostname` | Default hostname |
| `web_app_identity` | Managed identity details |
| `application_insights_instrumentation_key` | AppInsights key |
| `key_vault_uri` | Key Vault URI |
| `private_endpoint_ip_address` | Private IP of web app endpoint |

## Variables

### Essential Variables

```hcl
# Azure Credentials
subscription_id = "00000000-0000-0000-0000-000000000000"
tenant_id       = "00000000-0000-0000-0000-000000000000"
client_id       = "00000000-0000-0000-0000-000000000000"
client_secret   = "your-secret"

# Environment
project_name = "webapp"
environment  = "prod"
location     = "eastus"

# ASE Configuration
ase_kind               = "ILBASEv3"  # or "ASEv3" for external
ase_availability_zones = 3
ase_frontend_scale_factor = 3

# App Service Plan
app_service_plan_sku          = "I1V2"  # or I2V2, I3V2
app_service_plan_worker_count = 3

# Web App
web_app_runtime_stack = "TOMCAT|10.0"  # or DOTNET|6.0, NODE|18-lts
app_service_plan_is_linux = true
```

See `variables.tf` for all available variables.

## Deployment Scenarios

### Scenario 1: ILB ASE (Recommended for Hub-Spoke)
```hcl
ase_kind                = "ILBASEv3"
app_service_plan_is_linux = true
enable_private_endpoint = true
enable_private_dns_zone = true
```

### Scenario 2: External ASE with Application Gateway
```hcl
ase_kind                = "ASEv3"
# Add Application Gateway configuration separately
```

### Scenario 3: Development Environment (Cost-Optimized)
```hcl
ase_kind                    = "ILBASEv3"
ase_availability_zones      = 1  # Single zone
app_service_plan_worker_count = 1
auto_scale_min_count        = 1
auto_scale_max_count        = 3
```

## Customization

### Adding Connection Strings
```hcl
web_app_connection_strings = {
  "DefaultConnection" = {
    value = "Server=myserver.database.windows.net;..."
    type  = "SQLAzure"
  }
}
```

### Custom Application Settings
```hcl
web_app_app_settings = {
  "CUSTOM_SETTING"           = "value"
  "JAVA_OPTS"                = "-Xmx2g -Xms1g"
  "LOG_LEVEL"                = "DEBUG"
}
```

### Enable Azure AD Authentication
```hcl
enable_authentication = true
azure_ad_tenant_id    = "your-tenant-id"
azure_ad_client_id    = "your-app-id"
azure_ad_client_secret = "your-app-secret"
```

## State Management

### Local State (Development)
```bash
# Default - state stored locally in terraform.tfstate
# Good for: Single developer, testing, dev environments
```

### Remote State (Recommended for Teams/Production)
```bash
# Create storage account for terraform state
az storage account create \
  --name tfstatestg \
  --resource-group rg-terraform \
  --location eastus \
  --sku Standard_LRS

# Create container
az storage container create \
  --name tfstate \
  --account-name tfstatestg

# Update backend in main.tf:
# terraform {
#   backend "azurerm" {
#     resource_group_name  = "rg-terraform"
#     storage_account_name = "tfstatestg"
#     container_name       = "tfstate"
#     key                  = "azure-webapp-ase.tfstate"
#   }
# }

# Reinitialize
terraform init
```

## Maintenance

### Updating Resources
```bash
# Edit terraform.tfvars
nano terraform.tfvars

# Plan changes
terraform plan

# Review and apply
terraform apply
```

### Scaling Up
```hcl
# In terraform.tfvars:
app_service_plan_worker_count = 5  # Increase from 3
auto_scale_max_count         = 15   # Increase from 10
```

### Changing ASE Size
```hcl
# Change SKU
app_service_plan_sku = "I2V2"  # Upgrade from I1V2
```

## Troubleshooting

### Common Issues

**Issue: "Insufficient capacity in ASE"**
- Wait for capacity to free up
- Scale down other app service plans if possible
- Monitor in Azure Portal

**Issue: "Private endpoint creation failed"**
- Ensure subnet has private endpoint network policies enabled
- Check NSG allows traffic
- Verify subnet is not full (/24 minimum recommended)

**Issue: "ASE deployment timeout"**
- ASE creation can take 45+ minutes
- Check deployment status in Azure Portal
- Monitor activity logs for errors

### Debugging
```bash
# Validate configuration
terraform validate

# Check current state
terraform show

# View resource details
terraform state show azurerm_app_service_environment_v3.main

# Enable debug logging
TF_LOG=DEBUG terraform apply

# Check Azure resources
az resource list --resource-group rg-webapp-prod
```

## Security Best Practices

### DO
✅ Use Managed Identity for all authentication
✅ Store secrets in Key Vault
✅ Enable HTTPS only
✅ Use Private Endpoints for private deployments
✅ Enable Azure Defender for App Service
✅ Use ILB ASE for sensitive workloads
✅ Implement NSG rules with least privilege
✅ Enable audit logging

### DON'T
❌ Hardcode secrets in code or terraform.tfvars
❌ Use public endpoints for internal applications
❌ Disable HTTPS
❌ Skip network security groups
❌ Use overly permissive NSG rules
❌ Store credentials in comments or documentation
❌ Commit terraform.tfvars to version control

## Cost Estimation

### ILB ASE (Monthly - Approximate)
| Component | SKU | Monthly Cost |
|-----------|-----|--------------|
| ASE Compute | I1V2 x 3 workers | $220 |
| App Service Plan | I1V2 | Included |
| Application Insights | Pay-as-you-go | $5-50 |
| Log Analytics | PerGB2018 | $5-20 |
| Key Vault | Standard | $0.34 |
| Storage Account | Standard GRS | $10-20 |
| **Total** | | **$240-300+** |

### Cost Optimization Tips
- Use single zone (1 availability zone) for dev/test
- Scale down outside business hours
- Use reserved instances for predictable workloads
- Monitor actual usage and right-size

## Cleanup

### Destroy All Resources
```bash
# WARNING: This will DELETE everything

terraform destroy

# Or with specific resource
terraform destroy -target=azurerm_resource_group.main

# Confirm with 'yes'
```

### Remove Only Web App (Keep ASE/Plan)
```bash
terraform destroy -target=azurerm_windows_web_app.main
```

## Support & Documentation

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest)
- [Azure ASE Documentation](https://learn.microsoft.com/azure/app-service/environment/)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Azure Migration Guide](../AZURE_MIGRATION_GUIDE.md)

## License

This Terraform module is provided as-is for use in your Azure environments.

## Contributing

For improvements or bug fixes, please follow these steps:
1. Test changes in a dev environment
2. Validate with `terraform validate` and `terraform fmt`
3. Document changes
4. Submit pull request with detailed description

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release with ASEv3, App Service Plans, Web Apps, Networking, Monitoring |

---

**Last Updated**: March 2024
**Terraform Version**: >= 1.0
**Provider Version**: >= 3.80 (azurerm)

For the latest version and updates, visit the repository.
