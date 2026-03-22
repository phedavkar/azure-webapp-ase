/*
  Azure Web App Service with App Service Environment (ASE)
  Resource Definitions
*/

# ============================================================================
# LOCAL VARIABLES FOR NAMING
# ============================================================================

locals {
  # Clean up names for resources (remove dashes, convert to lowercase)
  resource_group_name           = var.resource_group_name != "" ? var.resource_group_name : "rg-${var.project_name}-${var.environment}"
  vnet_name                     = var.vnet_name != "" ? var.vnet_name : "vnet-${var.project_name}-${var.environment}"
  ase_subnet_name               = var.ase_subnet_name != "" ? var.ase_subnet_name : "subnet-ase-${var.environment}"
  private_endpoints_subnet_name = var.private_endpoints_subnet_name != "" ? var.private_endpoints_subnet_name : "subnet-pe-${var.environment}"
  app_gateway_subnet_name       = var.app_gateway_subnet_name != "" ? var.app_gateway_subnet_name : "subnet-appgw-${var.environment}"
  ase_name                      = var.ase_name != "" ? var.ase_name : "ase-${var.project_name}-${var.environment}"
  app_service_plan_name         = var.app_service_plan_name != "" ? var.app_service_plan_name : "asp-${var.project_name}-${var.environment}"
  web_app_name                  = var.web_app_name != "" ? var.web_app_name : "webapp-${var.project_name}-${var.environment}"
  app_insights_name             = var.app_insights_name != "" ? var.app_insights_name : "appinsights-${var.project_name}-${var.environment}"
  log_analytics_name            = var.log_analytics_name != "" ? var.log_analytics_name : "law-${var.project_name}-${var.environment}"
  key_vault_name                = var.key_vault_name != "" ? var.key_vault_name : "kv${replace(var.project_name, "-", "")}${var.environment}"
  storage_account_name          = var.storage_account_name != "" ? var.storage_account_name : "sa${replace(var.project_name, "-", "")}${var.environment}"

  # Combine tags
  tags = merge(
    var.common_tags,
    {
      "Environment" = var.environment
      "Project"     = var.project_name
      "CreatedBy"   = "Terraform"
      "CreatedDate" = timestamp()
    }
  )
}

# ============================================================================
# RESOURCE GROUP
# ============================================================================

resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# ============================================================================
# NETWORKING - VIRTUAL NETWORK & SUBNETS
# ============================================================================

resource "azurerm_virtual_network" "main" {
  name                = local.vnet_name
  address_space       = var.vnet_address_space
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

# ASE Subnet
resource "azurerm_subnet" "ase" {
  name                 = local.ase_subnet_name
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.ase_subnet_address_prefix]

  service_endpoints = [
    "Microsoft.KeyVault",
    "Microsoft.Sql",
    "Microsoft.Storage"
  ]

  delegation {
    name = "delegation"
    service_delegation {
      name = "Microsoft.Web/serverFarms"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/action"
      ]
    }
  }
}

# Private Endpoints Subnet
resource "azurerm_subnet" "private_endpoints" {
  name                 = local.private_endpoints_subnet_name
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.private_endpoints_subnet_address_prefix]

  private_endpoint_network_policies_enabled = true
}

# Application Gateway Subnet (optional, for external ASE)
resource "azurerm_subnet" "app_gateway" {
  count                = var.ase_kind == "ASEv3" ? 1 : 0
  name                 = local.app_gateway_subnet_name
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.app_gateway_subnet_address_prefix]
}

# ============================================================================
# NETWORKING - NETWORK SECURITY GROUPS
# ============================================================================

resource "azurerm_network_security_group" "ase" {
  name                = "nsg-ase-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "10.0.0.0/8"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "10.0.0.0/8"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAzureInfrastructure"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "AzureCloud"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowAllOutbound"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "ase" {
  subnet_id                 = azurerm_subnet.ase.id
  network_security_group_id = azurerm_network_security_group.ase.id
}

# ============================================================================
# APP SERVICE ENVIRONMENT (ASE v3)
# ============================================================================

resource "azurerm_app_service_environment_v3" "main" {
  name                = local.ase_name
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.ase.id
  location            = azurerm_resource_group.main.location

  # Internal Load Balancer for ILBASEv3
  internal_load_balancing_mode = var.ase_kind == "ILBASEv3" ? "Web, Publishing" : "None"

  # Availability zones for high availability
  zone_redundant = var.ase_zone_redundant

  tags = local.tags

  depends_on = [azurerm_subnet_network_security_group_association.ase]

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# ============================================================================
# APP SERVICE PLAN
# ============================================================================

resource "azurerm_service_plan" "main" {
  name                       = local.app_service_plan_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  os_type                    = var.app_service_plan_is_linux ? "Linux" : "Windows"
  sku_name                   = var.app_service_plan_sku
  app_service_environment_id = azurerm_app_service_environment_v3.main.id

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# ============================================================================
# WEB APP
# ============================================================================

# Windows Web App
resource "azurerm_windows_web_app" "main" {
  count               = var.app_service_plan_is_linux ? 0 : 1
  name                = local.web_app_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = var.web_app_https_only

  site_config {
    always_on             = var.web_app_always_on
    http2_enabled         = var.web_app_http2_enabled
    managed_pipeline_mode = "Integrated"
    websockets_enabled    = true
    load_balancing_mode   = "LeastRequests"

    application_stack {
      current_stack  = "dotnet"
      dotnet_version = "v6.0"
    }
  }

  app_settings = merge(
    var.web_app_app_settings,
    var.enable_app_insights ? {
      "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main[0].connection_string
      "APPLICATIONINSIGHTS_ENABLE_AGENT"      = "true"
    } : {}
  )

  dynamic "connection_string" {
    for_each = var.web_app_connection_strings
    content {
      name  = connection_string.key
      type  = connection_string.value.type
      value = connection_string.value.value
    }
  }

  dynamic "identity" {
    for_each = var.enable_managed_identity ? [1] : []
    content {
      type = "SystemAssigned"
    }
  }

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_service_plan.main]
}

# Linux Web App (alternative)
resource "azurerm_linux_web_app" "main" {
  count               = var.app_service_plan_is_linux ? 1 : 0
  name                = local.web_app_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = var.web_app_https_only

  site_config {
    always_on          = var.web_app_always_on
    http2_enabled      = var.web_app_http2_enabled
    websockets_enabled = true

    application_stack {
      docker_image_name   = var.web_app_runtime_stack
      docker_registry_url = "https://index.docker.io"
    }
  }

  app_settings = merge(
    var.web_app_app_settings,
    var.enable_app_insights ? {
      "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.main[0].connection_string
    } : {}
  )

  dynamic "connection_string" {
    for_each = var.web_app_connection_strings
    content {
      name  = connection_string.key
      type  = connection_string.value.type
      value = connection_string.value.value
    }
  }

  dynamic "identity" {
    for_each = var.enable_managed_identity ? [1] : []
    content {
      type = "SystemAssigned"
    }
  }

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_service_plan.main]
}

# ============================================================================
# LOGGING & MONITORING
# ============================================================================

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  count               = var.enable_log_analytics ? 1 : 0
  name                = local.log_analytics_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = var.log_analytics_sku
  retention_in_days   = var.log_analytics_retention_days

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# Application Insights
resource "azurerm_application_insights" "main" {
  count               = var.enable_app_insights ? 1 : 0
  name                = local.app_insights_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  workspace_id        = var.enable_log_analytics ? azurerm_log_analytics_workspace.main[0].id : null
  retention_in_days   = var.app_insights_retention_days

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_log_analytics_workspace.main]
}

# Diagnostic Settings for Web App
resource "azurerm_monitor_diagnostic_setting" "web_app" {
  count                      = var.enable_monitoring ? 1 : 0
  name                       = "diag-${local.web_app_name}"
  target_resource_id         = var.app_service_plan_is_linux ? azurerm_linux_web_app.main[0].id : azurerm_windows_web_app.main[0].id
  log_analytics_workspace_id = var.enable_log_analytics ? azurerm_log_analytics_workspace.main[0].id : null

  enabled_log {
    category = "AppServiceHTTPLogs"
  }

  enabled_log {
    category = "AppServiceConsoleLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }

  depends_on = [azurerm_log_analytics_workspace.main]
}

# ============================================================================
# SECRETS MANAGEMENT - KEY VAULT
# ============================================================================

resource "azurerm_key_vault" "main" {
  count                           = var.enable_key_vault ? 1 : 0
  name                            = local.key_vault_name
  location                        = azurerm_resource_group.main.location
  resource_group_name             = azurerm_resource_group.main.name
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  sku_name                        = var.key_vault_sku
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  enabled_for_deployment          = true
  soft_delete_retention_days      = 7
  purge_protection_enabled        = var.key_vault_enable_purge_protection

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# Grant managed identity access to Key Vault (if using managed identity)
resource "azurerm_role_assignment" "web_app_key_vault_access" {
  count              = var.enable_key_vault && var.enable_managed_identity ? 1 : 0
  scope              = azurerm_key_vault.main[0].id
  role_definition_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/providers/Microsoft.Authorization/roleDefinitions/4633458b-17de-408a-b874-0445c86b69e6" # Key Vault Secrets User
  principal_id       = var.app_service_plan_is_linux ? azurerm_linux_web_app.main[0].identity[0].principal_id : azurerm_windows_web_app.main[0].identity[0].principal_id

  depends_on = [azurerm_linux_web_app.main, azurerm_windows_web_app.main]
}

# ============================================================================
# STORAGE ACCOUNT (for backups/diagnostics)
# ============================================================================

resource "azurerm_storage_account" "main" {
  count                      = var.enable_storage_account ? 1 : 0
  name                       = local.storage_account_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  account_tier               = var.storage_account_tier
  account_replication_type   = var.storage_account_replication_type
  https_traffic_only_enabled = true
  min_tls_version            = "TLS1_2"

  network_rules {
    default_action = "Allow"
    bypass         = ["AzureServices"]
  }

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# ============================================================================
# PRIVATE ENDPOINTS & DNS
# ============================================================================

# Private Endpoint for Web App
resource "azurerm_private_endpoint" "webapp" {
  count               = var.enable_private_endpoint ? 1 : 0
  name                = "pe-${local.web_app_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id

  private_service_connection {
    name                           = "psc-${local.web_app_name}"
    private_connection_resource_id = var.app_service_plan_is_linux ? azurerm_linux_web_app.main[0].id : azurerm_windows_web_app.main[0].id
    subresource_names              = ["sites"]
    is_manual_connection           = false
  }

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_linux_web_app.main, azurerm_windows_web_app.main]
}

# Private DNS Zone (for ILB ASE)
resource "azurerm_private_dns_zone" "main" {
  count               = var.enable_private_dns_zone && var.ase_kind == "ILBASEv3" ? 1 : 0
  name                = var.private_dns_zone_name
  resource_group_name = azurerm_resource_group.main.name

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }
}

# Link Private DNS Zone to VNet
resource "azurerm_private_dns_zone_virtual_network_link" "main" {
  count                 = var.enable_private_dns_zone && var.ase_kind == "ILBASEv3" ? 1 : 0
  name                  = "link-${azurerm_virtual_network.main.name}"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.main[0].name
  virtual_network_id    = azurerm_virtual_network.main.id
  registration_enabled  = false

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_private_dns_zone.main]
}

# Private DNS A Record for Web App (ILB ASE)
resource "azurerm_private_dns_a_record" "webapp" {
  count               = var.enable_private_dns_zone && var.ase_kind == "ILBASEv3" ? 1 : 0
  name                = var.app_service_plan_is_linux ? azurerm_linux_web_app.main[0].name : azurerm_windows_web_app.main[0].name
  zone_name           = azurerm_private_dns_zone.main[0].name
  resource_group_name = azurerm_resource_group.main.name
  ttl                 = 300
  records             = [azurerm_app_service_environment_v3.main.internal_ip_address]

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_private_dns_zone.main, azurerm_private_dns_zone_virtual_network_link.main]
}

# ============================================================================
# AUTO-SCALING
# ============================================================================

resource "azurerm_monitor_autoscale_setting" "main" {
  count               = var.enable_auto_scale ? 1 : 0
  name                = "autoscale-${local.app_service_plan_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  target_resource_id  = azurerm_service_plan.main.id

  profile {
    name = "Scale based on CPU"

    capacity {
      default = var.app_service_plan_worker_count
      minimum = var.auto_scale_min_count
      maximum = var.auto_scale_max_count
    }

    rule {
      metric_trigger {
        metric_name        = "CpuPercentage"
        metric_resource_id = azurerm_service_plan.main.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_aggregation   = "Average"
        time_window        = "PT5M"
        operator           = "GreaterThan"
        threshold          = var.auto_scale_cpu_threshold_up
      }

      scale_action {
        direction = "Increase"
        type      = "ChangeCount"
        value     = 1
        cooldown  = "PT5M"
      }
    }

    rule {
      metric_trigger {
        metric_name        = "CpuPercentage"
        metric_resource_id = azurerm_service_plan.main.id
        time_grain         = "PT1M"
        statistic          = "Average"
        time_aggregation   = "Average"
        time_window        = "PT5M"
        operator           = "LessThan"
        threshold          = var.auto_scale_cpu_threshold_down
      }

      scale_action {
        direction = "Decrease"
        type      = "ChangeCount"
        value     = 1
        cooldown  = "PT10M"
      }
    }
  }

  tags = local.tags

  lifecycle {
    ignore_changes = [tags["CreatedDate"]]
  }

  depends_on = [azurerm_service_plan.main]
}
