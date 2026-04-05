# Developer Runbook — plte-fie-test2 Observability Guide

> **App**: `plte-fie-test2` (Java 17 / Tomcat 10.1, ILBASEv3)  
> **App Insights**: `appi-app-spoke` (Spoke subscription)  
> **Shared LAW**: `law-shared-hub` (Hub subscription — shared, use sparingly)  
> **Shared AMPLS**: `ampls-shared-hub` (Hub subscription — private telemetry only)  
> **Last updated**: April 2026

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Quick Access — Live Log Streaming](#2-quick-access--live-log-streaming)
3. [Quick Access — Azure Portal](#3-quick-access--azure-portal)
4. [Quick Access — Azure CLI](#4-quick-access--azure-cli)
5. [KQL Query Runbook](#5-kql-query-runbook)
6. [Shared LAW Rules of Engagement](#6-shared-law-rules-of-engagement)
7. [Alert Response Playbook](#7-alert-response-playbook)
8. [Sampling & Cost Guidance](#8-sampling--cost-guidance)

---

## 1. Architecture Overview

```
Developer Machine
      │
      │ (AMPLS Private DNS — no public internet)
      ▼
appi-app-spoke  ──── AMPLS link ────►  ampls-shared-hub
(App Insights)                              │
      ▲                                     ▼
      │                              law-shared-hub
plte-fie-test2                       (Shared LAW)
(Web App / ASE ILB)
      │
      ├──► ESF (on-prem via ExpressRoute)   [authz]
      ├──► Oracle DB (on-prem via ER)       [data]
      ├──► kv-app-spoke (Key Vault)         [secrets]
      └──► appconf-app-spoke (App Config)   [config]
```

**Key principle**: App Insights (`appi-app-spoke`) is your **primary** debugging tool.
Shared LAW (`law-shared-hub`) is for **compliance logs only** — never flood it with debug data.

---

## 2. Quick Access — Live Log Streaming

### Option A: Azure CLI (fastest, no portal needed)

```bash
# Stream live stdout/stderr logs
az webapp log tail \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg

# Stream with filter (e.g., only ERROR lines)
az webapp log tail \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg \
  --provider application \
  --filter Error
```

> **Tip**: Enable application logging first if not already on:
> ```bash
> az webapp log config \
>   --name plte-fie-test2 \
>   --resource-group ph-dev-rg \
>   --application-logging filesystem \
>   --level warning
> ```

### Option B: VS Code Azure Extension

1. Install: `ms-azuretools.vscode-azureappservice`
2. Open **Azure** sidebar (`Ctrl+Shift+A` / `Cmd+Shift+A`)
3. Expand **App Services** → `plte-fie-test2`
4. Right-click → **Start Streaming Logs**

### Option C: Azure Portal

1. Go to `plte-fie-test2` → **Log stream** (left menu)
2. Select **Application logs** for Java output

---

## 3. Quick Access — Azure Portal

| Task | Portal Path |
|---|---|
| Live log stream | App Service → Log stream |
| App Insights overview | `appi-app-spoke` → Overview |
| Failed requests | `appi-app-spoke` → Failures |
| Slow requests | `appi-app-spoke` → Performance |
| End-to-end traces | `appi-app-spoke` → Transaction search |
| Live Metrics (real-time) | `appi-app-spoke` → Live metrics |
| Custom KQL queries | `appi-app-spoke` → Logs |
| Shared LAW queries | `law-shared-hub` → Logs *(use sparingly)* |

---

## 4. Quick Access — Azure CLI

```bash
# ── Find App Insights resource ID ──────────────────────────────
az monitor app-insights component show \
  --app appi-app-spoke \
  --resource-group ph-dev-rg \
  --query "{name:name, appId:appId, connectionString:connectionString}" \
  --output table

# ── Run a KQL query via CLI ─────────────────────────────────────
APP_ID=$(az monitor app-insights component show \
  --app appi-app-spoke \
  --resource-group ph-dev-rg \
  --query appId --output tsv)

az monitor app-insights query \
  --app "$APP_ID" \
  --analytics-query "
    exceptions
    | where timestamp > ago(30m)
    | where severityLevel >= 3
    | project timestamp, type, outerMessage
    | order by timestamp desc
    | take 20
  " \
  --output table

# ── Check web app health ────────────────────────────────────────
az webapp show \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg \
  --query "{state:state, hostName:defaultHostName, httpsOnly:httpsOnly}" \
  --output table

# ── Restart web app (last resort) ──────────────────────────────
az webapp restart \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg

# ── Check app settings (verify env vars) ───────────────────────
az webapp config appsettings list \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg \
  --output table
```

---

## 5. KQL Query Runbook

All `.kql` files are in the [`kql/`](kql/) folder. Open them in VS Code or paste into App Insights / LAW Logs blade.

### VS Code Setup for KQL

Install the KQL extension for syntax highlighting:
```
ext install rosshamish.kuskus-kusto-language-server
```

Then open any `.kql` file → you get syntax highlighting and autocomplete.

---

### Query Index

| File | Scenario | Target |
|---|---|---|
| [`01-errors-last-30min.kql`](kql/01-errors-last-30min.kql) | Alert fired / user reports error | App Insights |
| [`02-failed-requests-with-stack.kql`](kql/02-failed-requests-with-stack.kql) | HTTP 4xx/5xx with full stack trace | App Insights |
| [`03-slow-requests-latency.kql`](kql/03-slow-requests-latency.kql) | Performance / SLA investigation | App Insights |
| [`04-auth-entra-failures.kql`](kql/04-auth-entra-failures.kql) | User cannot log in (Entra ID) | App Insights |
| [`05-esf-authorization-failures.kql`](kql/05-esf-authorization-failures.kql) | User authenticated but 403 (ESF authz) | App Insights |
| [`06-oracle-db-connectivity.kql`](kql/06-oracle-db-connectivity.kql) | DB errors / ORA- codes / timeouts | App Insights |
| [`07-keyvault-secret-failures.kql`](kql/07-keyvault-secret-failures.kql) | Secret read failures (Managed Identity) | App Insights |
| [`08-performance-overview.kql`](kql/08-performance-overview.kql) | Daily health check / SLA report | App Insights |
| [`09-shared-law-queries.kql`](kql/09-shared-law-queries.kql) | HTTP logs / audit logs in shared LAW | **Shared LAW** ⚠️ |
| [`10-e2e-trace-by-operation-id.kql`](kql/10-e2e-trace-by-operation-id.kql) | Reconstruct full trace for one request | App Insights |

---

## 6. Shared LAW Rules of Engagement

> The shared LAW (`law-shared-hub`) serves **all spoke application teams**.
> Expensive or unscoped queries degrade everyone's experience and increase cost.

### ✅ You MAY send to shared LAW

| Log Category | Why |
|---|---|
| `AppServiceHTTPLogs` | HTTP request logs — SLA & audit evidence |
| `AppServiceAppLogs` | App logs at **WARN/ERROR level only** |
| `AppServiceAuditLogs` | Auth audit trail — compliance requirement |
| `AllMetrics` | Lightweight metrics — CPU, memory, requests |

### ❌ You MUST NOT send to shared LAW

| Log Category | Why Not | Use Instead |
|---|---|---|
| `AppServiceConsoleLogs` | Extremely verbose, floods LAW | App Insights Traces |
| `AppServicePlatformLogs` | Azure internal platform noise | Not needed |
| DEBUG / TRACE level logs | Developer noise | App Insights (sampled) |
| `AppServiceIPSecAuditLogs` | Not relevant without WAF | N/A |

### Query etiquette for shared LAW

```kusto
// ✅ CORRECT — always scope + time bound + limit
AppServiceAppLogs
| where TimeGenerated > ago(1h)
| where _ResourceId has "plte-fie-test2"   // YOUR app only
| where Level == "Error"
| take 100

// ❌ WRONG — no scope, no time bound
AppServiceAppLogs
| where Level == "Error"
```

---

## 7. Alert Response Playbook

| Alert | First Query | Likely Cause |
|---|---|---|
| Error rate > 5% | `01-errors-last-30min.kql` | Deploy issue / downstream service |
| P95 latency > 3s | `03-slow-requests-latency.kql` | Oracle slow query / ESF timeout |
| HTTP 401/403 spike | `04-auth-entra-failures.kql` | Entra token expiry / RBAC change |
| ESF 403 spike | `05-esf-authorization-failures.kql` | ESF policy change / ER connectivity |
| ORA- errors | `06-oracle-db-connectivity.kql` | DB connection pool / ExpressRoute |
| Key Vault 403 | `07-keyvault-secret-failures.kql` | Managed Identity RBAC removed |
| User reports "my request failed" | `10-e2e-trace-by-operation-id.kql` | Any — get operation_Id from user |

### How to get `operation_Id` from a user

Ask the user for:
1. The exact **time** of failure (HH:MM timezone)
2. Their **user ID / email**
3. The **URL** they were hitting

Then run the first block of `10-e2e-trace-by-operation-id.kql` with that info to find the `operation_Id`.

---

## 8. Sampling & Cost Guidance

| Environment | Sampling % | How to Change |
|---|---|---|
| Production | **10%** | `APPLICATIONINSIGHTS_SAMPLING_PERCENTAGE=10` |
| Staging | **25%** | `APPLICATIONINSIGHTS_SAMPLING_PERCENTAGE=25` |
| Development | **100%** | `APPLICATIONINSIGHTS_SAMPLING_PERCENTAGE=100` |

> **Important**: With 10% sampling, multiply observed counts by 10 to estimate actual volume.
> KQL does this automatically when you use `count()` — App Insights adjusts for sampling.

### Temporarily increase sampling for debugging

```bash
# Increase to 100% temporarily (remember to revert!)
az webapp config appsettings set \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg \
  --settings APPLICATIONINSIGHTS_SAMPLING_PERCENTAGE="100"

# Revert after debugging
az webapp config appsettings set \
  --name plte-fie-test2 \
  --resource-group ph-dev-rg \
  --settings APPLICATIONINSIGHTS_SAMPLING_PERCENTAGE="10"
```

---

## Related Files

| File | Purpose |
|---|---|
| [`../terraform/resources.tf`](../terraform/resources.tf) | Terraform — App Insights + AMPLS + diagnostic settings |
| [`../terraform/Architecture_Diagrams_Python_AI/Arch_Diagrams/diagrams/webappserviceFlow.md`](../terraform/Architecture_Diagrams_Python_AI/Arch_Diagrams/diagrams/webappserviceFlow.md) | End-to-end flow documentation |
| [`../terraform/Architecture_Diagrams_Python_AI/instructions.md`](../terraform/Architecture_Diagrams_Python_AI/instructions.md) | Architecture decisions |
| [`../APP_SERVICE_VS_ASE_DECISION.md`](../APP_SERVICE_VS_ASE_DECISION.md) | ASE vs App Service decision record |
