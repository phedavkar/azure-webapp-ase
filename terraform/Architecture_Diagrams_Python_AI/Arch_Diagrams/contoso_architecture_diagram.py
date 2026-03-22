#!/usr/bin/env python3
"""
Generate Azure Architecture Diagram for Contoso 3-Tier Application
Based on instructions.md specifications
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.azure.network import (
    VirtualNetworks, 
    Subnets, 
    Firewall, 
    ApplicationGateway, 
    FrontDoors,
    NetworkSecurityGroupsClassic,
    RouteTables,
    PrivateEndpoint
)
from diagrams.azure.compute import (
    AppServices,
    FunctionApps,
    ContainerInstances
)
from diagrams.azure.database import (
    SQLServers,
    SQLDatabases
)
from diagrams.azure.storage import (
    StorageAccounts,
    BlobStorage
)
from diagrams.azure.security import (
    KeyVaults
)
from diagrams.azure.integration import (
    ServiceBus
)
from diagrams.azure.analytics import (
    LogAnalyticsWorkspaces
)
from diagrams.azure.devops import (
    ApplicationInsights
)
from diagrams.azure.identity import (
    ManagedIdentities
)
from diagrams.generic.device import Mobile
from diagrams.generic.blank import Blank

# Graph attributes for better layout
graph_attr = {
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.5",
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5"
}

# Cluster attributes for different tiers
vnet_attr = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",  # Light Blue
    "style": "rounded",
    "margin": "20"
}

frontend_attr = {
    "fontsize": "12",
    "bgcolor": "#BBDEFB",  # Medium Blue
    "style": "rounded",
    "margin": "15"
}

backend_attr = {
    "fontsize": "12",
    "bgcolor": "#C8E6C9",  # Light Green
    "style": "rounded",
    "margin": "15"
}

data_attr = {
    "fontsize": "12",
    "bgcolor": "#FFF9C4",  # Light Yellow
    "style": "rounded",
    "margin": "15"
}

monitoring_attr = {
    "fontsize": "12",
    "bgcolor": "#F8BBD0",  # Light Pink
    "style": "rounded",
    "margin": "15"
}

# Create diagram
with Diagram(
    "Contoso 3-Tier Azure Architecture",
    filename="Arch_Diagrams/diagrams/contoso_architecture",
    direction="TB",
    graph_attr=graph_attr,
    show=False,
    outformat=["png", "dot"]
):
    
    # ========================================================================
    # EXTERNAL USERS
    # ========================================================================
    users = Mobile("Users")
    
    # ========================================================================
    # MAIN VNET CLUSTER
    # ========================================================================
    with Cluster("VNet: vnet-contoso-auea-001 (10.10.0.0/16)", graph_attr=vnet_attr):
        
        # ====================================================================
        # FRONTEND SUBNET (10.10.1.0/24)
        # ====================================================================
        with Cluster("Frontend Subnet (10.10.1.0/24)", graph_attr=frontend_attr):
            
            # Front Door (outside VNet but shown for flow)
            front_door = FrontDoors("Front Door\nafd-contoso")
            
            # Application Gateway with WAF
            app_gateway = ApplicationGateway("App Gateway (WAF)\nagw-contoso")
            
            # Web App
            web_app = AppServices("Web App\nph-frontend-portal\nASP: asp-contoso-prod")
            
            # NSG for frontend
            frontend_nsg = NetworkSecurityGroupsClassic("NSG-Frontend")
            
        # ====================================================================
        # BACKEND SUBNET (10.10.2.0/24)
        # ====================================================================
        with Cluster("Backend Subnet (10.10.2.0/24)", graph_attr=backend_attr):
            
            # Backend API
            backend_api = AppServices("Backend API\napp-order-api\nASP: asp-contoso-backend")
            
            # Function App
            func_app = FunctionApps("Function App\nfunc-order-processor")
            
            # Service Bus
            service_bus = ServiceBus("Service Bus\nsb-contoso-orders")
            
            # NSG for backend
            backend_nsg = NetworkSecurityGroupsClassic("NSG-Backend")
        
        # ====================================================================
        # DATA SUBNET (10.10.3.0/24)
        # ====================================================================
        with Cluster("Data Subnet (10.10.3.0/24)", graph_attr=data_attr):
            
            # SQL Server and Database
            sql_server = SQLServers("SQL Server\nsqlsrv-contoso")
            sql_db = SQLDatabases("SQL Database\nsqldb-orders")
            
            # Storage Account
            storage = StorageAccounts("Storage Account\nstcontosodata001")
            
            # Key Vault
            key_vault = KeyVaults("Key Vault\nkv-contoso-prod")
            
            # Private Endpoints
            sql_pe = Blank("PE-SQL")
            storage_pe = Blank("PE-Storage")
            kv_pe = Blank("PE-KeyVault")
            
            # NSG for data
            data_nsg = NetworkSecurityGroupsClassic("NSG-Data")
        
        # ====================================================================
        # FIREWALL (Bottom Left)
        # ====================================================================
        firewall = Firewall("Azure Firewall\nazfw-contoso")
        route_table = RouteTables("Route Table\n(Default → Firewall)")
    
    # ========================================================================
    # MONITORING (Outside VNet)
    # ========================================================================
    with Cluster("Monitoring", graph_attr=monitoring_attr):
        log_analytics = LogAnalyticsWorkspaces("Log Analytics\nlaw-contoso-prod")
        app_insights = ApplicationInsights("Application Insights\nappi-contoso")
    
    # ========================================================================
    # CONNECTIONS / EDGES
    # ========================================================================
    
    # Users to Front Door
    users >> Edge(label="https") >> front_door
    
    # Front Door to Application Gateway
    front_door >> Edge(label="route") >> app_gateway
    
    # Application Gateway to Web App
    app_gateway >> Edge(label="route") >> web_app
    
    # Web App to Backend API
    web_app >> Edge(label="api call") >> backend_api
    
    # Backend API to SQL Database (via private endpoint)
    backend_api >> Edge(label="query") >> sql_pe
    sql_pe >> Edge() >> sql_db
    
    # Backend API to Storage (via private endpoint)
    backend_api >> Edge(label="access") >> storage_pe
    storage_pe >> Edge() >> storage
    
    # Backend API to Key Vault (via private endpoint)
    backend_api >> Edge(label="secrets") >> kv_pe
    kv_pe >> Edge() >> key_vault
    
    # Function App to Service Bus
    func_app >> Edge(label="message") >> service_bus
    
    # Service Bus to SQL Database
    service_bus >> Edge(label="query") >> sql_db
    
    # Service Bus to Key Vault
    service_bus >> Edge(label="secrets") >> key_vault
    
    # Web App to Key Vault
    web_app >> Edge(label="secrets") >> key_vault
    
    # All apps to Log Analytics (Diagnostic logs)
    web_app >> Edge(label="logs", style="dotted") >> log_analytics
    backend_api >> Edge(label="logs", style="dotted") >> log_analytics
    func_app >> Edge(label="logs", style="dotted") >> log_analytics
    
    # All apps to Application Insights (Monitoring)
    web_app >> Edge(label="metrics", style="dotted") >> app_insights
    backend_api >> Edge(label="metrics", style="dotted") >> app_insights
    func_app >> Edge(label="metrics", style="dotted") >> app_insights
    
    # Firewall connections (outbound traffic flow)
    web_app >> Edge(label="outbound", style="dashed") >> firewall
    backend_api >> Edge(label="outbound", style="dashed") >> firewall
    func_app >> Edge(label="outbound", style="dashed") >> firewall


if __name__ == "__main__":
    print("✅ Diagram generation complete!")
    print("📁 Output files:")
    print("   - Arch_Diagrams/diagrams/contoso_architecture.png")
    print("   - Arch_Diagrams/diagrams/contoso_architecture.dot")
    print("\n🔄 Converting to draw.io format...")
    
    import subprocess
    import os
    
    try:
        # Convert DOT to DRAWIO
        subprocess.run([
            "graphviz2drawio",
            "Arch_Diagrams/diagrams/contoso_architecture.dot",
            "-o",
            "Arch_Diagrams/diagrams/contoso_architecture.drawio"
        ], check=True)
        print("✅ Arch_Diagrams/diagrams/contoso_architecture.drawio created!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Note: graphviz2drawio conversion failed: {e}")
        print("   You can manually convert the .dot file using online tools or draw.io")
    
    print("\n📊 Diagram files ready!")
    print("   Open with: code Arch_Diagrams/diagrams/contoso_architecture.drawio")
