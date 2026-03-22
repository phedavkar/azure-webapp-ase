# Terraform Deployment Checklist

## Pre-Deployment Preparation

### 1. Infrastructure Planning
- [ ] Decided on ASE type: **ILBASEv3** (internal) or **ASEv3** (external)
- [ ] Chosen Azure region: **_____________**
- [ ] Chosen app name/project: **_____________**
- [ ] Planned VNet address space: **10.3.0.0/16** (or custom: **_____________**)
- [ ] Planned ASE subnet: **10.3.1.0/24** (or custom: **_____________**)
- [ ] Decided on ASE SKU: **I1V2** / **I2V2** / **I3V2** (default: I1V2)
- [ ] Planned number of workers: **_____________** (default: 3)
- [ ] Decided on runtime: **TOMCAT|10.0** / **DOTNET|6.0** / **NODE|18** (or other)

### 2. Budget & Cost Approval
- [ ] Reviewed monthly cost estimate ($240-290 for ILB ASE)
- [ ] Got budget approval
- [ ] Identified cost center/billing code: **_____________**
- [ ] Notified finance team

### 3. Azure Credentials
- [ ] Have Azure Subscription ID: **_____________**
- [ ] Have Azure Tenant ID: **_____________**
- [ ] Created Service Principal with Contributor role
- [ ] Have Client ID: **_____________**
- [ ] Have Client Secret: **_____________** (securely stored)

### 4. Local Environment Setup
- [ ] Terraform installed (`terraform --version` works)
- [ ] Azure CLI installed (`az --version` works)
- [ ] Git installed (if using version control)
- [ ] Text editor available (nano, vim, VS Code, etc.)
- [ ] Bash/zsh shell available

### 5. Security & Compliance
- [ ] Reviewed security requirements
- [ ] Confirmed HTTPS-only requirement
- [ ] Reviewed Key Vault setup
- [ ] Confirmed Managed Identity usage
- [ ] Checked Azure Defender requirements
- [ ] Reviewed network isolation requirements
- [ ] Confirmed Private Endpoint needs

### 6. Network Coordination (if Hub-Spoke)
- [ ] Coordinated with network team
- [ ] Got approval for VNet address space
- [ ] Planned VNet peering with hub
- [ ] Confirmed ExpressRoute connectivity
- [ ] Reviewed network security requirements
- [ ] Hub VNet details: **_____________**

### 7. Application Readiness
- [ ] Application runtime identified: **_____________**
- [ ] Application version/branch ready: **_____________**
- [ ] Database requirements documented
- [ ] External API dependencies listed
- [ ] Configuration externalized (no hardcoding)
- [ ] Health check endpoint defined: **_____________**
- [ ] Application artifact ready (WAR/JAR/image)

### 8. Team Communication
- [ ] Notified DevOps team
- [ ] Notified security team
- [ ] Scheduled deployment window
- [ ] Created incident response plan
- [ ] Prepared rollback procedures
- [ ] Team members trained on new infrastructure

### 9. Documentation Preparation
- [ ] Created operational runbooks
- [ ] Documented scaling procedures
- [ ] Documented backup procedures
- [ ] Created monitoring dashboard plan
- [ ] Prepared troubleshooting guide

---

## Deployment Phase

### Step 1: Prepare Terraform Directory
```bash
# In project root:
cd terraform
ls -la

# Expected files:
# - main.tf                    ✓ Present?
# - variables.tf              ✓ Present?
# - resources.tf              ✓ Present?
# - terraform.tfvars.example  ✓ Present?
# - README.md                 ✓ Present?
# - DEPLOYMENT_GUIDE.md       ✓ Present?
```

Checklist:
- [ ] All .tf files present
- [ ] All documentation files present
- [ ] terraform directory clean (no extra files)

### Step 2: Create terraform.tfvars
```bash
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit file
nano terraform.tfvars
```

Checklist - Fill in these values:
- [ ] subscription_id = "your-subscription-id"
- [ ] tenant_id = "your-tenant-id"
- [ ] client_id = "your-service-principal-client-id"
- [ ] client_secret = "your-service-principal-secret"
- [ ] project_name = "webapp"
- [ ] environment = "prod" (or staging/dev)
- [ ] location = "eastus"
- [ ] ase_kind = "ILBASEv3" (or ASEv3)
- [ ] web_app_runtime_stack = "TOMCAT|10.0" (or your runtime)
- [ ] app_service_plan_sku = "I1V2" (or I2V2/I3V2)
- [ ] All other optional variables reviewed

Verification:
```bash
# Check file is not empty
wc -l terraform.tfvars

# Verify key values set
grep -E "subscription_id|client_id|project_name" terraform.tfvars
```

Checklist:
- [ ] terraform.tfvars created
- [ ] All required values filled
- [ ] File not empty and readable
- [ ] File added to .gitignore (secret!)

### Step 3: Verify Azure Connectivity
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "YOUR-SUBSCRIPTION-ID"

# Verify subscription
az account show

# List resource groups to verify access
az group list --output table
```

Checklist:
- [ ] `az login` succeeded
- [ ] Correct subscription set
- [ ] Can list existing resources
- [ ] Have Contributor role or higher

### Step 4: Initialize Terraform
```bash
# Initialize Terraform
terraform init

# Check for errors
# Expected output: "Terraform has been successfully configured!"
```

Checklist:
- [ ] `terraform init` completed successfully
- [ ] `.terraform` directory created
- [ ] No error messages
- [ ] `.terraform.lock.hcl` created (do not edit)

### Step 5: Validate Configuration
```bash
# Validate Terraform files
terraform validate

# Expected output: "Success! The configuration is valid."

# Also format code
terraform fmt -recursive

# Check if changes were made (shouldn't be many)
git diff --name-only  # If using git
```

Checklist:
- [ ] `terraform validate` passes
- [ ] No syntax errors
- [ ] `terraform fmt` run
- [ ] Code formatted correctly

### Step 6: Create Execution Plan
```bash
# Create plan (saves to file for safe review)
terraform plan -out=tfplan

# Check for errors
# Should see: "Plan: XX to add, 0 to change, 0 to destroy"
```

Checklist:
- [ ] Plan created successfully
- [ ] No validation errors
- [ ] Plan file saved (tfplan)
- [ ] Review output shows correct resources

### Step 7: Review Plan Carefully
```bash
# Show the plan
terraform show tfplan

# Look for:
# - Correct resource group name
# - Correct location
# - Correct VNet address space
# - Correct ASE type (ILB or External)
# - Correct SKU
# - All required resources present
```

Review Checklist:
- [ ] Resource Group name correct: **_____________**
- [ ] Location correct: **_____________**
- [ ] VNet address space correct: **_____________**
- [ ] ASE kind correct: **_____________**
- [ ] Web app name correct: **_____________**
- [ ] All resources tagged correctly
- [ ] No destructive changes (should be all additions)
- [ ] Counts match expectations (20+ resources)

Key Resources Expected:
- [ ] 1x Resource Group
- [ ] 1x Virtual Network
- [ ] 3x Subnets
- [ ] 1x Network Security Group
- [ ] 1x App Service Environment
- [ ] 1x App Service Plan
- [ ] 1x Web App (Windows or Linux)
- [ ] 1x Log Analytics Workspace
- [ ] 1x Application Insights
- [ ] 1x Key Vault
- [ ] 1x Storage Account
- [ ] 1x Private Endpoint
- [ ] 1x Private DNS Zone
- [ ] Other supporting resources

### Step 8: Get Final Approval
- [ ] DevOps lead reviewed plan
- [ ] Security team reviewed plan
- [ ] Infrastructure lead reviewed plan
- [ ] All approvals documented
- [ ] Scheduled deployment time confirmed
- [ ] Backup procedures in place
- [ ] Rollback plan documented

### Step 9: Execute Deployment
```bash
# Apply the plan
terraform apply tfplan

# Watch the output carefully
# Deployment should take 30-50 minutes
# DO NOT INTERRUPT - Ctrl+C during ASE creation can corrupt state

# Monitor progress:
# - May see "Still creating..."
# - This is normal for ASE
# - Wait patiently (30-45 minutes typical)
```

Checklist:
- [ ] `terraform apply` started successfully
- [ ] Watching output for errors
- [ ] Not interrupting deployment
- [ ] Noting creation times for each resource
- [ ] Monitoring for any warnings

Expected Timeline:
- [ ] First 2-3 minutes: Basic resources (RG, VNet)
- [ ] Next 30-45 minutes: ASE creation (LONG - be patient!)
- [ ] Next 3-5 minutes: App Service Plan, Web App
- [ ] Last 2-3 minutes: Monitoring, DNS, auto-scale

### Step 10: Verify Deployment Success
```bash
# After deployment completes
terraform output

# Should see all outputs with values
# Check for:
# - ase_name
# - web_app_name
# - web_app_identity
# - app_service_plan_name
# - application_insights_instrumentation_key

# Also check in Azure Portal:
az resource list --resource-group rg-webapp-prod --output table
```

Checklist:
- [ ] `terraform apply` completed with no errors
- [ ] Outputs displayed correctly
- [ ] All critical outputs populated (not empty)
- [ ] Can see resources in Azure Portal
- [ ] ASE status shows "Healthy" or similar
- [ ] Web App status shows "Running"

---

## Post-Deployment Verification

### 1. Azure Portal Verification
Navigate to Azure Portal and verify:
- [ ] Resource Group created: rg-**_______**-**______** 
- [ ] Virtual Network created and healthy
- [ ] ASE created and status = "Healthy"
- [ ] App Service Plan visible
- [ ] Web App created and status = "Running"
- [ ] Application Insights collecting data
- [ ] Key Vault created
- [ ] Storage Account created
- [ ] Network Security Groups configured
- [ ] Private Endpoints created
- [ ] Private DNS Zone created (if ILB)

### 2. Managed Identity Verification
```bash
# Get web app managed identity
terraform output web_app_identity

# Or from Azure CLI
az webapp identity show \
  --resource-group rg-webapp-prod \
  --name webapp-webapp-prod
```

Checklist:
- [ ] Managed Identity enabled
- [ ] Principal ID is not empty
- [ ] Type is "SystemAssigned"

### 3. Key Vault Verification
```bash
# Check Key Vault access
az keyvault show \
  --name "kvwebappprod" \
  --resource-group "rg-webapp-prod"

# Verify managed identity has access
az keyvault set-policy \
  --name "kvwebappprod" \
  --object-id "PRINCIPAL_ID_FROM_ABOVE" \
  --secret-permissions get list
```

Checklist:
- [ ] Key Vault exists
- [ ] Managed identity has permissions
- [ ] Can view vault properties

### 4. Network Verification
```bash
# Check Network Security Groups
az network nsg list --resource-group rg-webapp-prod

# Check NSG rules
az network nsg rule list \
  --resource-group rg-webapp-prod \
  --nsg-name nsg-ase-prod
```

Checklist:
- [ ] NSG created
- [ ] Inbound rules for HTTP/HTTPS present
- [ ] Outbound rules allow traffic

### 5. Monitoring Verification
```bash
# Check Application Insights
az monitor app-insights component show \
  --resource-group rg-webapp-prod \
  --app appinsights-webapp-prod

# Check Log Analytics
az monitor log-analytics workspace show \
  --resource-group rg-webapp-prod \
  --workspace-name law-webapp-prod
```

Checklist:
- [ ] Application Insights created
- [ ] Instrumentation key captured
- [ ] Log Analytics workspace created
- [ ] Diagnostic settings configured

### 6. Application Deployment Verification
```bash
# Get web app name
WEB_APP=$(terraform output -raw web_app_name)

# Deploy test application
az webapp deployment source config-zip \
  --resource-group rg-webapp-prod \
  --name $WEB_APP \
  --src test-app.war
```

Checklist:
- [ ] Application deployed successfully
- [ ] Web app responds to HTTP requests
- [ ] No 500 errors in logs
- [ ] Application Insights shows requests

### 7. DNS Verification (for ILB ASE)
```bash
# Get ILB internal IP
terraform output ase_internal_ip_address

# Test DNS resolution (from within VNet)
# nslookup webapp-webapp-prod.internal.company.com
# Should resolve to: <internal_ip>
```

Checklist:
- [ ] Private DNS zone created
- [ ] DNS records pointing to ILB IP
- [ ] DNS resolution works from VNet

### 8. Auto-Scale Verification
```bash
# Check auto-scale settings
az monitor autoscale setting list \
  --resource-group rg-webapp-prod
```

Checklist:
- [ ] Auto-scale configured
- [ ] Min instances set: 3
- [ ] Max instances set: 10 (or configured value)
- [ ] CPU threshold rules present

---

## First Week Operations

### Day 1: Monitoring & Alerting
- [ ] Check Application Insights for errors
- [ ] Verify logs flowing to Log Analytics
- [ ] Test alerting (send test email)
- [ ] Monitor ASE metrics
- [ ] Check cost projections in Cost Management

### Day 2-3: Load Testing
- [ ] Perform baseline load test
- [ ] Monitor performance metrics
- [ ] Check if auto-scaling triggers
- [ ] Document performance baselines
- [ ] Review and optimize configurations

### Day 4-5: Security Review
- [ ] Verify HTTPS enforced
- [ ] Check Managed Identity working
- [ ] Test Key Vault access
- [ ] Review NSG rules
- [ ] Enable Azure Defender if needed

### Day 6-7: Documentation & Handoff
- [ ] Complete operational runbooks
- [ ] Document custom settings
- [ ] Train operations team
- [ ] Document scaling procedures
- [ ] Create monitoring dashboard
- [ ] Prepare incident response procedures

---

## Rollback Procedures

If deployment needs to be rolled back:

```bash
# Option 1: Destroy via Terraform (recommended)
terraform destroy

# Option 2: Delete resource group (faster but less controlled)
az group delete --name rg-webapp-prod

# Option 3: Manual deletion in Azure Portal
# (least preferred - may leave orphaned resources)
```

Rollback Checklist:
- [ ] Have recent backup of application
- [ ] Have previous configuration saved
- [ ] Notified all teams before rollback
- [ ] Have contingency plan (previous infrastructure)
- [ ] Restoration process documented

---

## Success Criteria

Deployment is successful if:

- [ ] All 20+ resources created without errors
- [ ] No failed deployments shown in Portal
- [ ] ASE status is "Healthy"
- [ ] Web App status is "Running"
- [ ] Application Insights collecting data
- [ ] No critical alerts firing
- [ ] Application deployed and responding
- [ ] Monitoring dashboards accessible
- [ ] Team trained on new infrastructure
- [ ] Documentation complete
- [ ] Backup procedures tested
- [ ] Disaster recovery plan validated

---

## Sign-Off

### Deployment Completed Successfully

- [ ] Date: **_____________**
- [ ] Time: **_____________**
- [ ] Deployed By: **_____________**
- [ ] Reviewed By: **_____________**
- [ ] Approved By: **_____________**

### Issues Encountered & Resolutions

Issue 1: **_____________**
Resolution: **_____________**

Issue 2: **_____________**
Resolution: **_____________**

### Notes & Observations

**_____________**

---

## Maintenance Schedule

### Weekly
- [ ] Review Application Insights metrics
- [ ] Check for any error spikes
- [ ] Verify backups completed

### Monthly
- [ ] Cost review and optimization
- [ ] Security update checks
- [ ] Capacity planning review
- [ ] Update monitoring alerts as needed

### Quarterly
- [ ] Full disaster recovery test
- [ ] Performance optimization review
- [ ] Architecture review meeting
- [ ] Compliance audit

---

**Print this checklist and keep it for reference during deployment!**

For questions, refer to:
- `README.md` - Overview
- `DEPLOYMENT_GUIDE.md` - Detailed steps
- `QUICK-REFERENCE.md` - Command reference
