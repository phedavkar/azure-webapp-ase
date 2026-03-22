#!/usr/bin/env python3
"""
Enterprise Hub-Spoke Azure Architecture Diagram
================================================
Topology: Hub-Spoke with ExpressRoute to On-Premises
App: plte-fie-test2 (Java 17 / Tomcat 10.1) in ASEv3 (ILB)
Auth: Azure Entra ID + ESF (Enterprise Security Framework)
Secrets: Azure Key Vault (current) | HashiCorp Vault (future/strategic)
DNS: Private DNS Zone in Hub subscription (shared - app teams register records)
Monitoring: App Insights (Spoke) → AMPLS → LAW (Hub)

Key architecture decisions reflected:
- ASE is ILB mode → web app needs NO private endpoint
- Private DNS Zone lives in Hub (shared services) — spoke has no DNS forwarders
- App teams register A records in shared DNS zone for their web app / ASE
- Azure Key Vault = current solution (accessed via Managed Identity)
- HashiCorp Vault = future strategic replacement (shown with dashed border)
"""

import os
import subprocess
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices
from diagrams.azure.network import (
    VirtualNetworks,
    VirtualNetworkGateways,
    ExpressrouteCircuits,
    DNSPrivateZones,
    NetworkSecurityGroupsClassic,
)
from diagrams.azure.security import KeyVaults
from diagrams.azure.identity import (
    AzureActiveDirectory,
    ManagedIdentities,
    AppRegistrations
)
from diagrams.azure.analytics import LogAnalyticsWorkspaces, PrivateLinkServices
from diagrams.azure.devops import ApplicationInsights
from diagrams.azure.general import Resourcegroups
from diagrams.onprem.network import Internet
from diagrams.onprem.security import Vault
from diagrams.generic.device import Mobile
from diagrams.generic.blank import Blank

# ============================================================================
# GRAPH ATTRIBUTES
# ============================================================================
graph_attr = {
    "splines": "ortho",
    "nodesep": "1.2",
    "ranksep": "2.0",
    "fontsize": "16",
    "bgcolor": "#F5F5F5",
    "pad": "1.0",
    "compound": "true"
}

# Cluster styles
hub_vnet_attr = {
    "fontsize": "13",
    "bgcolor": "#E8EAF6",   # Indigo light
    "style": "rounded",
    "margin": "20",
    "pencolor": "#3949AB",
    "penwidth": "2"
}

spoke_vnet_attr = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",   # Blue light
    "style": "rounded",
    "margin": "20",
    "pencolor": "#1565C0",
    "penwidth": "2"
}

ase_attr = {
    "fontsize": "12",
    "bgcolor": "#BBDEFB",   # Blue medium
    "style": "rounded",
    "margin": "15",
    "pencolor": "#0D47A1",
    "penwidth": "2"
}

ase_subnet_attr = {
    "fontsize": "11",
    "bgcolor": "#90CAF9",   # Blue darker
    "style": "dashed",
    "margin": "12"
}

pe_subnet_attr = {
    "fontsize": "11",
    "bgcolor": "#B3E5FC",   # Light cyan
    "style": "dashed",
    "margin": "12"
}

hub_monitoring_attr = {
    "fontsize": "12",
    "bgcolor": "#F3E5F5",   # Purple light
    "style": "rounded",
    "margin": "15",
    "pencolor": "#6A1B9A",
    "penwidth": "2"
}

spoke_monitoring_attr = {
    "fontsize": "12",
    "bgcolor": "#FCE4EC",   # Pink light
    "style": "rounded",
    "margin": "15",
    "pencolor": "#AD1457",
    "penwidth": "2"
}

spoke_security_attr = {
    "fontsize": "12",
    "bgcolor": "#FFF8E1",   # Amber light
    "style": "rounded",
    "margin": "15",
    "pencolor": "#FF8F00",
    "penwidth": "2"
}

vault_future_attr = {
    "fontsize": "12",
    "bgcolor": "#FAFAFA",   # Near white — "not yet active"
    "style": "dashed",
    "margin": "15",
    "pencolor": "#757575",
    "penwidth": "2"
}

hub_dns_attr = {
    "fontsize": "12",
    "bgcolor": "#E8EAF6",   # Indigo light
    "style": "rounded",
    "margin": "15",
    "pencolor": "#3949AB",
    "penwidth": "2"
}

onprem_attr = {
    "fontsize": "13",
    "bgcolor": "#E8F5E9",   # Green light
    "style": "rounded",
    "margin": "20",
    "pencolor": "#2E7D32",
    "penwidth": "2"
}

entra_attr = {
    "fontsize": "12",
    "bgcolor": "#EDE7F6",   # Deep purple light
    "style": "rounded",
    "margin": "15",
    "pencolor": "#4527A0",
    "penwidth": "2"
}

# ============================================================================
# OUTPUT DIRECTORY
# ============================================================================
os.makedirs("Arch_Diagrams/diagrams", exist_ok=True)

# ============================================================================
# DIAGRAM
# ============================================================================
with Diagram(
    "ph-dev Enterprise Architecture\n(Hub-Spoke | ILB ASE | Entra ID | ESF | HashiCorp Vault Future)",
    filename="Arch_Diagrams/diagrams/ph_dev_architecture",
    direction="LR",
    graph_attr=graph_attr,
    show=False,
    outformat=["png", "dot"]
):

    # ========================================================================
    # TOP: USER
    # ========================================================================
    user = Mobile("User\n(Internal / VPN)")

    # ========================================================================
    # AZURE ENTRA ID (External Cloud Service)
    # ========================================================================
    with Cluster("Azure Entra ID (Cloud IDP)", graph_attr=entra_attr):
        entra_id = AzureActiveDirectory("Entra ID\nAuthentication")
        app_reg = AppRegistrations("App Registration\n(user claims in headers)")

    # ========================================================================
    # HUB SUBSCRIPTION (Shared Services)
    # ========================================================================
    with Cluster("Hub Subscription — Shared Services", graph_attr=hub_vnet_attr):

        # ExpressRoute
        expressroute = ExpressrouteCircuits("ExpressRoute\nCircuit")
        er_gateway = VirtualNetworkGateways("ExpressRoute\nGateway")

        # Private DNS Zone — SHARED, lives in Hub
        with Cluster(
            "Private DNS Zone (Shared)\nprivatelink.azurewebsites.net\n"
            "Policy: App teams register records here\n(No DNS forwarders in spoke)",
            graph_attr=hub_dns_attr
        ):
            private_dns = DNSPrivateZones(
                "ase-plte-fie\n.appserviceenvironment.net\n"
                "plte-fie-test2 A record\n→ ILB IP"
            )

        # Hub Monitoring
        with Cluster("Monitoring (Shared)", graph_attr=hub_monitoring_attr):
            law = LogAnalyticsWorkspaces(
                "Log Analytics\nlaw-shared-enterprise\n(Enterprise-wide)"
            )
            ampls = PrivateLinkServices(
                "AMPLS\nampls-shared-hub\n(Azure Monitor\nPrivate Link Scope)"
            )

    # ========================================================================
    # SPOKE SUBSCRIPTION (Application)
    # ========================================================================
    with Cluster("Spoke Subscription — Application Team", graph_attr=spoke_vnet_attr):

        # VNet label
        vnet = VirtualNetworks("vnet-app-spoke\n10.3.0.0/24")

        # NSG
        nsg = NetworkSecurityGroupsClassic("NSG\n(Deny public inbound)")

        # ----------------------------------------------------------------
        # ASE Subnet + App Service Environment
        # ----------------------------------------------------------------
        with Cluster("snet-ase  (10.3.0.0/26)", graph_attr=ase_subnet_attr):
            with Cluster(
                "App Service Env: ase-plte-fie\n[ ILBASEv3 | NO PUBLIC ACCESS ]\n"
                "No private endpoint needed — ILB provides private access",
                graph_attr=ase_attr
            ):
                web_app = AppServices(
                    "Web App\nplte-fie-test2\nJava 17 / Tomcat 10.1"
                )
                managed_id = ManagedIdentities("Managed Identity\n(System-assigned)")

        # ----------------------------------------------------------------
        # Private Endpoint Subnet — Reserved
        # ----------------------------------------------------------------
        with Cluster("snet-pe  (10.3.1.0/26)\nReserved for Future Private Endpoints",
                     graph_attr=pe_subnet_attr):
            pe_reserved = Blank("(Reserved)")

        # ----------------------------------------------------------------
        # Security & Config — Current (Azure Key Vault)
        # ----------------------------------------------------------------
        with Cluster("Security & Config (Current)", graph_attr=spoke_security_attr):
            key_vault = KeyVaults(
                "Azure Key Vault\nkv-app-spoke\n[CURRENT]\n(Secrets, Certs, API Keys)"
            )
            app_config = Blank(
                "App Configuration\nappconf-app-spoke\n(Env Vars, Feature Flags)"
            )

        # ----------------------------------------------------------------
        # HashiCorp Vault — Future / Strategic
        # ----------------------------------------------------------------
        with Cluster(
            "HashiCorp Vault  [FUTURE — Strategic]\n"
            "Central secrets platform (replaces Azure Key Vault)",
            graph_attr=vault_future_attr
        ):
            hashi_vault = Vault(
                "HashiCorp Vault\n(Future)\nEnterprise Secrets\nAll App Teams"
            )

        # ----------------------------------------------------------------
        # Monitoring (Spoke)
        # ----------------------------------------------------------------
        with Cluster("Monitoring (Spoke)", graph_attr=spoke_monitoring_attr):
            app_insights = ApplicationInsights(
                "Application Insights\nappi-app-spoke\n(Perf, Logs, Exceptions)"
            )

    # ========================================================================
    # ON-PREMISES (Private Cloud)
    # ========================================================================
    with Cluster("On-Premises (Private Cloud)", graph_attr=onprem_attr):
        esf = Resourcegroups(
            "ESF\n(Enterprise Security\nFramework)\nUser Roles &\nData Entitlements"
        )
        onprem_network = Internet("Private Cloud\nNetwork")

    # ========================================================================
    # CONNECTIONS / EDGES
    # ========================================================================

    # --- Authentication Flow (purple) ---
    user >> Edge(
        label="1. Login Request", color="#7B1FA2", style="bold"
    ) >> entra_id

    entra_id >> Edge(
        label="2. Auth Token +\nUser Claims", color="#7B1FA2", style="bold"
    ) >> web_app

    # --- Web App access via ILB (blue) ---
    user >> Edge(
        label="Access (via ILB\nprivate only)", color="#1565C0", style="bold"
    ) >> web_app

    # --- Authorization Flow to ESF (dark green) ---
    web_app >> Edge(
        label="3. User headers\n(auth request)", color="#1B5E20", style="bold"
    ) >> esf

    esf >> Edge(
        label="4. Returns Roles &\nEntitlements", color="#1B5E20", style="bold"
    ) >> web_app

    # --- ExpressRoute path to On-Premises (dark green dashed) ---
    er_gateway >> Edge(
        label="ExpressRoute\n(private)", color="#2E7D32", style="dashed"
    ) >> onprem_network

    onprem_network >> Edge(color="#2E7D32", style="dashed") >> esf

    # --- VNet Peering: Spoke → Hub (blue dashed) ---
    vnet >> Edge(
        label="VNet Peering", color="#1565C0", style="dashed"
    ) >> er_gateway

    # --- DNS Registration: ASE/WebApp → Shared Private DNS Zone in Hub ---
    web_app >> Edge(
        label="DNS record\nregistered here\n(A record → ILB IP)",
        color="#546E7A", style="dotted"
    ) >> private_dns

    # --- Secret Management — Current: Web App → Azure Key Vault (orange) ---
    web_app >> Edge(
        label="5a. Fetch Secrets\n(Managed Identity)\n[CURRENT]",
        color="#E65100", style="bold"
    ) >> key_vault

    # --- App Configuration (purple) ---
    web_app >> Edge(
        label="5b. Fetch Config\n(Managed Identity)", color="#6A1B9A"
    ) >> app_config

    # --- Secret Management — Future: Web App → HashiCorp Vault (gray dashed) ---
    web_app >> Edge(
        label="5c. Fetch Secrets\n[FUTURE — Strategic]",
        color="#757575", style="dashed"
    ) >> hashi_vault

    # --- Monitoring Flow (red dotted) ---
    web_app >> Edge(
        label="6. Telemetry &\nApp Logs", color="#B71C1C", style="dotted"
    ) >> app_insights

    app_insights >> Edge(
        label="Private Link\n(AMPLS)", color="#B71C1C", style="dotted"
    ) >> ampls

    ampls >> Edge(
        label="Enterprise Logs", color="#B71C1C", style="dotted"
    ) >> law

    # --- NSG association ---
    nsg >> Edge(
        label="Applied to\nsubnets", color="#546E7A", style="dotted"
    ) >> vnet

    # --- App Registration linked to Entra ID ---
    app_reg >> Edge(color="#4527A0", style="dotted") >> entra_id


# ============================================================================
# CONVERT TO DRAW.IO
# ============================================================================
if __name__ == "__main__":
    print("\n✅ Diagram PNG and DOT generated!")
    print("📁 Output files:")
    print("   - Arch_Diagrams/diagrams/ph_dev_architecture.png")
    print("   - Arch_Diagrams/diagrams/ph_dev_architecture.dot")
    print("\n🔄 Converting to draw.io format...")

    try:
        subprocess.run([
            "graphviz2drawio",
            "Arch_Diagrams/diagrams/ph_dev_architecture.dot",
            "-o",
            "Arch_Diagrams/diagrams/ph_dev_architecture.drawio"
        ], check=True)
        print("✅ Arch_Diagrams/diagrams/ph_dev_architecture.drawio created!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  graphviz2drawio conversion failed: {e}")

    print("\n📊 All diagram files ready in: Arch_Diagrams/diagrams/")
    print("   Open with: code Arch_Diagrams/diagrams/ph_dev_architecture.drawio")
    print("\n🔑 Flow Summary:")
    print("   1. User → Entra ID (Authentication)")
    print("   2. Entra ID → Web App (Token + User Claims in Headers)")
    print("   3. Web App → ESF via ExpressRoute (Authorization Request)")
    print("   4. ESF → Web App (Roles & Data Entitlements)")
    print("   5a. Web App → Azure Key Vault (Secrets via Managed Identity) [CURRENT]")
    print("   5b. Web App → App Configuration (Config via Managed Identity)")
    print("   5c. Web App → HashiCorp Vault (Secrets) [FUTURE — Strategic]")
    print("   6. Web App → App Insights → AMPLS → LAW (Monitoring)")
    print("\n🌐 DNS:")
    print("   - Private DNS Zone in Hub subscription (shared)")
    print("   - App teams register A records (ASE ILB IP) here")
    print("   - Spoke has no DNS forwarders — cannot host own DNS zone")
    print("\n🔒 Key Architecture Decisions:")
    print("   - ASE ILB mode: web app needs NO private endpoint")
    print("   - snet-pe is reserved for future private endpoints")
    print("   - HashiCorp Vault will replace Azure Key Vault (strategic)")
