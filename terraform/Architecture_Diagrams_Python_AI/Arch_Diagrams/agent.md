# Agent Instructions: Azure Architecture Diagram Generation

## Overview
This workspace contains tools to automatically generate Azure architecture diagrams from Infrastructure-as-Code (Terraform, Bicep, ARM templates). The diagrams are created using Python's `diagrams` library, rendered with GraphViz, and converted to editable draw.io format.

---

## Environment Setup

### Python Environment
- **Location**: `/Users/prasanna/Documents/source/project-webapp/terraform/Architecture_Diagrams_Python_AI/venv`
- **Python Version**: 3.13+ (or your installed version)
- **Activation**: `source venv/bin/activate` (macOS/Linux)
- **Installation**: See setup instructions below (pygraphviz requires special handling)

### Installed Packages (Exact Versions)
```
diagrams==0.24.4
graphviz==0.20.3
pygraphviz==1.14
graphviz2drawio==1.1.0
puremagic==1.30
svg.path==7.0
```

### Initial Setup from Scratch (macOS)
```bash
# 1. Navigate to workspace
cd /Users/prasanna/Documents/source/project-webapp/terraform/Architecture_Diagrams_Python_AI

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install GraphViz via Homebrew (required for pygraphviz)
brew install graphviz

# 4. Install pygraphviz with GraphViz paths
pip install --config-settings="--global-option=build_ext" --config-settings="--global-option=-I$(brew --prefix graphviz)/include" --config-settings="--global-option=-L$(brew --prefix graphviz)/lib" pygraphviz

# 5. Install remaining packages
pip install diagrams graphviz graphviz2drawio puremagic svg.path

# OR use requirements.txt (but pygraphviz needs special install first)
# pip install -r requirements.txt
```

### GraphViz Installation
- **Location**: `/usr/local/bin/dot` (via Homebrew)
- **Version**: Latest (check with `dot -V`)
- **Verification**: 
  ```bash
  which dot
  dot -V
  ```

### VS Code Extensions
- **Draw.io**: `hediet.vscode-drawio` - For viewing/editing .drawio files
- SVG file association configured for draw.io

---

## File Structure

```
/Users/prasanna/Documents/source/project-webapp/
├── terraform/
│   ├── Architecture_Diagrams_Python_AI/
│   │   ├── venv/                           # Python virtual environment
│   │   ├── requirements.txt                # Python package dependencies
│   │   ├── Arch_Diagrams/
│   │   │   ├── diagrams/                   # Output directory for all generated diagrams
│   │   │   │   ├── *.png                   # PNG image outputs
│   │   │   │   ├── *.dot                   # GraphViz DOT source files
│   │   │   │   └── *.drawio                # Editable draw.io files
│   │   │   ├── contoso_architecture.py     # Manual diagram from instructions.md
│   │   │   ├── terraform_to_diagram.py     # Terraform parser & diagram generator
│   │   │   ├── bicep_lab01_diagram.py      # Bicep lab01 specific generator
│   │   │   ├── arm_iis_sql_diagram.py      # ARM template (3-tier IIS+SQL) generator
│   │   │   ├── README.md                   # Complete setup & usage documentation
│   │   │   ├── script.md                   # YouTube video script
│   │   │   └── agent.md                    # THIS FILE - Agent instructions
│   │   └── External Repositories (git cloned):
│   │       ├── terraform-demo/             # Terraform demo with 19 Azure resources
│   │       ├── avm-bicep-labs/             # Azure Verified Modules Bicep labs
│   │       └── azure-quickstart-templates/ # Azure quickstart ARM/Bicep templates
│   ├── main.tf
│   ├── variables.tf
│   ├── resources.tf
│   └── terraform.tfvars
├── src/                            # Your Java/Tomcat application source
└── README.md
```

---

## Diagram Generation Workflow

### Complete Process (3 Steps)

#### Step 1: Create Python Diagram Script
- Import required Azure components from `diagrams.azure.*`
- Use proper icon names (e.g., `PublicIpAddresses` not `PublicIPAddresses`)
- Configure graph attributes for layout:
  ```python
  graph_attr = {
      "splines": "ortho",      # Orthogonal lines
      "nodesep": "0.8",        # Node spacing
      "ranksep": "1.2",        # Rank spacing
      "fontsize": "14",
      "bgcolor": "white",
      "pad": "0.5"
  }
  ```
- Use Cluster for logical grouping (VNets, Subnets, Resource Groups)
- Set different background colors for different tiers/clusters
- Set output format: `outformat=["png", "dot"]`

#### Step 2: Run with GraphViz in PATH (macOS)
```bash
cd /Users/prasanna/Documents/source/project-webapp/terraform/Architecture_Diagrams_Python_AI
source venv/bin/activate
python Arch_Diagrams/<script_name>.py
```

GraphViz is automatically in PATH via Homebrew, no manual PATH setup needed.

#### Step 3: Convert DOT to Draw.io
This happens automatically in the script using:
```python
subprocess.run([
    "graphviz2drawio", 
    "Arch_Diagrams/diagrams/<name>.dot", 
    "-o", 
    "Arch_Diagrams/diagrams/<name>.drawio"
], check=True)
```

---

## Parsing Infrastructure-as-Code

### Terraform Parsing
**File**: `Arch_Diagrams/terraform_to_diagram.py`

**Usage**:
```bash
python Arch_Diagrams/terraform_to_diagram.py "/Users/prasanna/Documents/source/project-webapp/terraform/main.tf" "ph-dev"
```

**What it does**:
1. Reads .tf file(s)
2. Uses regex to extract `resource "type" "name"` blocks
3. Detects relationships via:
   - `depends_on` attributes
   - Resource references (e.g., `azurerm_subnet.example.id`)
4. Groups resources by VNet/subnet
5. Generates diagram with connections

**Example**: Parse your Terraform for ph-dev-webapp infrastructure

### Bicep Parsing
**File**: `Arch_Diagrams/bicep_lab01_diagram.py` (lab-specific)

**Challenges**:
- Bicep uses module references (harder to parse than Terraform's flat structure)
- Often requires manual inspection of module parameters
- Best approach: Create scenario-specific generators

### ARM Template Parsing
**File**: `Arch_Diagrams/arm_iis_sql_diagram.py`

**Approach**:
- Read ARM template JSON
- Extract resources array
- Map ARM resource types to diagrams icons
- Build connections based on `dependsOn` and resource references

---

## Color Coding for Tiers

Use different background colors to distinguish architectural tiers:

```python
# Frontend Tier
frontend_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",  # Light Blue
    "style": "rounded",
    "margin": "15"
}

# Database Tier
database_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#FFF3E0",  # Light Orange
    "style": "rounded",
    "margin": "15"
}

# Load Balancer
lb_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#F3E5F5",  # Light Purple
    "style": "rounded",
    "margin": "15"
}

# Availability Set
avset_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E8F5E9",  # Light Green
    "style": "rounded",
    "margin": "15"
}
```

Apply to clusters:
```python
with Cluster("Frontend Subnet", graph_attr=frontend_cluster_attr):
    # components
```

---

## Common Azure Icon Imports

```python
from diagrams import Diagram, Cluster, Edge

# Compute
from diagrams.azure.compute import VM, AvailabilitySets, FunctionApps, ContainerInstances, AppServices

# Network
from diagrams.azure.network import (
    VirtualNetworks, Subnets, LoadBalancers, 
    ApplicationGateway, FrontDoors, 
    NetworkSecurityGroupsClassic, 
    PublicIpAddresses, NetworkInterfaces,
    PrivateEndpoint, DNSPrivateZones
)

# Database
from diagrams.azure.database import SQLServers, SQLDatabases, CosmosDB

# Storage
from diagrams.azure.storage import StorageAccounts, BlobStorage

# Security
from diagrams.azure.security import KeyVaults

# Identity
from diagrams.azure.identity import ManagedIdentities

# Integration
from diagrams.azure.integration import ServiceBus

# Monitoring
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights
```

**Important**: Always check actual available class names using:
```python
from diagrams.azure import network
print([x for x in dir(network) if not x.startswith('_')])
```

---

## Troubleshooting

### GraphViz Not Found
**Error**: `ExecutableNotFound: failed to execute 'dot'`

**Solution** (macOS):
```bash
brew install graphviz
which dot
```

Verify installation:
```bash
dot -V
```

### Import Errors
**Error**: `cannot import name 'PublicIPAddresses'`

**Solution**: Check exact class name (case-sensitive):
- Correct: `PublicIpAddresses`
- Wrong: `PublicIPAddresses`

### pygraphviz Installation Issues
**Error**: `error: command 'gcc' failed with exit status 1`

**Solution** (macOS):
```bash
# Install build tools
xcode-select --install

# Install via Homebrew graphviz first
brew install graphviz

# Then install pygraphviz with correct paths
pip install --config-settings="--global-option=build_ext" --config-settings="--global-option=-I$(brew --prefix graphviz)/include" --config-settings="--global-option=-L$(brew --prefix graphviz)/lib" pygraphviz
```

### Cluttered Layout
**Issue**: Auto-generated diagrams have messy layouts

**Solutions**:
1. Adjust graph attributes (`nodesep`, `ranksep`)
2. Use `direction="TB"` or `"LR"`
3. Simplify cluster nesting
4. **Best approach**: Auto-generate, then manually refine in draw.io

---

## Output Files

Each diagram generation produces 3 files:

1. **PNG** - Static image for documentation/presentations
2. **DOT** - GraphViz source (text format, can be version controlled)
3. **DRAWIO** - Editable diagram for manual refinement

**Location**: `/Users/prasanna/Documents/source/project-webapp/terraform/Architecture_Diagrams_Python_AI/Arch_Diagrams/diagrams/`

**Typical sizes**:
- PNG: ~100-200 KB
- DOT: ~10-15 KB
- DRAWIO: ~120-300 KB

---

## Example Diagrams to Generate

### 1. Your ph-dev Infrastructure
```bash
cd /Users/prasanna/Documents/source/project-webapp/terraform/Architecture_Diagrams_Python_AI
source venv/bin/activate
python Arch_Diagrams/terraform_to_diagram.py "/Users/prasanna/Documents/source/project-webapp/terraform/main.tf" "ph-dev"
```

### 2. Contoso Architecture (Manual)
```bash
python Arch_Diagrams/contoso_architecture.py
```

### 3. Custom Java/Tomcat App Service Architecture
Create new file: `Arch_Diagrams/ph_dev_webapp_diagram.py`

---

## Quick Start Commands (macOS)

```bash
# Navigate to workspace
cd /Users/prasanna/Documents/source/project-webapp/terraform/Architecture_Diagrams_Python_AI

# Activate virtual environment
source venv/bin/activate

# Generate Terraform diagram
python Arch_Diagrams/terraform_to_diagram.py "/Users/prasanna/Documents/source/project-webapp/terraform/resources.tf" "ph-dev"

# View generated files
ls -la Arch_Diagrams/diagrams/

# Open in VS Code
code Arch_Diagrams/diagrams/ph_dev_arch.drawio

# Deactivate when done
deactivate
```

---

## Key Principles

1. **Auto-generate first, refine later**: Use Python scripts to get 95% of the diagram, then manually polish in draw.io
2. **Version control DOT files**: They're text-based and show changes clearly
3. **Color code tiers**: Makes diagrams easier to understand at a glance
4. **Use clusters liberally**: Group related resources (VNets, Subnets, Resource Groups)
5. **Edge labels**: Label connections with protocols/ports for clarity
6. **Homebrew for dependencies**: macOS-friendly package management

---