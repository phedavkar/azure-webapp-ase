# Azure Web App Deployment in App Service Environment (ASE)
## Complete Implementation Guide

---

## Table of Contents
1. [ASE Architecture Overview](#ase-architecture-overview)
2. [ASE Types and Comparison](#ase-types-and-comparison)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Step-by-Step ASE Deployment](#step-by-step-ase-deployment)
5. [App Service Plan Creation](#app-service-plan-creation)
6. [Web App Deployment](#web-app-deployment)
7. [Networking Configuration](#networking-configuration)
8. [Security Configuration](#security-configuration)
9. [Monitoring and Diagnostics](#monitoring-and-diagnostics)
10. [Scaling and Performance](#scaling-and-performance)
11. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
12. [Cost Optimization](#cost-optimization)
13. [Troubleshooting](#troubleshooting)

---

## ASE Architecture Overview

### What is App Service Environment (ASE)?

An **App Service Environment (ASE)** is a fully isolated and dedicated environment for running Azure App Service apps at high scale. It provides:

- **Dedicated infrastructure**: Your own isolated deployment stamp
- **Complete isolation**: No multi-tenancy with other customers
- **High-capacity hosting**: Can host thousands of applications
- **Enterprise-grade security**: Enhanced network isolation and control
- **Compliance**: Meets stringent regulatory and compliance requirements

### ASE Deployment Models

#### 1. **External ASE** (Most Common)
```
Internet
  ↓
Public IP / Application Gateway
  ↓
External ASE (Public endpoint)
  ↓
App Service Plans & Apps
```
- Apps have public IP addresses
- Can accept inbound traffic from internet
- Good for public-facing applications
- Can also use Private Endpoints for private access

#### 2. **Internal Load Balancer (ILB) ASE**
```
On-Premises / VPN / ExpressRoute
  ↓
Hub VNet / ExpressRoute
  ↓
Spoke VNet
  ↓
ILB ASE (Private IP only)
  ↓
App Service Plans & Apps (No public IPs)
```
- Apps have only internal private IPs
- No public internet access to apps
- Requires VPN, ExpressRoute, or peering for access
- Perfect for your hub-spoke topology
- **Recommended for your scenario**

---

## ASE Types and Comparison

### ASEv3 (Current - Recommended)

| Aspect | ASEv3 |
|--------|-------|
| **Release Date** | 2021 (Latest) |
| **Infrastructure** | Premium isolated compute |
| **Min Instances** | 0 (new feature - can scale to 0) |
| **Max Scale** | 201 instances |
| **Pricing Model** | Per-instance pricing |
| **VNet Requirement** | /24 subnet minimum |
| **Base Fee** | No longer required to pay for unused capacity |
| **Patching** | Microsoft managed |
| **Availability Zones** | Supported |
| **ARM Template** | Fully supported |
| **Status** | ✅ Current & Supported |

### ASEv2 (Legacy)

| Aspect | ASEv2 |
|--------|-------|
| **Release Date** | 2016 |
| **Infrastructure** | Standard isolated compute |
| **Min Instances** | 1 (always pay minimum) |
| **Max Scale** | 55 instances |
| **Pricing Model** | Stamp fee + per-instance |
| **VNet Requirement** | /24 subnet minimum |
| **Base Fee** | $0.25-0.50/hour (always charged) |
| **Patching** | Customer/Microsoft shared |
| **Availability Zones** | Not supported |
| **Deprecation** | Planned for 2026 |
| **Status** | ⚠️ Legacy - Plan to migrate |

### ASEv1 (Deprecated)

| Aspect | ASEv1 |
|--------|-------|
| **Release Date** | 2014 |
| **Status** | ❌ Retired (Support ended) |
| **Action** | **MUST migrate** |

---

## Pre-Deployment Checklist

### Planning Phase
- [ ] Determine ASE type (External vs ILB)
- [ ] Choose ASEv3 (do NOT use ASEv2)
- [ ] Plan VNet and subnet requirements
- [ ] Determine availability zone requirements
- [ ] Plan capacity (number of instances needed)
- [ ] Identify hybrid connectivity needs (ExpressRoute, VPN)
- [ ] Document compliance requirements
- [ ] Plan for disaster recovery and backups

### Networking Phase
- [ ] Virtual Network created (with sufficient address space)
- [ ] Dedicated subnet for ASE (/24 minimum recommended)
- [ ] Network Security Groups (NSGs) planned
- [ ] For ILB ASE: Plan internal IP address
- [ ] Private DNS zones designed
- [ ] Private Endpoints strategy (if using)
- [ ] ExpressRoute/VPN connectivity configured (if needed)

### Security Phase
- [ ] Azure Entra ID (Azure AD) authentication configured
- [ ] Key Vault created for secrets
- [ ] Managed Identity strategy planned
- [ ] RBAC roles defined
- [ ] Network security groups drafted
- [ ] WAF (Web Application Firewall) requirements identified
- [ ] DDoS protection evaluated

### Infrastructure Phase
- [ ] Resource Group created
- [ ] Cost center/billing tags defined
- [ ] Naming conventions established
- [ ] Log Analytics workspace created
- [ ] Application Insights created
- [ ] Storage account for diagnostics created
- [ ] Azure backup vaults planned

### Application Phase
- [ ] Application runtime identified (Java, .NET, Node.js, Python, PHP, etc.)
- [ ] Dependencies documented
- [ ] Configuration externalized (no hardcoding)
- [ ] Docker image prepared (if containerized)
- [ ] Container registry (ACR) set up
- [ ] Health check endpoint defined
- [ ] Startup/shutdown scripts prepared

---

## Step-by-Step ASE Deployment

### Step 1: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="rg-ase-prod"
LOCATION="eastus"
ASE_NAME="ase-prod-001"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --tags "environment=production" "billing-center=IT"
```

### Step 2: Create Virtual Network and Subnet

```bash
# Set variables
VNET_NAME="vnet-ase-prod"
VNET_ADDRESS_SPACE="10.3.0.0/16"
ASE_SUBNET_NAME="subnet-ase"
ASE_SUBNET_ADDRESS="10.3.1.0/24"
PRIVATE_ENDPOINTS_SUBNET="10.3.2.0/24"

# Create Virtual Network
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix $VNET_ADDRESS_SPACE \
  --location $LOCATION

# Create ASE Subnet
az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $ASE_SUBNET_NAME \
  --address-prefix $ASE_SUBNET_ADDRESS \
  --service-endpoints "Microsoft.KeyVault" "Microsoft.Sql" "Microsoft.Storage"

# Create Private Endpoints Subnet
az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name "subnet-private-endpoints" \
  --address-prefix $PRIVATE_ENDPOINTS_SUBNET
```

### Step 3: Configure Network Security Group (NSG)

```bash
# Create NSG for ASE Subnet
az network nsg create \
  --resource-group $RESOURCE_GROUP \
  --name "nsg-ase" \
  --location $LOCATION

# Allow inbound from Application Gateway (for external ASE)
# Or from hub VNet (for ILB ASE)
az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "nsg-ase" \
  --name "Allow-HTTP" \
  --priority 100 \
  --direction Inbound \
  --source-address-prefixes "10.0.0.0/8" \
  --protocol Tcp \
  --destination-port-ranges 80 \
  --access Allow

az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "nsg-ase" \
  --name "Allow-HTTPS" \
  --priority 110 \
  --direction Inbound \
  --source-address-prefixes "10.0.0.0/8" \
  --protocol Tcp \
  --destination-port-ranges 443 \
  --access Allow

# Allow outbound to all (default)
# Restrict as needed based on your security requirements

# Associate NSG with ASE subnet
az network vnet subnet update \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $ASE_SUBNET_NAME \
  --network-security-group "nsg-ase"
```

### Step 4: Create App Service Environment (ASEv3)

#### Option A: ILB ASE (Recommended for Hub-Spoke)

```bash
# Create ILB ASE
az appservice ase create \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --subnet-name $ASE_SUBNET_NAME \
  --kind "ILBASEv3" \
  --location $LOCATION \
  --zonecount 3 \
  --frontendcount 3 \
  --debug
```

#### Option B: External ASE

```bash
# Create External ASE
az appservice ase create \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --subnet-name $ASE_SUBNET_NAME \
  --kind "ASEv3" \
  --location $LOCATION \
  --zonecount 3 \
  --frontendcount 3 \
  --debug
```

**Parameters Explained:**
- `--zonecount`: Number of availability zones (1, 2, or 3) - use 3 for HA
- `--frontendcount`: Number of front-end instances (minimum 1, recommended 3)
- `--kind`: ASEv3 (external) or ILBASEv3 (internal load balancer)

### Step 5: Verify ASE Creation

```bash
# Get ASE details
az appservice ase show \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP

# List ASE resources
az appservice ase list \
  --resource-group $RESOURCE_GROUP

# Get ASE configuration
az appservice ase list-addresses \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP

# For ILB ASE, note the internal IP address assigned
```

### Step 6: Configure VNet Peering (for hub-spoke topology)

```bash
# Peer spoke VNet with hub VNet
az network vnet peering create \
  --name "peer-spoke-to-hub" \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --remote-group "rg-hub" \
  --remote-vnet "vnet-hub" \
  --allow-vnet-access true \
  --allow-forwarded-traffic true \
  --use-remote-gateways true

# Create reverse peering from hub
az network vnet peering create \
  --name "peer-hub-to-spoke" \
  --resource-group "rg-hub" \
  --vnet-name "vnet-hub" \
  --remote-group $RESOURCE_GROUP \
  --remote-vnet $VNET_NAME \
  --allow-vnet-access true \
  --allow-forwarded-traffic true \
  --allow-gateway-transit true
```

---

## App Service Plan Creation

### Step 7: Create App Service Plan in ASE

```bash
# Set variables
APP_SERVICE_PLAN_NAME="asp-ase-prod-001"
SKU="I1V2"  # ILBv2, can be I1V2, I2V2, I3V2

# Create App Service Plan in ASE
az appservice plan create \
  --name $APP_SERVICE_PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --ase $ASE_NAME \
  --sku $SKU \
  --is-linux false \
  --number-of-workers 3

# Verify Plan
az appservice plan show \
  --name $APP_SERVICE_PLAN_NAME \
  --resource-group $RESOURCE_GROUP
```

**SKU Options for ASEv3:**
- `I1V2`: 1 core, 3.5 GB RAM (recommended starting point)
- `I2V2`: 2 cores, 7 GB RAM (for medium workloads)
- `I3V2`: 4 cores, 14 GB RAM (for high-performance workloads)

### Step 8: Scale App Service Plan

```bash
# Scale to specific number of workers
az appservice plan update \
  --name $APP_SERVICE_PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --number-of-workers 5

# Or scale programmatically based on metrics
# Use auto-scale rules (see Scaling section below)
```

---

## Web App Deployment

### Step 9: Create Web App in App Service Plan

```bash
# Set variables
WEB_APP_NAME="webapp-tomcat-prod-001"
RUNTIME="TOMCAT|10.0"  # For Java/Tomcat

# Create Web App (Linux)
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN_NAME \
  --name $WEB_APP_NAME \
  --runtime "$RUNTIME"

# Or for Windows/.NET
# az webapp create \
#   --resource-group $RESOURCE_GROUP \
#   --plan $APP_SERVICE_PLAN_NAME \
#   --name $WEB_APP_NAME \
#   --runtime "DOTNET|6.0"

# Or for Docker container
# az webapp create \
#   --resource-group $RESOURCE_GROUP \
#   --plan $APP_SERVICE_PLAN_NAME \
#   --name $WEB_APP_NAME \
#   --deployment-container-image-name-user YOUR_REGISTRY.azurecr.io/YOUR_IMAGE:TAG
```

### Step 10: Configure Web App Settings

```bash
# Enable Managed Identity
az webapp identity assign \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --identities "[system]"

# Get Managed Identity Object ID
IDENTITY_ID=$(az webapp identity show \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --query principalId \
  --output tsv)

echo "Managed Identity Object ID: $IDENTITY_ID"

# Configure application settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    "JAVA_OPTS=-Dcom.sun.jndi.ldap.connect.pool=true" \
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE=false" \
    "ENVIRONMENT=production" \
    "LOG_LEVEL=INFO"

# Configure connection strings (non-sensitive, or use Key Vault reference)
az webapp config connection-string set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --connection-string-type "SQLAzure" \
  --settings "DefaultConnection=Server=tcp:myserver.database.windows.net,1433;Initial Catalog=mydb;Persist Security Info=False;User ID=myuser;Password=mypassword;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
```

### Step 11: Deploy Application

#### Option A: Deploy WAR File

```bash
# For Java/Tomcat applications
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --src "path/to/application.war"

# Or for built binaries
az webapp up \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --runtime "TOMCAT|10.0|Java|11"
```

#### Option B: Deploy from Git

```bash
# Configure Git deployment
az webapp deployment source config-local-git \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME

# Set Git credentials
az webapp deployment user set \
  --user-name "yourdeploymentuser" \
  --password "yourpassword"

# Git commands
git remote add azure [git_url_from_above]
git push azure main
```

#### Option C: Deploy Docker Container

```bash
# Configure container registry
az webapp config container set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name "YOUR_REGISTRY.azurecr.io/your-app:latest" \
  --docker-registry-server-url "https://YOUR_REGISTRY.azurecr.io"

# Configure registry credentials
az webapp config container set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name "YOUR_REGISTRY.azurecr.io/your-app:latest" \
  --docker-registry-server-url "https://YOUR_REGISTRY.azurecr.io" \
  --docker-registry-server-user "username" \
  --docker-registry-server-password "password"
```

#### Option D: Deploy using Managed Identity (Recommended)

```bash
# Push image to ACR with managed identity
az acr build \
  --registry YOUR_REGISTRY \
  --image your-app:latest \
  --file Dockerfile .

# Configure ACR pull with managed identity
az role assignment create \
  --assignee $IDENTITY_ID \
  --role "AcrPull" \
  --scope "/subscriptions/SUBSCRIPTION_ID/resourceGroups/REGISTRY_RG/providers/Microsoft.ContainerRegistry/registries/YOUR_REGISTRY"
```

### Step 12: Verify Deployment

```bash
# Get app status
az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME

# Get deployment history
az webapp deployment list \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME

# Check default hostname (for External ASE)
# or internal IP (for ILB ASE)
az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --query "defaultHostName" \
  --output tsv
```

---

## Networking Configuration

### Step 13: Configure Regional VNet Integration

```bash
# For additional outbound traffic control
az webapp vnet-integration add \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --vnet $VNET_NAME \
  --subnet $ASE_SUBNET_NAME

# Note: Apps in ASE are already integrated
# This is for additional control if needed
```

### Step 14: Configure Private Endpoints (if needed)

```bash
# Create private endpoint for web app
az network private-endpoint create \
  --name "pe-webapp" \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --subnet "subnet-private-endpoints" \
  --private-connection-resource-id "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --group-ids "sites" \
  --connection-name "webapp-connection"

# Create private DNS zone
az network private-dns zone create \
  --resource-group $RESOURCE_GROUP \
  --name "privatelink.azurewebsites.net"

# Link private DNS zone to VNet
az network private-dns link vnet create \
  --resource-group $RESOURCE_GROUP \
  --zone-name "privatelink.azurewebsites.net" \
  --name "vnet-link" \
  --virtual-network $VNET_NAME \
  --registration-enabled false

# Create DNS record
az network private-dns record-set a create \
  --resource-group $RESOURCE_GROUP \
  --zone-name "privatelink.azurewebsites.net" \
  --name $WEB_APP_NAME

az network private-dns record-set a add-record \
  --resource-group $RESOURCE_GROUP \
  --zone-name "privatelink.azurewebsites.net" \
  --record-set-name $WEB_APP_NAME \
  --ipv4-address "10.3.2.10"  # Private IP of the endpoint
```

### Step 15: Configure DNS (for ILB ASE)

For ILB ASE, apps are not publicly accessible. Configure internal DNS:

```bash
# Create private DNS zone for internal apps
az network private-dns zone create \
  --resource-group $RESOURCE_GROUP \
  --name "internal.company.com"

# Link to all VNets (hub and spokes)
az network private-dns link vnet create \
  --resource-group $RESOURCE_GROUP \
  --zone-name "internal.company.com" \
  --name "hub-link" \
  --virtual-network "/subscriptions/SUBSCRIPTION_ID/resourceGroups/rg-hub/providers/Microsoft.Network/virtualNetworks/vnet-hub" \
  --registration-enabled false

# Create A record pointing to ILB internal IP
ILB_IP=$(az appservice ase show \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "internalIpAddress" \
  --output tsv)

az network private-dns record-set a create \
  --resource-group $RESOURCE_GROUP \
  --zone-name "internal.company.com" \
  --name "app1"

az network private-dns record-set a add-record \
  --resource-group $RESOURCE_GROUP \
  --zone-name "internal.company.com" \
  --record-set-name "app1" \
  --ipv4-address $ILB_IP
```

---

## Security Configuration

### Step 16: Configure HTTPS/TLS

```bash
# Import certificate to App Service (from Key Vault or local)
az webapp config ssl upload \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --certificate-file "path/to/certificate.pfx" \
  --certificate-password "password"

# Create binding for HTTPS
az webapp config ssl bind \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --certificate-thumbprint "THUMBPRINT" \
  --ssl-type "SNI"

# Or use App Service managed certificate
az webapp config ssl create \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --certificate-name "default"
```

### Step 17: Enable HTTPS Only

```bash
# Redirect HTTP to HTTPS
az webapp update \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --https-only true
```

### Step 18: Configure Authentication with Azure Entra ID

```bash
# Enable Azure Entra ID authentication
az webapp auth update \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --enabled true \
  --action LoginWithAzureIdentity \
  --aad-allowed-token-audiences "https://$WEB_APP_NAME.azurewebsites.net" \
  --aad-client-id "YOUR_APP_ID" \
  --aad-client-secret "YOUR_CLIENT_SECRET" \
  --aad-tenant "https://login.microsoftonline.com/YOUR_TENANT_ID"
```

### Step 19: Configure Key Vault References

```bash
# Grant managed identity access to Key Vault
az keyvault set-policy \
  --name "kv-prod" \
  --object-id $IDENTITY_ID \
  --secret-permissions get list \
  --certificate-permissions get list

# Use Key Vault references in app settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    "DatabasePassword=@Microsoft.KeyVault(SecretUri=https://kv-prod.vault.azure.net/secrets/db-password/)" \
    "ApiKey=@Microsoft.KeyVault(SecretUri=https://kv-prod.vault.azure.net/secrets/api-key/)"
```

### Step 20: Enable Web Application Firewall (WAF)

If using External ASE with Application Gateway:

```bash
# WAF is configured at Application Gateway level, not ASE
# Create Application Gateway with WAF
az network application-gateway create \
  --resource-group $RESOURCE_GROUP \
  --name "appgw-prod" \
  --location $LOCATION \
  --vnet-name $VNET_NAME \
  --subnet "subnet-appgw" \
  --capacity 2 \
  --sku WAF_v2 \
  --http-settings-cookie-based-affinity Enabled \
  --public-ip-address-allocation Static \
  --public-ip-address "pip-appgw"

# Configure WAF policies
az network application-gateway waf-config set \
  --resource-group $RESOURCE_GROUP \
  --gateway-name "appgw-prod" \
  --enabled true \
  --firewall-mode Detection
```

---

## Monitoring and Diagnostics

### Step 21: Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --resource-group $RESOURCE_GROUP \
  --application-type "web" \
  --app "appinsights-prod" \
  --location $LOCATION \
  --kind "web"

# Get Instrumentation Key
IKEY=$(az monitor app-insights component show \
  --resource-group $RESOURCE_GROUP \
  --app "appinsights-prod" \
  --query "instrumentationKey" \
  --output tsv)

# Configure app to use Application Insights
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    "APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$IKEY" \
    "APPLICATIONINSIGHTS_ENABLE_AGENT=true"
```

### Step 22: Configure Diagnostic Settings

```bash
# Send logs to Log Analytics
az monitor diagnostic-settings create \
  --resource-group $RESOURCE_GROUP \
  --name "diag-webapp" \
  --resource "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --logs '[
    {
      "category": "AppServiceHTTPLogs",
      "enabled": true,
      "retentionPolicy": {
        "enabled": true,
        "days": 30
      }
    },
    {
      "category": "AppServiceConsoleLogs",
      "enabled": true,
      "retentionPolicy": {
        "enabled": true,
        "days": 7
      }
    }
  ]' \
  --workspace "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.operationalinsights/workspaces/law-prod"
```

### Step 23: Set Up Alerts

```bash
# Create action group for notifications
az monitor action-group create \
  --resource-group $RESOURCE_GROUP \
  --name "ag-prod-notifications" \
  --short-name "ag-prod"

# Add email notification
az monitor action-group update \
  --resource-group $RESOURCE_GROUP \
  --name "ag-prod-notifications" \
  --add-action email email-alert --email-address "devops@company.com"

# Create metric alert for high CPU
az monitor metrics alert create \
  --resource-group $RESOURCE_GROUP \
  --name "alert-high-cpu" \
  --description "Alert when app CPU > 80%" \
  --scopes "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --condition "avg CpuPercentage > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/actionGroups/ag-prod-notifications"

# Create metric alert for high memory
az monitor metrics alert create \
  --resource-group $RESOURCE_GROUP \
  --name "alert-high-memory" \
  --description "Alert when app memory > 80%" \
  --scopes "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --condition "avg MemoryPercentage > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/actionGroups/ag-prod-notifications"

# Create alert for failed requests
az monitor metrics alert create \
  --resource-group $RESOURCE_GROUP \
  --name "alert-failed-requests" \
  --description "Alert when failed request rate > 5%" \
  --scopes "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --condition "total Http5xx > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/actionGroups/ag-prod-notifications"
```

---

## Scaling and Performance

### Step 24: Configure Auto-Scale Rules

```bash
# Create auto-scale settings
az monitor autoscale create \
  --resource-group $RESOURCE_GROUP \
  --resource $APP_SERVICE_PLAN_NAME \
  --resource-type "Microsoft.Web/serverfarms" \
  --name "autoscale-asp-prod" \
  --min-count 3 \
  --max-count 10 \
  --count 3

# Add scale-out rule (CPU > 70%)
az monitor autoscale rule create \
  --resource-group $RESOURCE_GROUP \
  --autoscale-name "autoscale-asp-prod" \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Add scale-in rule (CPU < 30%)
az monitor autoscale rule create \
  --resource-group $RESOURCE_GROUP \
  --autoscale-name "autoscale-asp-prod" \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

### Step 25: Performance Tuning

```bash
# Enable HTTP/2
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --http20-enabled true

# Configure general settings
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --always-on true \
  --use-32bit-worker-process false \
  --managed-pipeline-mode "Integrated" \
  --php-version "OFF" \
  --python-version "OFF"

# Configure platform settings for Java
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --always-on true \
  --use-32bit-worker-process false

# Configure connection pooling
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings \
    "TOMCAT_CONN_MAX_CONNECTIONS=1000" \
    "TOMCAT_CONN_MAX_IDLE_TIME=30000"
```

---

## Backup and Disaster Recovery

### Step 26: Configure Backups

```bash
# Enable automated backups
az webapp config backup update \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --storage-account-url "https://mystorageaccount.blob.core.windows.net/backups?sv=2021-01-01&st=..." \
  --backup-schedule-frequency "Daily" \
  --backup-schedule-start-hour 2

# Configure backup retention
az webapp config backup update \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --backup-schedule-keep-at-least 7

# Create manual backup
az webapp backup create \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME
```

### Step 27: Configure Disaster Recovery

```bash
# For multi-region HA, create traffic manager
az network traffic-manager profile create \
  --resource-group $RESOURCE_GROUP \
  --name "tm-prod" \
  --routing-method "Performance" \
  --path "/" \
  --protocol "HTTPS" \
  --port 443 \
  --unique-dns-name "tm-prod"

# Add primary endpoint
az network traffic-manager endpoint create \
  --name "endpoint-primary" \
  --profile-name "tm-prod" \
  --resource-group $RESOURCE_GROUP \
  --type "azureEndpoints" \
  --target "$WEB_APP_NAME.azurewebsites.net"

# Add secondary endpoint (in different region)
az network traffic-manager endpoint create \
  --name "endpoint-secondary" \
  --profile-name "tm-prod" \
  --resource-group $RESOURCE_GROUP \
  --type "azureEndpoints" \
  --target "webapp-secondary.azurewebsites.net"
```

---

## Cost Optimization

### Step 28: Right-Size Your ASE

```bash
# Monitor actual usage
az monitor metrics list \
  --resource "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/serverfarms/$APP_SERVICE_PLAN_NAME" \
  --metric "PercentageCPU" \
  --start-time "2024-01-01T00:00:00Z" \
  --interval PT1H \
  --aggregation Average

# Adjust based on actual usage
# Don't over-provision - ASE costs accumulate
```

### Step 29: Optimize Licensing

```bash
# If you have SQL Server licenses, use BYOL
# Configure in Azure Hybrid Benefit during deployment

# Monitor cost
az costmanagement query \
  --timeframe "MonthToDate" \
  --type "Usage" \
  --dataset \
    '{
      "granularity": "Daily",
      "aggregation": {
        "totalCost": {
          "name": "PreTaxCost",
          "function": "Sum"
        }
      },
      "filter": {
        "dimensions": {
          "name": "ResourceGroup",
          "operator": "In",
          "values": ["rg-ase-prod"]
        }
      }
    }'
```

---

## Troubleshooting

### Common ASE Issues and Solutions

#### Issue 1: Deployment Fails - "Insufficient Capacity"

**Cause**: ASE has hit resource limits
**Solution**:
```bash
# Check ASE capacity
az appservice ase show \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP

# Scale ASE if needed
az appservice ase update \
  --name $ASE_NAME \
  --resource-group $RESOURCE_GROUP \
  --number-of-workers 5

# Or upgrade worker SKU
```

#### Issue 2: Application Timeout - "502 Bad Gateway"

**Cause**: Backend is slow or unresponsive
**Solution**:
```bash
# Check application health
curl -v "http://webapp-internal-ip:8080/health"

# Increase timeout in app settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings "WEBSITE_LOAD_USER_PROFILE=1"

# Check logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME
```

#### Issue 3: High Memory Usage - "OutOfMemory Exception"

**Cause**: Application memory leak or insufficient heap
**Solution**:
```bash
# Increase app tier
az appservice plan update \
  --name $APP_SERVICE_PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku "I2V2"  # Larger instance

# Configure Java heap settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --settings "JAVA_OPTS=-Xmx2g -Xms1g"

# Analyze memory dumps
az webapp log show \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --provider filesystem
```

#### Issue 4: DNS Resolution Issues (ILB ASE)

**Cause**: Private DNS zone not linked or misconfigured
**Solution**:
```bash
# Verify private DNS zone is linked to all VNets
az network private-dns link vnet list \
  --resource-group $RESOURCE_GROUP \
  --zone-name "internal.company.com"

# Test DNS resolution from VM in VNet
# From within VNet:
# nslookup app1.internal.company.com
# Should resolve to ILB internal IP

# Add missing VNet link if needed
az network private-dns link vnet create \
  --resource-group $RESOURCE_GROUP \
  --zone-name "internal.company.com" \
  --name "spoke-link" \
  --virtual-network "/subscriptions/SUBSCRIPTION_ID/resourceGroups/rg-spoke/providers/Microsoft.Network/virtualNetworks/vnet-spoke"
```

#### Issue 5: Cannot Connect via ExpressRoute

**Cause**: ExpressRoute routing not properly configured
**Solution**:
```bash
# Verify ExpressRoute route table
az network route-table list \
  --resource-group $RESOURCE_GROUP

# Add route for on-premises via ExpressRoute
az network route-table route create \
  --resource-group $RESOURCE_GROUP \
  --route-table-name "rt-ase" \
  --name "route-onprem" \
  --address-prefix "192.168.0.0/16" \
  --next-hop-type "VirtualNetworkGateway"

# Verify NSG rules allow traffic from on-premises
az network nsg rule list \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "nsg-ase"
```

### Useful Diagnostic Commands

```bash
# Get diagnostic information
az webapp log download \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME \
  --log-file "app-diagnostics.zip"

# Stream live logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP_NAME

# Get detailed metrics
az monitor metrics list-definitions \
  --resource "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$WEB_APP_NAME" \
  --metric-names "PercentageCPU" "MemoryPercentage" "Http2xx" "Http5xx"

# Query Application Insights
# Via Azure Portal -> Application Insights -> Logs (KQL queries)
# Example KQL:
# requests
# | where url contains "api"
# | where duration > 1000
# | summarize count() by url, bin(duration, 100)
```

---

## Post-Deployment Checklist

After deploying your web app in ASE, verify:

- [ ] Application is deployed and running
- [ ] Health check endpoint responds (200 OK)
- [ ] HTTPS is working and properly configured
- [ ] Authentication and authorization working
- [ ] Database connectivity verified
- [ ] All external services accessible
- [ ] Logging and monitoring active
- [ ] Backups configured and tested
- [ ] Auto-scaling rules in place
- [ ] Security scanning enabled
- [ ] NSG rules appropriate and restrictive
- [ ] Private DNS zones working (for ILB ASE)
- [ ] VNet peering established (for hub-spoke)
- [ ] ExpressRoute connectivity working (if applicable)
- [ ] Load testing completed
- [ ] Performance meets SLAs
- [ ] Documentation updated
- [ ] Operations team trained

---

## Best Practices Summary

### Security
✅ Use Managed Identity for all authentication
✅ Store secrets in Key Vault
✅ Enable HTTPS only
✅ Use Azure Entra ID for application authentication
✅ Enable Azure Defender for App Service
✅ Implement WAF with Application Gateway
✅ Use NSGs to restrict traffic
✅ Enable audit logging

### Performance
✅ Use I2V2 or I3V2 SKUs for production workloads
✅ Configure auto-scaling properly
✅ Enable Always On for consistent performance
✅ Use HTTP/2 for improved performance
✅ Monitor key metrics continuously
✅ Set up alerts for anomalies

### Operations
✅ Implement comprehensive monitoring
✅ Set up automated backups
✅ Create disaster recovery plan
✅ Document architecture and procedures
✅ Use Infrastructure as Code (ARM/Terraform)
✅ Implement CI/CD pipelines
✅ Regular capacity planning reviews
✅ Keep ASE and apps updated

### Cost
✅ Right-size instances based on actual usage
✅ Use reserved instances for known capacity
✅ Shut down non-production environments
✅ Monitor cost trends regularly
✅ Use spot instances where appropriate (if available)
✅ Evaluate multi-region needs (may not need ASE in all regions)

---

## References

- [App Service Environment Documentation](https://learn.microsoft.com/azure/app-service/environment/)
- [ASEv3 Overview](https://learn.microsoft.com/azure/app-service/environment/overview)
- [ILB ASE Configuration](https://learn.microsoft.com/azure/app-service/environment/create-ilb-ase)
- [Azure CLI for App Service](https://learn.microsoft.com/cli/azure/webapp/)
- [Azure Monitor and Alerting](https://learn.microsoft.com/azure/azure-monitor/)

---

## Getting Help

If you encounter issues:

1. **Check Azure Portal Diagnostics**: App Service → Diagnose and Solve Problems
2. **Review Azure Service Health**: See if there are platform issues
3. **Contact Azure Support**: For complex infrastructure issues
4. **Check Azure Documentation**: Most common issues have solutions documented
5. **Monitor Application Insights**: For application-level issues

