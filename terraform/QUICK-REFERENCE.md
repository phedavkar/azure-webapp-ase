# Terraform Module - Quick Reference Card

## What This Does
Creates a complete Azure Web App Service infrastructure with App Service Environment (ASE v3) using Terraform.

## Files You Need

| File | Purpose |
|------|---------|
| `variables.tf` | Variable definitions (do not edit) |
| `main.tf` | Provider & outputs (do not edit) |
| `resources.tf` | Resource definitions (do not edit) |
| `terraform.tfvars.example` | Example config ← COPY THIS |
| `terraform.tfvars` | Your config ← EDIT THIS |
| `README.md` | Full documentation |
| `DEPLOYMENT_GUIDE.md` | Step-by-step instructions |

## 3-Step Deployment

```bash
# STEP 1: Copy & Customize
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Edit these values:
# - subscription_id
# - tenant_id
# - client_id
# - client_secret

# STEP 2: Deploy
terraform init
terraform plan -out=tfplan

# STEP 3: Apply
terraform apply tfplan
```

## Essential Variables

```hcl
# MUST SET
subscription_id = "xxxxx-xxxxx"
tenant_id       = "xxxxx-xxxxx"
client_id       = "xxxxx-xxxxx"
client_secret   = "xxxxx-xxxxx"

# SHOULD SET
project_name        = "webapp"
environment         = "prod"
location            = "eastus"

# OPTIONAL (good defaults)
ase_kind                      = "ILBASEv3"  # or ASEv3
app_service_plan_sku          = "I1V2"
app_service_plan_worker_count = 3
web_app_runtime_stack         = "TOMCAT|10.0"
```

## What Gets Created

```
Resource Group
├── Virtual Network (10.3.0.0/16)
│   ├── ASE Subnet (10.3.1.0/24)
│   │   └── App Service Environment
│   │       └── App Service Plan
│   │           └── Web App
│   ├── Private Endpoints Subnet
│   └── Network Security Groups
├── Key Vault (secrets)
├── Storage Account (backups)
├── Log Analytics (logging)
├── Application Insights (monitoring)
├── Private DNS Zone
└── Auto-scale Settings
```

## Runtime Stacks

```hcl
# Tomcat
web_app_runtime_stack = "TOMCAT|10.0"
app_service_plan_is_linux = true

# .NET
web_app_runtime_stack = "DOTNET|6.0"
app_service_plan_is_linux = false

# Node.js
web_app_runtime_stack = "NODE|18-lts"
app_service_plan_is_linux = true

# Python
web_app_runtime_stack = "PYTHON|3.11"
app_service_plan_is_linux = true
```

## ASE Types

| Type | Internal IP | Recommended For |
|------|-------------|-----------------|
| **ILBASEv3** | Private | Hub-spoke, private-only |
| **ASEv3** | Public | Public-facing apps |

## SKUs

| SKU | vCPU | RAM | Monthly Cost |
|-----|------|-----|--------------|
| I1V2 | 1 | 3.5GB | ~$75 |
| I2V2 | 2 | 7GB | ~$150 |
| I3V2 | 4 | 14GB | ~$300 |

## Deployment Time

- **Total**: 30-50 minutes
- **ASE creation**: 30-45 minutes
- **Other resources**: 5-10 minutes

## Post-Deployment

```bash
# View what was created
terraform output

# Deploy your app
WEB_APP=$(terraform output -raw web_app_name)
az webapp deployment source config-zip \
  --resource-group rg-webapp-prod \
  --name $WEB_APP \
  --src app.war

# Check monitoring
# → Azure Portal → Application Insights
```

## Common Commands

```bash
terraform init              # Initialize
terraform validate          # Check syntax
terraform plan             # Preview changes
terraform apply            # Deploy (confirm with 'yes')
terraform output           # View outputs
terraform destroy          # Delete everything
terraform show             # Show state details
terraform fmt              # Format code
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Error acquiring state lock" | Wait for previous op to finish |
| "Invalid credentials" | Check service principal in terraform.tfvars |
| "Insufficient capacity" | Wait or try different region |
| "Validation failed" | Run `terraform validate` |
| "Private endpoint failed" | Ensure subnet is /24 or larger |

## Documentation

| File | Read It For |
|------|-------------|
| `00-START-HERE.md` | Overview (5 min read) |
| `README.md` | Features & architecture (15 min) |
| `DEPLOYMENT_GUIDE.md` | Step-by-step (30 min) |
| `variables.tf` | Variable reference (detailed) |

## Cost Estimate

| Component | Monthly |
|-----------|---------|
| ASE | $220 |
| App Services | Included |
| Monitoring | $10-50 |
| Storage | $10-20 |
| **Total** | **$240-290** |

## Security Checklist

- [ ] HTTPS only enabled
- [ ] Managed Identity configured
- [ ] Key Vault with secrets
- [ ] Private Endpoints setup
- [ ] Network Security Groups active
- [ ] RBAC configured
- [ ] Monitoring enabled

## Important Notes

1. **Don't commit terraform.tfvars** - It has secrets
2. **ILB ASE is private** - No public access needed for hub-spoke
3. **Deployment is slow** - ASE takes 30+ minutes, normal behavior
4. **Costs are real** - Baseline costs even with 0 instances
5. **Test in dev first** - Before production deployment
6. **Keep backups** - Enable automatic backups
7. **Monitor carefully** - Check logs from day 1

## Quick Customization Examples

### Add Database Connection
```hcl
web_app_connection_strings = {
  "DefaultConnection" = {
    value = "Server=mydb.database.windows.net;..."
    type = "SQLAzure"
  }
}
```

### Set Java Options
```hcl
web_app_app_settings = {
  "JAVA_OPTS" = "-Xmx2g -Xms1g"
}
```

### Enable Debug Logging
```hcl
web_app_app_settings = {
  "LOG_LEVEL" = "DEBUG"
}
```

## Getting Help

**Before Asking:**
1. Read README.md
2. Check DEPLOYMENT_GUIDE.md troubleshooting
3. Run `terraform validate`
4. Check Azure Portal

**Resources:**
- Terraform: https://www.terraform.io/docs
- Azure Provider: https://registry.terraform.io/providers/hashicorp/azurerm/latest
- Azure ASE: https://learn.microsoft.com/azure/app-service/environment/

## Success Checklist

- [ ] terraform.tfvars created with credentials
- [ ] `terraform validate` passes
- [ ] `terraform plan` looks correct
- [ ] Deployment completes (30-50 min)
- [ ] `terraform output` shows resources
- [ ] Azure Portal shows ASE, App Service, Web App
- [ ] Application deployed successfully
- [ ] Monitoring shows data in Application Insights

## Next Steps

1. Copy `terraform.tfvars.example` to `terraform.tfvars`
2. Edit with your Azure credentials
3. Run `terraform init`
4. Run `terraform plan` to review
5. Run `terraform apply` to deploy
6. View results with `terraform output`
7. Deploy your application
8. Monitor in Azure Portal

---

## File Locations

```
/terraform/
├── 00-START-HERE.md          ← You are here
├── QUICK-REFERENCE.md        ← This file
├── README.md                 ← Full guide
├── DEPLOYMENT_GUIDE.md       ← Step-by-step
├── INDEX.md                  ← File index
├── SUMMARY.md                ← Technical summary
├── main.tf                   ← Don't edit
├── variables.tf              ← Don't edit
├── resources.tf              ← Don't edit
├── terraform.tfvars.example  ← Copy this
├── terraform.tfvars          ← Edit this (you create it)
└── .gitignore                ← Add to git
```

---

**Ready?** → `cp terraform.tfvars.example terraform.tfvars` → Edit → `terraform apply`

**Confused?** → Read `README.md` → Read `DEPLOYMENT_GUIDE.md` → Try again
