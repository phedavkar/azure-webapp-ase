# Enterprise Hub-Spoke Architecture with App Service Environment (ILB)Create an Azure architecture diagram.

Scenario:

## ScenarioOne subscription, one VNet, three subnets, web tier, app tier, data tier, and monitoring.



Enterprise hub-spoke network topology with on-premises integration via ExpressRoute.Resources:

Single web application hosted in spoke subscription using App Service Environment (ILBASEv3) with Entra ID authentication and private access only.

1. **Networking**

---   - VNet: "vnet-contoso-auea-001" (10.10.0.0/16)

   - Subnets:

## Resources in Spoke Subscription     - "snet-frontend" (10.10.1.0/24)

     - "snet-backend" (10.10.2.0/24)

### 1. **Networking**     - "snet-data" (10.10.3.0/24)

- **VNet**: `vnet-app-spoke` (10.3.0.0/24)   - Azure Firewall: "azfw-contoso"

- **Subnets**:   - NSGs for each subnet

  - `snet-ase` (10.3.0.0/26) - App Service Environment   - Route table with default route to Firewall

  - `snet-pe` (10.3.1.0/26) - Reserved for private endpoints

- **VNet Peering**: Connected to Hub VNet2. **Web Tier**

- **ExpressRoute**: Via Hub to on-premises   - Azure Front Door: "afd-contoso"

- **NSGs**: Network Security Groups for each subnet   - Application Gateway (WAF): "agw-contoso" in frontend subnet

- **Private DNS Zones**: For ILB ASE resolution   - App Service Plan: "asp-contoso-prod"

   - Web App: "ph-frontend-portal"

### 2. **Compute**

- **App Service Environment (ASEv3)**:3. **Application Tier**

  - Name: `ase-plte-fie`   - Internal App Service Plan: "asp-contoso-backend"

  - Type: `ILBASEv3` (Internal Load Balancer)   - Backend App Service: "app-order-api"

  - Public Access: **DISABLED**   - App Service Environment V3 with ILB

  - Subnet: `snet-ase`   - Azure Function App: "func-order-processor"

- **App Service Plan**: Isolated tier (I1V2)   - Azure Service Bus: "sb-contoso-orders"

- **Web App**: `plte-fie-test2`

  - Runtime: Java 17 + Tomcat 10.14. **Data Tier**

  - Hosted in: ASE (private only, no public endpoints)   - SQL Server: "sqlsrv-contoso"

   - SQL Database: "sqldb-orders"

### 3. **Security & Identity**   - Storage Account: "stcontosodata001"

- **Azure Entra ID**: Authentication IDP   - Azure Key Vault: "kv-contoso-prod"

  - App Registration: Configured with user claims in headers   - Private Endpoints for SQL, Storage, Key Vault (inside snet-data)

- **Azure Key Vault**: `kv-app-spoke`

  - Purpose: Secret management5. **Monitoring**

  - Access: Managed Identity   - Log Analytics Workspace: "law-contoso-prod"

  - Contents: Entra ID credentials, API keys, certificates   - Application Insights: "appi-contoso"

- **App Configuration Service**: `appconf-app-spoke`

  - Purpose: Configuration managementConnections:

  - Stores: Environment variables, feature flags, app settings- Users → Front Door → Application Gateway → Web App

- **Managed Identity**: System-assigned for secure Azure service access- Web App → Order API

- Order API → SQL DB and Storage (private endpoints)

### 4. **Enterprise Security Framework (ESF) Integration**- Function App → Service Bus → SQL

- **Location**: On-premises private cloud- All apps → Key Vault for secrets

- **Connectivity**: Via ExpressRoute (secure, private)- All resources → Log Analytics

- **Purpose**: User authorization, roles, data entitlements- All outbound traffic → Azure Firewall

- **Integration**: Web App → ESF (HTTPS over ExpressRoute) → Returns user roles

Layout rules:

### 5. **Monitoring & Logging**- Top: Users + Front Door

- **Application Insights** (Spoke): `appi-app-spoke`- Below: Application Gateway

  - Purpose: Detailed performance metrics, app logs, exceptions- Middle: Web App + Backend API

  - Data collection: Automatic instrumentation- Right side: Function App + Service Bus

- **Connection to Enterprise Monitoring**:- Bottom: Data tier (SQL, Storage, Key Vault)

  - Via AMPLS (Azure Monitor Private Link Scope) in Hub- Bottom left: Firewall

  - Forwards to Log Analytics Workspace in Hub (Shared Services)- Bottom centre: Monitoring resources

- Place everything inside a single VNet box with subnet boundaries.

---

Output format required:

## Resources in Hub Subscription (Shared Services)- List each container (VNet, each subnet)

- List each resource with labels

- **ExpressRoute Gateway**: Connection to on-premises- List the arrows and connections

- **Log Analytics Workspace**: `law-shared-enterprise`- Make the layout instructions clear

  - Purpose: Enterprise-wide centralized logging- Use icons for every resource following the icon instructions above

  - Consumers: All app teams write logs here
- **AMPLS** (Azure Monitor Private Link Scope): `ampls-shared-hub`
  - Purpose: Private link connectivity for monitoring data
  - Connection: App Insights (spoke) → AMPLS → LAW (hub)

---

## External Resources

- **Azure Entra ID**: Cloud authentication service
- **ESF**: On-premises enterprise security framework

---

## Data Flows

### Authentication Flow
```
User → Azure Entra ID (authentication)
  ↓
Entra ID → Web App (plte-fie-test2, private via ILB ASE)
  ↓
User info in headers (claims, email, name, etc.)
```

### Authorization Flow
```
Web App → ESF (via ExpressRoute/Hub, HTTPS)
  ↓
ESF receives user info in headers
  ↓
ESF → Returns user roles and data entitlements
  ↓
Web App applies role-based authorization
```

### Secret Management Flow
```
Web App (Managed Identity)
  ↓
Azure Key Vault (kv-app-spoke)
  ↓ (returns secrets)
Web App uses secrets securely
```

### Configuration Management Flow
```
Web App (Managed Identity)
  ↓
App Configuration Service (appconf-app-spoke)
  ↓ (returns config values)
Web App uses environment-specific settings
```

### Monitoring Flow
```
Web App
  ↓
Application Insights (appi-app-spoke, spoke subscription)
  ↓
AMPLS (ampls-shared-hub, hub subscription)
  ↓
Log Analytics Workspace (law-shared-enterprise, enterprise-wide)
  ↓
Analytics, alerts, dashboards
```

---

## Network Security

- **Public Access**: ✓ DISABLED
- **Private Only**: ILB ASE internal endpoints
- **Outbound to ESF**: Via ExpressRoute (on-premises private)
- **Outbound to Azure Services**: Via service endpoints (no public internet)
- **NSG Rules**: Restrict to required traffic only

---

## Architecture Diagram Requirements

Generate diagram showing:

### **Three Regions**
1. **Hub Subscription (Left)**
   - Hub VNet
   - ExpressRoute Gateway
   - AMPLS (Azure Monitor Private Link Scope)
   - Log Analytics Workspace (simplified view)

2. **Spoke Subscription (Center)**
   - Spoke VNet (`vnet-app-spoke` 10.3.0.0/24)
   - Subnets clearly marked
   - ASE (with ILB indicator, no public access)
   - Web App (`plte-fie-test2`) inside ASE
   - Key Vault (`kv-app-spoke`)
   - App Configuration (`appconf-app-spoke`)
   - Application Insights (`appi-app-spoke`)
   - Managed Identity (system-assigned)

3. **On-Premises (Right)**
   - ESF (Enterprise Security Framework) system

4. **External Cloud (Top)**
   - Azure Entra ID

### **Network Connections**
- **VNet Peering**: Hub ↔ Spoke (solid line)
- **ExpressRoute**: Hub ↔ On-Premises (dashed line)
- **Private Links**: App Insights → AMPLS → LAW (dotted line)

### **Data Flow Connections**
- **Authentication** (green): Entra ID → Web App
- **Authorization** (blue): Web App → ESF → Web App (with roles)
- **Secrets** (orange): Web App → Key Vault
- **Configuration** (purple): Web App → App Configuration
- **Monitoring** (red): Web App → App Insights → AMPLS → LAW

### **Important Labels**
- Mark ASE as `ILBASEv3` with `NO PUBLIC ACCESS` indicator
- Mark all connections with data flow type
- Show Managed Identity usage
- Highlight private-only connectivity
- Label all resource names
- Show CIDR blocks for subnets

### **Layout**
- Spoke VNet centered with clear subnet boundaries
- Hub VNet simplified on left
- ESF on right with ExpressRoute connection
- Entra ID cloud at top
- Clear visual separation between public cloud, private cloud, and on-premises
- Monitoring path clearly distinct from main data flow
