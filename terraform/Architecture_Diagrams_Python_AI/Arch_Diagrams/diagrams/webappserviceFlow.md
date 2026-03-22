# Web App Service Flow — plte-fie-test2

Enterprise architecture data flow documentation for the `plte-fie-test2` web application
hosted in App Service Environment `ase-plte-fie` (ILBASEv3).

---

## Architecture Overview

| Component | Name | Location |
|---|---|---|
| Web App | `plte-fie-test2` | Spoke subscription — ASE |
| App Service Environment | `ase-plte-fie` (ILBASEv3) | `snet-ase` (10.3.0.0/26) |
| VNet | `vnet-app-spoke` (10.3.0.0/24) | Spoke subscription |
| Key Vault | `kv-app-spoke` | Spoke subscription |
| App Configuration | `appconf-app-spoke` | Spoke subscription |
| Application Insights | `appi-app-spoke` | Spoke subscription |
| Private DNS Zone | `privatelink.azurewebsites.net` | Hub subscription (shared) |
| AMPLS | `ampls-shared-hub` | Hub subscription |
| Log Analytics Workspace | `law-shared-enterprise` | Hub subscription |
| ESF | Enterprise Security Framework | On-premises (private cloud) |
| Identity Provider | Azure Entra ID | Cloud (external) |

---

## Flow 1 — Authentication

```
User (internal network / VPN)
  │
  ▼
Azure Entra ID  ← App Registration configured with user claims
  │
  │  Auth token + user claims (email, name, roles) passed in HTTP headers
  ▼
Web App: plte-fie-test2
  (accessible via ILB private IP only — ASE ILB mode, NO public access)
```

**Notes:**
- ASE is in ILB mode — no public endpoint exists
- Users must be on corporate network or VPN to reach the app
- Entra ID App Registration is configured to pass user identity claims in headers

---

## Flow 2 — Authorization (ESF)

```
Web App: plte-fie-test2
  │
  │  HTTPS request with user claims in headers
  │  (via ExpressRoute → Hub VNet → On-premises)
  ▼
ESF — Enterprise Security Framework (on-premises private cloud)
  │
  │  Returns user roles and data entitlements
  ▼
Web App applies role-based access control
```

**Notes:**
- ESF connectivity is via ExpressRoute (private, no internet traversal)
- Web app sends user identity headers received from Entra ID to ESF
- ESF is the authoritative source for roles and data entitlements

---

## Flow 3 — Secret Management

### Current State — Azure Key Vault

```
Web App: plte-fie-test2
  │  (System-Assigned Managed Identity)
  ▼
Azure Key Vault: kv-app-spoke
  │
  │  Returns: credentials, API keys, certificates, connection strings
  ▼
Web App uses secrets at runtime
```

### Future State — HashiCorp Vault (Strategic)

```
Web App: plte-fie-test2
  │
  ▼
HashiCorp Vault  ← Central secrets platform for all app teams
  │
  │  Returns secrets centrally managed and audited
  ▼
Web App uses secrets at runtime
```

**Notes:**
- Azure Key Vault is the **current** active solution
- HashiCorp Vault is the **strategic future** replacement across the enterprise
- Managed Identity is used for Azure Key Vault access (no credentials stored in code)

---

## Flow 4 — Configuration Management

```
Web App: plte-fie-test2
  │  (System-Assigned Managed Identity)
  ▼
App Configuration Service: appconf-app-spoke
  │
  │  Returns: environment variables, feature flags, app settings
  ▼
Web App uses configuration at runtime
```

---

## Flow 5 — DNS Resolution

```
Client resolves: plte-fie-test2.<ase-domain>.appserviceenvironment.net
  │
  ▼
DNS query → Private DNS Zone in Hub subscription (shared services)
  │         (privatelink.azurewebsites.net or ASE custom domain)
  │         Policy: App teams register A records here
  │                 Spoke subscriptions have NO DNS forwarders
  ▼
A record returns ILB private IP of ase-plte-fie
  │
  ▼
Request reaches Web App privately via ILB
```

**Key DNS Policy:**
- Private DNS Zone is owned and managed by the **Shared Services / Hub team**
- Spoke subscriptions **cannot** create their own private DNS zones (no DNS forwarders configured)
- Each app team submits a request to register their web app / ASE DNS record in the shared zone
- `ase-plte-fie` domain and `plte-fie-test2` A record are registered in the Hub DNS zone

---

## Flow 6 — Monitoring & Observability

```
Web App: plte-fie-test2
  │
  │  Application telemetry, logs, exceptions, performance metrics
  ▼
Application Insights: appi-app-spoke  (spoke subscription)
  │
  │  Private Link via AMPLS (no public internet)
  ▼
AMPLS: ampls-shared-hub  (hub subscription)
  │
  │  Aggregated enterprise telemetry
  ▼
Log Analytics Workspace: law-shared-enterprise  (hub subscription)
  │
  ▼
Dashboards · Alerts · Queries · Audit logs
```

---

## Network Security Summary

| Rule | Detail |
|---|---|
| Public access | ✗ DISABLED — ASE ILB mode |
| Private endpoint for web app | ✗ NOT NEEDED — ASE ILB inherently private |
| Inbound traffic | Internal network / VPN only (via ILB private IP) |
| Outbound to ESF | Via ExpressRoute (private, on-premises) |
| Outbound to Azure services | Via Managed Identity (Key Vault, App Config) |
| Monitoring traffic | Via AMPLS private link (no public internet) |
| NSG | Applied to `snet-ase` and `snet-pe` subnets |

---

## Subnet Layout

| Subnet | CIDR | Purpose |
|---|---|---|
| `snet-ase` | 10.3.0.0/26 | App Service Environment (ASE) |
| `snet-pe` | 10.3.1.0/26 | Reserved for future private endpoints |

---

## Related Files

| File | Description |
|---|---|
| `ph_dev_architecture.py` | Python script to generate the architecture diagram |
| `ph_dev_architecture.png` | Architecture diagram (PNG) |
| `ph_dev_architecture.drawio` | Architecture diagram (Draw.io — editable) |
| `ph_dev_architecture.dot` | Architecture diagram (Graphviz DOT source) |
| `../instructions.md` | Full architecture specification and diagram requirements |
