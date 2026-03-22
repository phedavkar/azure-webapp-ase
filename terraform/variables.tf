/*
  Azure Web App Service with App Service Environment (ASE)
  Variables Configuration
*/

# Provider Configuration
variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "client_id" {
  description = "Azure Service Principal Client ID"
  type        = string
  sensitive   = true
}

variable "client_secret" {
  description = "Azure Service Principal Client Secret"
  type        = string
  sensitive   = true
}

# Common Tags
variable "environment" {
  description = "Environment name (prod, staging, dev)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "webapp"
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    "Terraform"  = "true"
    "ManagedBy"  = "Terraform"
    "CostCenter" = "IT"
  }
}

# Resource Group Configuration
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = ""
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

# Virtual Network Configuration
variable "vnet_name" {
  description = "Name of the Virtual Network"
  type        = string
  default     = ""
}

variable "vnet_address_space" {
  description = "Address space for the Virtual Network"
  type        = list(string)
  default     = ["10.3.0.0/16"]
}

variable "ase_subnet_name" {
  description = "Name of the ASE subnet"
  type        = string
  default     = ""
}

variable "ase_subnet_address_prefix" {
  description = "Address prefix for ASE subnet (/24 minimum recommended)"
  type        = string
  default     = "10.3.1.0/24"
}

variable "private_endpoints_subnet_name" {
  description = "Name of the Private Endpoints subnet"
  type        = string
  default     = ""
}

variable "private_endpoints_subnet_address_prefix" {
  description = "Address prefix for Private Endpoints subnet"
  type        = string
  default     = "10.3.2.0/24"
}

variable "app_gateway_subnet_name" {
  description = "Name of the Application Gateway subnet (optional, for external ASE)"
  type        = string
  default     = ""
}

variable "app_gateway_subnet_address_prefix" {
  description = "Address prefix for Application Gateway subnet"
  type        = string
  default     = "10.3.3.0/24"
}

# App Service Environment Configuration
variable "ase_name" {
  description = "Name of the App Service Environment"
  type        = string
  default     = ""
}

variable "ase_kind" {
  description = "Kind of ASE - 'ASEv3' for external, 'ILBASEv3' for internal load balancer"
  type        = string
  default     = "ILBASEv3"

  validation {
    condition     = contains(["ASEv3", "ILBASEv3"], var.ase_kind)
    error_message = "ASE kind must be either 'ASEv3' (external) or 'ILBASEv3' (internal load balancer)"
  }
}

variable "ase_zone_redundant" {
  description = "Enable zone redundancy for ASE"
  type        = bool
  default     = true
}

variable "ase_availability_zones" {
  description = "Availability zones for ASE (1, 2, or 3)"
  type        = number
  default     = 3

  validation {
    condition     = contains([1, 2, 3], var.ase_availability_zones)
    error_message = "ASE availability zones must be 1, 2, or 3"
  }
}

variable "ase_frontend_scale_factor" {
  description = "Number of front-end instances (minimum 1, recommended 3 for HA)"
  type        = number
  default     = 3

  validation {
    condition     = var.ase_frontend_scale_factor >= 1 && var.ase_frontend_scale_factor <= 10
    error_message = "ASE frontend scale factor must be between 1 and 10"
  }
}

# App Service Plan Configuration
variable "app_service_plan_name" {
  description = "Name of the App Service Plan"
  type        = string
  default     = ""
}

variable "app_service_plan_sku" {
  description = "SKU for App Service Plan (I1V2, I2V2, I3V2 for ASEv3)"
  type        = string
  default     = "I1V2"

  validation {
    condition     = contains(["I1V2", "I2V2", "I3V2"], var.app_service_plan_sku)
    error_message = "App Service Plan SKU must be I1V2, I2V2, or I3V2 for ASEv3"
  }
}

variable "app_service_plan_worker_count" {
  description = "Number of workers for App Service Plan"
  type        = number
  default     = 3

  validation {
    condition     = var.app_service_plan_worker_count >= 1
    error_message = "App Service Plan worker count must be at least 1"
  }
}

variable "app_service_plan_reserved" {
  description = "Is this App Service Plan reserved (for Windows)?"
  type        = bool
  default     = false
}

variable "app_service_plan_is_linux" {
  description = "Is this App Service Plan for Linux?"
  type        = bool
  default     = true
}

# Web App Configuration
variable "web_app_name" {
  description = "Name of the Web App"
  type        = string
  default     = ""
}

variable "web_app_runtime_stack" {
  description = "Runtime stack for the app (e.g., 'TOMCAT|10.0', 'DOTNET|6.0', 'NODE|18-lts')"
  type        = string
  default     = "TOMCAT|10.0"
}

variable "web_app_java_version" {
  description = "Java version (e.g., '17', '11')"
  type        = string
  default     = "17"
}

variable "web_app_always_on" {
  description = "Enable Always On for the web app"
  type        = bool
  default     = true
}

variable "web_app_https_only" {
  description = "Require HTTPS for the web app"
  type        = bool
  default     = true
}

variable "web_app_http2_enabled" {
  description = "Enable HTTP/2 for the web app"
  type        = bool
  default     = true
}

variable "web_app_32bit_worker_process" {
  description = "Use 32-bit worker process"
  type        = bool
  default     = false
}

variable "web_app_app_settings" {
  description = "Application settings for the web app"
  type        = map(string)
  default = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "JAVA_OPTS"                           = "-Dcom.sun.jndi.ldap.connect.pool=true"
    "LOG_LEVEL"                           = "INFO"
  }
}

variable "web_app_connection_strings" {
  description = "Connection strings for the web app"
  type = map(object({
    value = string
    type  = string
  }))
  default = {}
}

variable "enable_managed_identity" {
  description = "Enable System-assigned Managed Identity for the web app"
  type        = bool
  default     = true
}

variable "enable_vnet_integration" {
  description = "Enable VNet integration for the web app"
  type        = bool
  default     = true
}

variable "enable_private_endpoint" {
  description = "Enable Private Endpoint for the web app"
  type        = bool
  default     = true
}

# Application Insights Configuration
variable "enable_app_insights" {
  description = "Enable Application Insights"
  type        = bool
  default     = true
}

variable "app_insights_name" {
  description = "Name of Application Insights"
  type        = string
  default     = ""
}

variable "app_insights_retention_days" {
  description = "Retention period for Application Insights in days"
  type        = number
  default     = 30
}

# Log Analytics Configuration
variable "enable_log_analytics" {
  description = "Enable Log Analytics workspace"
  type        = bool
  default     = true
}

variable "log_analytics_name" {
  description = "Name of Log Analytics workspace"
  type        = string
  default     = ""
}

variable "log_analytics_sku" {
  description = "SKU for Log Analytics workspace"
  type        = string
  default     = "PerGB2018"
}

variable "log_analytics_retention_days" {
  description = "Log Analytics retention period in days"
  type        = number
  default     = 30
}

# Key Vault Configuration
variable "enable_key_vault" {
  description = "Enable Key Vault for secrets management"
  type        = bool
  default     = true
}

variable "key_vault_name" {
  description = "Name of Key Vault"
  type        = string
  default     = ""
}

variable "key_vault_sku" {
  description = "SKU for Key Vault (standard or premium)"
  type        = string
  default     = "standard"
}

variable "key_vault_enable_soft_delete" {
  description = "Enable soft delete for Key Vault"
  type        = bool
  default     = true
}

variable "key_vault_enable_purge_protection" {
  description = "Enable purge protection for Key Vault"
  type        = bool
  default     = true
}

# Storage Account Configuration (for backups/diagnostics)
variable "enable_storage_account" {
  description = "Enable Storage Account for backups/diagnostics"
  type        = bool
  default     = true
}

variable "storage_account_name" {
  description = "Name of Storage Account"
  type        = string
  default     = ""
}

variable "storage_account_tier" {
  description = "Storage Account tier (Standard or Premium)"
  type        = string
  default     = "Standard"
}

variable "storage_account_replication_type" {
  description = "Storage Account replication type (LRS, GRS, RAGRS, ZRS)"
  type        = string
  default     = "GRS"
}

# Private DNS Zone Configuration
variable "enable_private_dns_zone" {
  description = "Enable Private DNS Zone for ILB ASE"
  type        = bool
  default     = true
}

variable "private_dns_zone_name" {
  description = "Name of Private DNS Zone"
  type        = string
  default     = "internal.company.com"
}

# Auto-Scaling Configuration
variable "enable_auto_scale" {
  description = "Enable auto-scaling for App Service Plan"
  type        = bool
  default     = true
}

variable "auto_scale_min_count" {
  description = "Minimum number of instances for auto-scaling"
  type        = number
  default     = 3
}

variable "auto_scale_max_count" {
  description = "Maximum number of instances for auto-scaling"
  type        = number
  default     = 10
}

variable "auto_scale_cpu_threshold_up" {
  description = "CPU percentage threshold to scale up"
  type        = number
  default     = 70
}

variable "auto_scale_cpu_threshold_down" {
  description = "CPU percentage threshold to scale down"
  type        = number
  default     = 30
}

# Authentication Configuration
variable "enable_authentication" {
  description = "Enable Azure AD authentication on the web app"
  type        = bool
  default     = false
}

variable "azure_ad_tenant_id" {
  description = "Azure AD Tenant ID for authentication"
  type        = string
  default     = ""
}

variable "azure_ad_client_id" {
  description = "Azure AD Application (Client) ID"
  type        = string
  default     = ""
  sensitive   = true
}

variable "azure_ad_client_secret" {
  description = "Azure AD Application Client Secret"
  type        = string
  default     = ""
  sensitive   = true
}

# Backup Configuration
variable "enable_backup" {
  description = "Enable automated backups for web app"
  type        = bool
  default     = true
}

variable "backup_frequency_days" {
  description = "Backup frequency in days"
  type        = number
  default     = 1
}

variable "backup_retention_days" {
  description = "Number of backup copies to keep"
  type        = number
  default     = 7
}

# Monitoring and Alerts
variable "enable_monitoring" {
  description = "Enable comprehensive monitoring and alerts"
  type        = bool
  default     = true
}

variable "alert_email_addresses" {
  description = "Email addresses for alert notifications"
  type        = list(string)
  default     = []
}
