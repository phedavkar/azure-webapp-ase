# Enterprise Hub-Spoke Architecture — App Service Environment (ILB ASEv3)# Enterprise Hub-Spoke Architecture with App Service Environment (ILB)Create an Azure architecture diagram.



## OverviewScenario:



Enterprise hub-spoke network topology with on-premises integration via ExpressRoute.## ScenarioOne subscription, one VNet, three subnets, web tier, app tier, data tier, and monitoring.

Single web application hosted in a spoke subscription using App Service Environment (ILBASEv3)

with Entra ID authentication and private access only.



---Enterprise hub-spoke network topology with on-premises integration via ExpressRoute.Resources:



## SubscriptionsSingle web application hosted in spoke subscription using App Service Environment (ILBASEv3) with Entra ID authentication and private access only.



### Spoke Subscription (`sub-app-spoke`)1. **Networking**



#### 1. Networking---   - VNet: "vnet-contoso-auea-001" (10.10.0.0/16)



- **VNet**: `vnet-app-spoke` (10.3.0.0/24)   - Subnets:

- **Subnets**:

  - `snet-ase` (10.3.0.0/26) — App Service Environment subnet## Resources in Spoke Subscription     - "snet-frontend" (10.10.1.0/24)

  - `snet-pe` (10.3.1.0/26) — Reserved for future private endpoints

- **VNet Peering**: Connected to Hub VNet (shared services subscription)     - "snet-backend" (10.10.2.0/24)

- **NSGs**: Network Security Groups on each subnet

### 1. **Networking**     - "snet-data" (10.10.3.0/24)

#### 2. Compute

- **VNet**: `vnet-app-spoke` (10.3.0.0/24)   - Azure Firewall: "azfw-contoso"

- **App Service Environment (ASEv3)**:

  - Name: `ase-plte-fie`- **Subnets**:   - NSGs for each subnet

  - Type: `ILBASEv3` (Internal Load Balancer — no public access)

  - Subnet: `snet-ase`  - `snet-ase` (10.3.0.0/26) - App Service Environment   - Route table with default route to Firewall

  - Public Access: **DISABLED**

  - DNS: ASE domain record is registered in the Private DNS Zone hosted in the Hub subscription (shared service)  - `snet-pe` (10.3.1.0/26) - Reserved for private endpoints

- **App Service Plan**: Isolated tier (I1V2), hosted inside ASE

- **Web App**: `plte-fie-test2`- **VNet Peering**: Connected to Hub VNet2. **Web Tier**

  - Runtime: Java 17 + Tomcat 10.1

  - Hosted inside ASE (ILB mode — no private endpoint needed, ASE itself provides private access)- **ExpressRoute**: Via Hub to on-premises   - Azure Front Door: "afd-contoso"

  - DNS record for the web app registered in the shared Private DNS Zone in Hub subscription

- **NSGs**: Network Security Groups for each subnet   - Application Gateway (WAF): "agw-contoso" in frontend subnet

#### 3. Security & Identity

- **Private DNS Zones**: For ILB ASE resolution   - App Service Plan: "asp-contoso-prod"

- **Azure Entra ID**: Authentication IDP

  - App Registration: Configured with user claims passed in request headers   - Web App: "ph-frontend-portal"

- **Azure Key Vault**: `kv-app-spoke`

  - Purpose: Secret management (**current solution**)### 2. **Compute**

  - Access: Via Managed Identity (no public endpoint)

  - Contents: Entra ID credentials, API keys, certificates- **App Service Environment (ASEv3)**:3. **Application Tier**

  - **Future**: Will be replaced by **HashiCorp Vault** (strategic direction)

- **App Configuration Service**: `appconf-app-spoke`  - Name: `ase-plte-fie`   - Internal App Service Plan: "asp-contoso-backend"

  - Purpose: Configuration management

  - Stores: Environment variables, feature flags, app settings  - Type: `ILBASEv3` (Internal Load Balancer)   - Backend App Service: "app-order-api"

- **Managed Identity**: System-assigned, used by Web App to access Key Vault and App Configuration

  - Public Access: **DISABLED**   - App Service Environment V3 with ILB

#### 4. Monitoring

  - Subnet: `snet-ase`   - Azure Function App: "func-order-processor"

- **Application Insights**: `appi-app-spoke`

  - Purpose: Application performance monitoring, logs, exceptions- **App Service Plan**: Isolated tier (I1V2)   - Azure Service Bus: "sb-contoso-orders"

  - Forwards to AMPLS in Hub subscription

- **Web App**: `plte-fie-test2`

---

  - Runtime: Java 17 + Tomcat 10.14. **Data Tier**

### Hub Subscription / Shared Services (`sub-hub-shared`)

  - Hosted in: ASE (private only, no public endpoints)   - SQL Server: "sqlsrv-contoso"

#### 1. Networking

   - SQL Database: "sqldb-orders"

- **Hub VNet**: Peered to all spoke VNets

- **ExpressRoute Gateway**: Connects Hub VNet to on-premises network### 3. **Security & Identity**   - Storage Account: "stcontosodata001"

- **Private DNS Zone**: `privatelink.azurewebsites.net` (or ASE-specific custom domain)

  - Hosted in **Hub / Shared Services subscription** — NOT in spoke- **Azure Entra ID**: Authentication IDP   - Azure Key Vault: "kv-contoso-prod"

  - **Policy**: App teams (spoke subscriptions) do NOT have permission to create their own private DNS zones (no DNS forwarders in spoke subscriptions)

  - **Usage**: Each app team creates a DNS record (A record) in this shared zone for their web app / ASE  - App Registration: Configured with user claims in headers   - Private Endpoints for SQL, Storage, Key Vault (inside snet-data)

  - The `ase-plte-fie` ASE domain and `plte-fie-test2` web app have their DNS records registered here

- **Azure Key Vault**: `kv-app-spoke`

#### 2. Monitoring (Shared)

  - Purpose: Secret management5. **Monitoring**

- **AMPLS** (Azure Monitor Private Link Scope): `ampls-shared-hub`

  - Purpose: Private link endpoint for all Azure Monitor traffic  - Access: Managed Identity   - Log Analytics Workspace: "law-contoso-prod"

  - Receives forwarded telemetry from all spoke App Insights instances

- **Log Analytics Workspace**: `law-shared-enterprise`  - Contents: Entra ID credentials, API keys, certificates   - Application Insights: "appi-contoso"

  - Purpose: Enterprise-wide centralized log aggregation

  - Consumers: All app teams forward logs here via AMPLS- **App Configuration Service**: `appconf-app-spoke`



---  - Purpose: Configuration managementConnections:



### On-Premises  - Stores: Environment variables, feature flags, app settings- Users → Front Door → Application Gateway → Web App



- **ESF** (Enterprise Security Framework):- **Managed Identity**: System-assigned for secure Azure service access- Web App → Order API

  - Location: Private cloud, on-premises

  - Connectivity: Via ExpressRoute through Hub- Order API → SQL DB and Storage (private endpoints)

  - Purpose: User authorization — receives user claims, returns roles and data entitlements

  - Integration: Web App → ESF (HTTPS over private ExpressRoute) → Web App receives roles### 4. **Enterprise Security Framework (ESF) Integration**- Function App → Service Bus → SQL



---- **Location**: On-premises private cloud- All apps → Key Vault for secrets



## Future State — HashiCorp Vault- **Connectivity**: Via ExpressRoute (secure, private)- All resources → Log Analytics



- **Strategic plan**: Replace Azure Key Vault with **HashiCorp Vault** enterprise-wide- **Purpose**: User authorization, roles, data entitlements- All outbound traffic → Azure Firewall

- **Current state**: Azure Key Vault (`kv-app-spoke`) is the active secrets solution

- **Future state**: HashiCorp Vault (on-premises or dedicated subscription) will serve as the- **Integration**: Web App → ESF (HTTPS over ExpressRoute) → Returns user roles

  central secrets manager for all app teams

- **Diagram requirement**: Show both current (Azure Key Vault) and future (HashiCorp Vault) in theLayout rules:

  architecture diagram. Use a visual indicator (e.g., dashed border or "Future" label) for HashiCorp Vault.

### 5. **Monitoring & Logging**- Top: Users + Front Door

---

- **Application Insights** (Spoke): `appi-app-spoke`- Below: Application Gateway

## Key Architecture Decisions

  - Purpose: Detailed performance metrics, app logs, exceptions- Middle: Web App + Backend API

| Decision | Detail |

|---|---|  - Data collection: Automatic instrumentation- Right side: Function App + Service Bus

| ASE ILB mode | No public access; web app accessible only within private network |

| No private endpoint for web app | Not needed — ASE ILB inherently provides private-only access |- **Connection to Enterprise Monitoring**:- Bottom: Data tier (SQL, Storage, Key Vault)

| Private DNS Zone in Hub | Shared across all app teams; spoke subscriptions have no DNS forwarders |

| Key Vault in Spoke | Current solution; access via Managed Identity only |  - Via AMPLS (Azure Monitor Private Link Scope) in Hub- Bottom left: Firewall

| HashiCorp Vault | Future strategic replacement for Azure Key Vault |

| Monitoring via AMPLS | All App Insights data flows privately to shared LAW in hub |  - Forwards to Log Analytics Workspace in Hub (Shared Services)- Bottom centre: Monitoring resources

| Authorization via ESF | On-premises ESF over ExpressRoute; no direct internet auth |

- Place everything inside a single VNet box with subnet boundaries.

---

---

## Data Flows

Output format required:

### Authentication Flow

```## Resources in Hub Subscription (Shared Services)- List each container (VNet, each subnet)

User (internal, on-premises or VPN)

  ↓- List each resource with labels

Azure Entra ID (authentication — cloud)

  ↓- **ExpressRoute Gateway**: Connection to on-premises- List the arrows and connections

Web App plte-fie-test2 (private via ILB ASE)

  ↓- **Log Analytics Workspace**: `law-shared-enterprise`- Make the layout instructions clear

User claims passed in HTTP headers (email, name, roles)

```  - Purpose: Enterprise-wide centralized logging- Use icons for every resource following the icon instructions above



### Authorization Flow  - Consumers: All app teams write logs here

```- **AMPLS** (Azure Monitor Private Link Scope): `ampls-shared-hub`

Web App (receives user claims in headers)  - Purpose: Private link connectivity for monitoring data

  ↓  - Connection: App Insights (spoke) → AMPLS → LAW (hub)

ESF — Enterprise Security Framework (on-premises, via ExpressRoute)

  ↓---

ESF returns user roles and data entitlements

  ↓## External Resources

Web App applies role-based access control

```- **Azure Entra ID**: Cloud authentication service

- **ESF**: On-premises enterprise security framework

### Secret Management Flow (Current)

```---

Web App (System-Assigned Managed Identity)

  ↓## Data Flows

Azure Key Vault kv-app-spoke (spoke subscription)

  ↓### Authentication Flow

Returns secrets: credentials, API keys, certificates```

```User → Azure Entra ID (authentication)

  ↓

### Secret Management Flow (Future)Entra ID → Web App (plte-fie-test2, private via ILB ASE)

```  ↓

Web AppUser info in headers (claims, email, name, etc.)

  ↓```

HashiCorp Vault (strategic secrets platform)

  ↓### Authorization Flow

Returns secrets centrally managed across all teams```

```Web App → ESF (via ExpressRoute/Hub, HTTPS)

  ↓

### Configuration Management FlowESF receives user info in headers

```  ↓

Web App (System-Assigned Managed Identity)ESF → Returns user roles and data entitlements

  ↓  ↓

App Configuration Service appconf-app-spokeWeb App applies role-based authorization

  ↓```

Returns environment-specific settings, feature flags

```### Secret Management Flow

```

### Monitoring FlowWeb App (Managed Identity)

```  ↓

Web AppAzure Key Vault (kv-app-spoke)

  ↓  ↓ (returns secrets)

Application Insights appi-app-spoke (spoke subscription)Web App uses secrets securely

  ↓```

AMPLS ampls-shared-hub (hub subscription — private link)

  ↓### Configuration Management Flow

Log Analytics Workspace law-shared-enterprise (hub — enterprise-wide)```

  ↓Web App (Managed Identity)

Dashboards, alerts, queries  ↓

```App Configuration Service (appconf-app-spoke)

  ↓ (returns config values)

### DNS Resolution FlowWeb App uses environment-specific settings

``````

Client resolves plte-fie-test2.<ase-domain>

  ↓### Monitoring Flow

DNS query forwarded to Private DNS Zone in Hub subscription```

  ↓Web App

A record returns ILB IP of ase-plte-fie  ↓

  ↓Application Insights (appi-app-spoke, spoke subscription)

Request reaches Web App privately  ↓

```AMPLS (ampls-shared-hub, hub subscription)

  ↓

---Log Analytics Workspace (law-shared-enterprise, enterprise-wide)

  ↓

## Architecture Diagram RequirementsAnalytics, alerts, dashboards

```

Generate a diagram with the following structure:

---

### Regions / Clusters

## Network Security

1. **Hub Subscription — Shared Services (Left)**

   - Hub VNet- **Public Access**: ✓ DISABLED

   - ExpressRoute Gateway- **Private Only**: ILB ASE internal endpoints

   - Private DNS Zone (`privatelink.azurewebsites.net` or ASE custom domain)- **Outbound to ESF**: Via ExpressRoute (on-premises private)

     - Label: "Managed by Shared Services — app teams register records here"- **Outbound to Azure Services**: Via service endpoints (no public internet)

   - AMPLS (`ampls-shared-hub`)- **NSG Rules**: Restrict to required traffic only

   - Log Analytics Workspace (`law-shared-enterprise`)

---

2. **Spoke Subscription — App Team (Center)**

   - Spoke VNet `vnet-app-spoke` (10.3.0.0/24)## Architecture Diagram Requirements

     - Subnet `snet-ase` (10.3.0.0/26):

       - ASE `ase-plte-fie` (ILBASEv3, NO PUBLIC ACCESS)Generate diagram showing:

         - Web App `plte-fie-test2` (Java 17 / Tomcat 10.1)

         - Managed Identity (system-assigned)### **Three Regions**

     - Subnet `snet-pe` (10.3.1.0/26):1. **Hub Subscription (Left)**

       - Label: "Reserved for Private Endpoints"   - Hub VNet

   - Security cluster (outside subnets, within spoke):   - ExpressRoute Gateway

     - Azure Key Vault `kv-app-spoke` — label: **(Current)**   - AMPLS (Azure Monitor Private Link Scope)

     - HashiCorp Vault — label: **(Future — Strategic)**  ← dashed border   - Log Analytics Workspace (simplified view)

     - App Configuration `appconf-app-spoke`

   - Application Insights `appi-app-spoke`2. **Spoke Subscription (Center)**

   - Spoke VNet (`vnet-app-spoke` 10.3.0.0/24)

3. **On-Premises (Right)**   - Subnets clearly marked

   - ESF (Enterprise Security Framework)   - ASE (with ILB indicator, no public access)

   - Private cloud network   - Web App (`plte-fie-test2`) inside ASE

   - Key Vault (`kv-app-spoke`)

4. **External / Cloud Identity (Top)**   - App Configuration (`appconf-app-spoke`)

   - Azure Entra ID   - Application Insights (`appi-app-spoke`)

   - Managed Identity (system-assigned)

### Network Connections

3. **On-Premises (Right)**

- **VNet Peering**: Hub VNet ↔ Spoke VNet (solid line)   - ESF (Enterprise Security Framework) system

- **ExpressRoute**: Hub Gateway ↔ On-Premises (thick dashed line)

- **DNS**: Web App / ASE → Private DNS Zone in Hub (dotted line, label: "DNS registration")4. **External Cloud (Top)**

   - Azure Entra ID

### Data Flow Connections (color-coded)

### **Network Connections**

| Flow | Color | Connection |- **VNet Peering**: Hub ↔ Spoke (solid line)

|---|---|---|- **ExpressRoute**: Hub ↔ On-Premises (dashed line)

| Authentication | Green | Entra ID → Web App |- **Private Links**: App Insights → AMPLS → LAW (dotted line)

| Authorization | Blue | Web App → ESF → Web App |

| Secrets (current) | Orange | Web App → Azure Key Vault |### **Data Flow Connections**

| Secrets (future) | Orange dashed | Web App → HashiCorp Vault |- **Authentication** (green): Entra ID → Web App

| Configuration | Purple | Web App → App Configuration |- **Authorization** (blue): Web App → ESF → Web App (with roles)

| Monitoring | Red | Web App → App Insights → AMPLS → LAW |- **Secrets** (orange): Web App → Key Vault

| DNS resolution | Gray dotted | Client → Private DNS Zone → ASE ILB IP |- **Configuration** (purple): Web App → App Configuration

- **Monitoring** (red): Web App → App Insights → AMPLS → LAW

### Important Labels and Annotations

### **Important Labels**

- ASE: `ILBASEv3` with badge `NO PUBLIC ACCESS`- Mark ASE as `ILBASEv3` with `NO PUBLIC ACCESS` indicator

- Web App: `NO PRIVATE ENDPOINT NEEDED` (ASE ILB provides private access)- Mark all connections with data flow type

- Private DNS Zone: `SHARED — Hub Subscription`, `App teams register records here`- Show Managed Identity usage

- Azure Key Vault: `CURRENT`- Highlight private-only connectivity

- HashiCorp Vault: `FUTURE — Strategic` with dashed border- Label all resource names

- Managed Identity: Show as attached to Web App- Show CIDR blocks for subnets

- All resource names and CIDR blocks labelled

### **Layout**

### Layout- Spoke VNet centered with clear subnet boundaries

- Hub VNet simplified on left

- Hub subscription cluster: left side- ESF on right with ExpressRoute connection

- Spoke subscription cluster: center- Entra ID cloud at top

- On-premises: right side- Clear visual separation between public cloud, private cloud, and on-premises

- Entra ID: top center- Monitoring path clearly distinct from main data flow

- Monitoring path visually distinct (bottom routing)
- DNS flow shown as separate dotted path from main data flows
