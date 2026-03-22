#!/usr/bin/env python3
"""
Enterprise Hub-Spoke Azure Architecture Diagram
================================================
Topology: Hub-Spoke with ExpressRoute to On-Premises
App: plte-fie-test2 (Java 17 / Tomcat 10.1) in ASEv3 (ILB)
Auth: Azure Entra ID + ESF (Enterprise Security Framework)
Monitoring: App Insights (Spoke) → AMPLS → LAW (Hub)
"""

import os
import subprocess
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices
from diagrams.azure.network import (
    VirtualNetworks,
    Subnets,
    VirtualNetworkGateways,
    ExpressrouteCircuits,
    DNSPrivateZones,
    NetworkSecurityGroupsClassic,
    PrivateEndpoint
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
from diagrams.onprem.database import Oracle
from diagrams.onprem.network import Internet
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
    "ph-dev Enterprise Architecture\n(Hub-Spoke | ILB ASE | Entra ID | ESF)",
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
    with Cluster("Hub Subscription (Shared Services)", graph_attr=hub_vnet_attr):

        # ExpressRoute
        expressroute = ExpressrouteCircuits("ExpressRoute\nCircuit")
        er_gateway = VirtualNetworkGateways("ExpressRoute\nGateway")

        # Hub Monitoring
        with Cluster("Monitoring (Shared)", graph_attr=hub_monitoring_attr):
            law = LogAnalyticsWorkspaces("Log Analytics\nlaw-shared-enterprise\n(Enterprise-wide)")
            ampls = PrivateLinkServices("AMPLS\nampls-shared-hub\n(Azure Monitor\nPrivate Link Scope)")

    # ========================================================================
    # SPOKE SUBSCRIPTION (Application)
    # ========================================================================
    with Cluster("Spoke Subscription (Application)", graph_attr=spoke_vnet_attr):

        # VNet label
        vnet = VirtualNetworks("vnet-app-spoke\n10.3.0.0/24")

        # NSG
        nsg = NetworkSecurityGroupsClassic("NSG\n(Deny public inbound)")

        # ----------------------------------------------------------------
        # ASE Subnet + App Service Environment
        # ----------------------------------------------------------------
        with Cluster("ASE Subnet: snet-ase (10.3.0.0/26)", graph_attr=ase_subnet_attr):
            with Cluster("App Service Env: ase-plte-fie\n[ ILBASEv3 | NO PUBLIC ACCESS ]", graph_attr=ase_attr):
                web_app = AppServices("Web App\nplte-fie-test2\nJava 17 / Tomcat 10.1")
                managed_id = ManagedIdentities("Managed Identity\n(System-assigned)")

        # ----------------------------------------------------------------
        # Private Endpoint Subnet
        # ----------------------------------------------------------------
        with Cluster("PE Subnet: snet-pe (10.3.1.0/26)", graph_attr=pe_subnet_attr):
            pe_kv = PrivateEndpoint("PE: Key Vault")
            pe_appcfg = PrivateEndpoint("PE: App Config")

        # ----------------------------------------------------------------
        # Security & Config
        # ----------------------------------------------------------------
        with Cluster("Security & Config (Spoke)", graph_attr=spoke_security_attr):
            key_vault = KeyVaults("Key Vault\nkv-app-spoke\n(Secrets, Certs, API Keys)")
            app_config = Blank("App Configuration\nappconf-app-spoke\n(Env Vars, Feature Flags)")

        # ----------------------------------------------------------------
        # Monitoring (Spoke)
        # ----------------------------------------------------------------
        with Cluster("Monitoring (Spoke)", graph_attr=spoke_monitoring_attr):
            app_insights = ApplicationInsights("Application Insights\nappi-app-spoke\n(Perf, Logs, Exceptions)")

        # Private DNS Zone
        private_dns = DNSPrivateZones("Private DNS Zone\nase-plte-fie.\nappserviceenvironment.net")

    # ========================================================================
    # ON-PREMISES (Private Cloud)
    # ========================================================================
    with Cluster("On-Premises (Private Cloud)", graph_attr=onprem_attr):
        esf = Resourcegroups("ESF\n(Enterprise Security\nFramework)\nUser Roles &\nData Entitlements")
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

    # --- Web App access (blue) ---
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

    # --- ExpressRoute path to ESF (dark green dashed) ---
    er_gateway >> Edge(
        label="ExpressRoute\n(private)", color="#2E7D32", style="dashed"
    ) >> onprem_network

    onprem_network >> Edge(color="#2E7D32", style="dashed") >> esf

    # --- VNet Peering (blue dashed) ---
    vnet >> Edge(
        label="VNet Peering", color="#1565C0", style="dashed"
    ) >> er_gateway

    # --- Secret Management (orange) ---
    managed_id >> Edge(
        label="Managed Identity\nauth", color="#E65100", style="bold"
    ) >> pe_kv

    pe_kv >> Edge(color="#E65100") >> key_vault

    web_app >> Edge(
        label="5. Fetch Secrets", color="#E65100"
    ) >> pe_kv

    # --- App Configuration (purple) ---
    web_app >> Edge(
        label="6. Fetch Config", color="#6A1B9A"
    ) >> pe_appcfg

    pe_appcfg >> Edge(color="#6A1B9A") >> app_config

    # --- Monitoring Flow (red dotted) ---
    web_app >> Edge(
        label="7. Telemetry &\nApp Logs", color="#B71C1C", style="dotted"
    ) >> app_insights

    app_insights >> Edge(
        label="Private Link\n(AMPLS)", color="#B71C1C", style="dotted"
    ) >> ampls

    ampls >> Edge(
        label="Enterprise Logs", color="#B71C1C", style="dotted"
    ) >> law

    # --- DNS Resolution ---
    web_app >> Edge(
        label="DNS Resolution", color="#546E7A", style="dotted"
    ) >> private_dns

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
    print("   5. Web App → Key Vault (Secrets via Managed Identity)")
    print("   6. Web App → App Configuration (Config via Managed Identity)")
    print("   7. Web App → App Insights → AMPLS → LAW (Monitoring)")
