# Terraform Deployment Guide for Azure Web App Service with ASE

## Prerequisites

### 1. Install Required Tools
```bash
# Install Terraform (macOS with Homebrew)
brew install terraform

# Install Azure CLI
brew install azure-cli

# Verify installations
terraform --version
az --version
```

### 2. Azure Subscription & Authentication

#### Option A: Using Azure CLI
```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "Your-Subscription-ID"

# Create a Service Principal for Terraform
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/SUBSCRIPTION_ID"

# This will output:
# {
#   "appId": "YOUR_CLIENT_ID",
#   "displayName": "...",
#   "password": "YOUR_CLIENT_SECRET",
#   "tenant": "YOUR_TENANT_ID"
# }

# Export these values for Terraform
export ARM_SUBSCRIPTION_ID="YOUR_SUBSCRIPTION_ID"
export ARM_CLIENT_ID="YOUR_CLIENT_ID"
export ARM_CLIENT_SECRET="YOUR_CLIENT_SECRET"
export ARM_TENANT_ID="YOUR_TENANT_ID"
```

#### Option B: Using Environment Variables in terraform.tfvars
See `terraform.tfvars.example` for reference

### 3. Create terraform.tfvars
```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
# or
vim terraform.tfvars
```

---

## Project Structure

```
terraform/
├── main.tf                      # Provider and outputs
├── variables.tf                 # Variable definitions
├── resources.tf                 # Resource definitions
├── terraform.tfvars.example     # Example variables
├── terraform.tfvars             # Your actual variables (DO NOT COMMIT)
└── .gitignore                   # Git ignore rules
```

### .gitignore Content
```bash
# Local .terraform directories
**/.terraform/*

# .tfstate files
*.tfstate
*.tfstate.*

# Crash log files
crash.log
crash.*.log

# Exclude all .tfvars files, which are likely to contain sentitive data
*.tfvars
*.tfvars.json

# Ignore override files
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# Include override files you do want to commit
!example_override.tf

# Ignore CLI configuration files
.terraformrc
terraform.rc

# Ignore plan files
*.tfplan

# Ignore .env files
.env*
```

---

## Deployment Steps

### Step 1: Initialize Terraform
```bash
cd terraform

# Initialize Terraform working directory
# This downloads providers and sets up state management
terraform init
```

### Step 2: Validate Configuration
```bash
# Check syntax and configuration
terraform validate

# Expected output: Success! The configuration is valid.
```

### Step 3: Format Code (Optional but Recommended)
```bash
# Format all Terraform files
terraform fmt -recursive
```

### Step 4: Plan Deployment
```bash
# Create and show an execution plan
terraform plan -out=tfplan

# Review the plan carefully to ensure:
# - Correct resources are being created
# - No unexpected deletions
# - Correct sizing and configuration

# You can also save the plan to review later
terraform plan -out=deployment.tfplan
```

### Step 5: Apply Configuration
```bash
# Option A: Apply with previously saved plan (recommended for production)
terraform apply deployment.tfplan

# Option B: Apply with confirmation prompt
terraform apply

# Type "yes" to confirm deployment
# Deployment typically takes 30-45 minutes for ASE creation

# Option C: Auto-approve (use with caution, only for dev/test)
terraform apply -auto-approve
```

### Step 6: Verify Deployment
```bash
# View all outputs
terraform output

# Specific output example:
terraform output ase_name
terraform output web_app_name
terraform output web_app_identity

# Check resources in Azure Portal or CLI
az resource list --resource-group rg-webapp-prod
```

---

## Important Variables Explained

### ASE Configuration
- `ase_kind`: 
  - `"ILBASEv3"` - Internal Load Balancer (recommended for hub-spoke with private access)
  - `"ASEv3"` - External (for public-facing apps)
  
- `ase_availability_zones`: 1, 2, or 3 zones (3 recommended for HA)
- `ase_frontend_scale_factor`: Number of front-end instances (3 recommended for HA)

### App Service Plan SKU
- `I1V2`: 1 core, 3.5 GB RAM (entry-level)
- `I2V2`: 2 cores, 7 GB RAM (medium workloads)
- `I3V2`: 4 cores, 14 GB RAM (high performance)

### Linux vs Windows
- `app_service_plan_is_linux = true`: Use Linux runtime (Tomcat, Node.js, Python, etc.)
- `app_service_plan_is_linux = false`: Use Windows runtime (.NET, Java on Windows)

### Security
- `web_app_https_only = true`: Force HTTPS
- `enable_managed_identity = true`: Use system-assigned managed identity
- `enable_private_endpoint = true`: Create private endpoint for web app

---

## Common Operations

### View Deployment Status
```bash
# Check current state
terraform show

# Show specific resource
terraform state show azurerm_app_service_environment_v3.main

# List all resources
terraform state list
```

### Update Configuration
```bash
# To update variables, edit terraform.tfvars
nano terraform.tfvars

# Plan changes
terraform plan

# Apply changes
terraform apply
```

### Scale App Service Plan
```bash
# Edit terraform.tfvars
# Change: app_service_plan_worker_count = 5

# Plan and apply
terraform plan
terraform apply

# Auto-scaling will handle traffic-based scaling after this baseline
```

### Destroy Resources (Careful!)
```bash
# WARNING: This will DELETE all resources

# Plan destruction
terraform plan -destroy

# Destroy
terraform destroy

# Confirm with 'yes' when prompted
```

### Refresh State
```bash
# Update local state to match Azure
terraform refresh

# Useful after manual changes in Azure Portal
```

---

## Troubleshooting

### Issue: "Error acquiring the state lock"
**Solution**: Wait for previous operation to complete or manually unlock:
```bash
terraform force-unlock <LOCK_ID>
```

### Issue: "Insufficient capacity in ASE"
**Solution**: The ASE might be at capacity. Either:
- Wait for capacity to free up
- Delete non-critical app service plans
- Upgrade to larger ASE if persistent

### Issue: "Invalid provider configuration"
**Solution**: Ensure Azure credentials are set:
```bash
# Check environment variables
printenv | grep ARM_

# Or verify terraform.tfvars has correct values
cat terraform.tfvars | grep subscription_id
```

### Issue: "Resource already exists"
**Solution**: 
- Someone may have created it manually
- Or previous terraform didn't clean up properly
```bash
# Import existing resource
terraform import azurerm_resource_group.main /subscriptions/SUB_ID/resourceGroups/RG_NAME

# Then plan/apply as normal
terraform plan
terraform apply
```

### ASE Deployment Takes Too Long
- ASE creation can take 45 minutes or more
- Monitor in Azure Portal → Resource Group → Deployments
- Check for errors with:
```bash
az monitor activity-log list --resource-group rg-webapp-prod --max-events 20
```

---

## Monitoring Deployment

### Via Azure Portal
1. Go to Resource Groups
2. Select your resource group (e.g., `rg-webapp-prod`)
3. View "Deployments" tab
4. Check latest deployment status

### Via Azure CLI
```bash
# Get resource group information
az group show --name rg-webapp-prod

# List all resources
az resource list --resource-group rg-webapp-prod --output table

# Check ASE status
az appservice ase show --name ase-webapp-prod --resource-group rg-webapp-prod

# Check web app
az webapp show --name webapp-webapp-prod --resource-group rg-webapp-prod
```

### Via Terraform
```bash
# View all outputs
terraform output

# View specific resource state
terraform state show azurerm_linux_web_app.main[0]

# View diagnostics
terraform console
> azurerm_linux_web_app.main[0].identity
```

---

## Security Best Practices

### Protecting Sensitive Data
1. **Never commit `terraform.tfvars`**
   - It contains secrets (subscription ID, client secret, etc.)
   - Add to `.gitignore`
   - Use environment variables instead

2. **Use Azure Key Vault for sensitive values**
   - Store database passwords in Key Vault
   - Reference from Terraform using `data.azurerm_key_vault_secret`

3. **Enable state encryption**
   - Use remote state (Azure Storage) with encryption
   - Use encrypted local state

### Terraform State Management
```bash
# Configure remote state (recommended for teams/production)
# Create storage account first, then configure backend

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform"
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "azure-webapp-ase.tfstate"
  }
}

# Then reinitialize:
# terraform init
```

---

## Post-Deployment Configuration

### 1. Deploy Your Application
```bash
# Get web app name
WEB_APP_NAME=$(terraform output -raw web_app_name)

# Deploy application (WAR file for Java)
az webapp deployment source config-zip \
  --resource-group rg-webapp-prod \
  --name $WEB_APP_NAME \
  --src application.war
```

### 2. Configure DNS (ILB ASE)
```bash
# Get ILB internal IP
ILB_IP=$(az appservice ase show \
  --name ase-webapp-prod \
  --resource-group rg-webapp-prod \
  --query "internalIpAddress" \
  --output tsv)

echo "ILB IP: $ILB_IP"

# Create DNS records pointing to this IP
# (Configure in your internal DNS server or Azure Private DNS)
```

### 3. Configure VNet Peering (Hub-Spoke)
```bash
# Peer this VNet with your hub VNet
az network vnet peering create \
  --name "peer-spoke-to-hub" \
  --resource-group rg-webapp-prod \
  --vnet-name vnet-webapp-prod \
  --remote-group rg-hub \
  --remote-vnet vnet-hub \
  --allow-vnet-access true \
  --allow-forwarded-traffic true
```

### 4. Enable Logging & Monitoring
```bash
# Application Insights is automatically enabled
# View metrics in Azure Portal:
# Resource Group → Application Insights → Performance

# Check logs
az monitor activity-log list --resource-group rg-webapp-prod
```

---

## Updating Terraform Code

### When to Run `terraform init` Again
- When changing backend configuration
- After pulling updated code from git with provider changes
- When adding new required providers

### When to Run `terraform validate`
- After any manual edits to .tf files
- Before committing to git
- As part of CI/CD pipeline

### Typical Workflow for Changes
```bash
# 1. Edit configuration
nano resources.tf

# 2. Validate
terraform validate

# 3. Format
terraform fmt

# 4. Plan
terraform plan -out=tfplan

# 5. Review plan carefully

# 6. Apply
terraform apply tfplan

# 7. Verify
terraform output
```

---

## Cleanup

### To Completely Remove All Resources
```bash
# WARNING: This is destructive

# 1. Plan destruction
terraform plan -destroy

# 2. Review what will be deleted

# 3. Destroy
terraform destroy

# 4. Confirm with 'yes'

# 5. Remove local state files (if not using remote state)
rm -rf .terraform
rm terraform.tfstate*
```

---

## Additional Resources

- [Terraform Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure App Service Environment Documentation](https://learn.microsoft.com/azure/app-service/environment/)
- [Terraform Best Practices](https://www.terraform.io/cloud-docs/recommended-practices)
- [Azure Terraform Examples](https://github.com/Azure/terraform-azurerm-examples)

---

## Support & Troubleshooting

### Get Help
```bash
# Check Terraform syntax
terraform fmt -check

# Validate configuration
terraform validate -json

# Check provider version
terraform providers

# Get detailed error messages
terraform apply -var="TF_LOG=DEBUG"

# Check Azure status
az account show
az group list
```

### Useful Commands Reference
```bash
# Planning and applying
terraform init                # Initialize
terraform validate            # Validate syntax
terraform format              # Format code
terraform plan               # Preview changes
terraform apply              # Apply changes
terraform destroy            # Remove resources

# State management
terraform state list         # List resources
terraform state show ADDR    # Show resource details
terraform state rm ADDR      # Remove from state
terraform refresh            # Update state

# Troubleshooting
terraform console            # Interactive console
terraform graph              # Dependency graph
terraform providers          # Provider info
terraform output             # View outputs
```
