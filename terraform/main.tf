/*
  Azure Web App Service with App Service Environment (ASE)
  Main Configuration - Provider and Outputs
*/

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }

  # Uncomment to use remote state (recommended for production)
  # backend "azurerm" {
  #   resource_group_name  = "rg-terraform"
  #   storage_account_name = "mystorageaccount"
  #   container_name       = "tfstate"
  #   key                  = "azure-webapp-ase.tfstate"
  # }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
      recover_soft_deleted_secrets = true
    }
  }

  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
  client_secret   = var.client_secret
}

# Data source to get current Azure context
data "azurerm_client_config" "current" {}

# ============================================================================
# OUTPUTS
# ============================================================================

output "resource_group_id" {
  description = "Resource Group ID"
  value       = azurerm_resource_group.main.id
}

output "resource_group_name" {
  description = "Resource Group Name"
  value       = azurerm_resource_group.main.name
}

output "virtual_network_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.main.id
}

output "virtual_network_name" {
  description = "Virtual Network Name"
  value       = azurerm_virtual_network.main.name
}

output "ase_id" {
  description = "App Service Environment ID"
  value       = azurerm_app_service_environment_v3.main.id
}

output "ase_name" {
  description = "App Service Environment Name"
  value       = azurerm_app_service_environment_v3.main.name
}

output "ase_kind" {
  description = "App Service Environment Kind"
  value       = azurerm_app_service_environment_v3.main.kind
}

output "ase_location" {
  description = "App Service Environment Location"
  value       = azurerm_app_service_environment_v3.main.location
}

output "ase_internal_ip_address" {
  description = "Internal IP Address of ILB ASE (if ILBASEv3)"
  value       = try(azurerm_app_service_environment_v3.main.internal_ip_address, "N/A - External ASE")
}

output "app_service_plan_id" {
  description = "App Service Plan ID"
  value       = azurerm_service_plan.main.id
}

output "app_service_plan_name" {
  description = "App Service Plan Name"
  value       = azurerm_service_plan.main.name
}

output "app_service_plan_sku" {
  description = "App Service Plan SKU"
  value       = azurerm_service_plan.main.sku_name
}

output "web_app_id" {
  description = "Web App ID"
  value       = azurerm_windows_web_app.main[0].id
}

output "web_app_name" {
  description = "Web App Name"
  value       = azurerm_windows_web_app.main[0].name
}

output "web_app_default_hostname" {
  description = "Web App Default Hostname"
  value       = azurerm_windows_web_app.main[0].default_hostname
}

output "web_app_identity" {
  description = "Web App Managed Identity Information"
  value = {
    type         = azurerm_windows_web_app.main[0].identity[0].type
    principal_id = azurerm_windows_web_app.main[0].identity[0].principal_id
    tenant_id    = azurerm_windows_web_app.main[0].identity[0].tenant_id
  }
  sensitive = true
}

output "application_insights_id" {
  description = "Application Insights ID"
  value       = try(azurerm_application_insights.main[0].id, "N/A")
}

output "application_insights_instrumentation_key" {
  description = "Application Insights Instrumentation Key"
  value       = try(azurerm_application_insights.main[0].instrumentation_key, "N/A")
  sensitive   = true
}

output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = try(azurerm_log_analytics_workspace.main[0].id, "N/A")
}

output "key_vault_id" {
  description = "Key Vault ID"
  value       = try(azurerm_key_vault.main[0].id, "N/A")
}

output "key_vault_name" {
  description = "Key Vault Name"
  value       = try(azurerm_key_vault.main[0].name, "N/A")
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = try(azurerm_key_vault.main[0].vault_uri, "N/A")
}

output "storage_account_id" {
  description = "Storage Account ID"
  value       = try(azurerm_storage_account.main[0].id, "N/A")
}

output "storage_account_name" {
  description = "Storage Account Name"
  value       = try(azurerm_storage_account.main[0].name, "N/A")
}

output "private_endpoint_id" {
  description = "Private Endpoint ID for Web App"
  value       = try(azurerm_private_endpoint.webapp[0].id, "N/A")
}

output "private_endpoint_network_interface_ids" {
  description = "Private Endpoint Network Interface IDs"
  value       = try(azurerm_private_endpoint.webapp[0].network_interface_ids, ["N/A"])
}

output "private_endpoint_ip_address" {
  description = "Private IP Address of Web App Private Endpoint"
  value       = try(azurerm_private_endpoint.webapp[0].private_service_connection[0].private_ip_address, "N/A")
}

output "private_dns_zone_id" {
  description = "Private DNS Zone ID"
  value       = try(azurerm_private_dns_zone.main[0].id, "N/A")
}

output "terraform_state_summary" {
  description = "Summary of deployed resources"
  value = {
    subscription_id          = data.azurerm_client_config.current.subscription_id
    tenant_id                = data.azurerm_client_config.current.tenant_id
    ase_type                 = var.ase_kind
    ase_zones                = var.ase_availability_zones
    app_service_plan_sku     = var.app_service_plan_sku
    app_service_plan_workers = var.app_service_plan_worker_count
    auto_scale_enabled       = var.enable_auto_scale
    managed_identity_enabled = var.enable_managed_identity
  }
}
