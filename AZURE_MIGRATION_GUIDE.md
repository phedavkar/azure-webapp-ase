# Tomcat to Azure Web App Service Migration Guide

A comprehensive checklist for migrating enterprise Java/Tomcat applications to Azure Web App Service with Azure-native solutions.

---

## Phase 1: Assessment & Planning

### 1.1 Application Inventory
- [ ] Document all Tomcat applications running in private cloud
- [ ] Identify application dependencies (internal, external, third-party APIs)
- [ ] List all Java versions and Tomcat versions in use
- [ ] Document custom configurations and non-standard deployments
- [ ] Identify any deprecated or EOL Java/Tomcat versions
- [ ] Review application code for cloud compatibility issues

### 1.2 Infrastructure Assessment
- [ ] Map current database systems (SQL Server, MySQL, PostgreSQL, Oracle, etc.)
- [ ] Document database sizes and growth rates
- [ ] Identify file storage requirements (local file system dependencies)
- [ ] Document network architecture and connectivity requirements
- [ ] List all external service integrations
- [ ] Identify failover and disaster recovery requirements

### 1.3 Security & Compliance Assessment
- [ ] Review current authentication mechanisms (LDAP, AD, custom, etc.)
- [ ] Document authorization and role-based access control (RBAC) models
- [ ] Identify compliance requirements (HIPAA, PCI-DSS, SOC 2, GDPR, etc.)
- [ ] Document current encryption standards (TLS versions, cipher suites)
- [ ] Review secrets management approach (hardcoded, config files, vault, etc.)
- [ ] Identify certificate management requirements

---

## Phase 2: Azure Architecture & Design

### 2.1 Azure Web App Service Setup
- [ ] Determine appropriate App Service Plan (B, P, or I series)
- [ ] Choose deployment regions (consider latency, compliance, redundancy)
- [ ] Plan scaling strategy (auto-scale rules, metrics)
- [ ] Design multi-region setup for high availability (if needed)
- [ ] Plan backup and disaster recovery strategy
- [ ] Configure monitoring and alerting

### 2.2 Authentication & Authorization
- [ ] **Azure Entra ID (formerly Azure AD) Integration**
  - [ ] Register applications in Azure Entra ID
  - [ ] Configure OpenID Connect or SAML flows
  - [ ] Set up multi-factor authentication (MFA) policies
  - [ ] Configure Conditional Access policies
  
- [ ] **Application-Level Authentication Options**
  - [ ] Use Azure Entra ID with Spring Security (for Spring apps)
  - [ ] Use Azure Entra ID with Quarkus (for Quarkus apps)
  - [ ] Implement custom OAuth 2.0/OpenID Connect using Microsoft libraries
  - [ ] Migrate LDAP to Azure Entra ID via Azure Entra Connect (if using on-premises AD)

- [ ] **Authorization**
  - [ ] Map existing RBAC to Azure Entra ID roles and groups
  - [ ] Implement Azure role-based access control (RBAC) for Azure resources
  - [ ] Configure application-level authorization using Azure Entra ID groups
  - [ ] Plan fine-grained access control within applications

### 2.3 Secrets Management
- [ ] **Azure Key Vault Setup**
  - [ ] Create Key Vault instance
  - [ ] Configure access policies or RBAC for Key Vault
  - [ ] Migrate all secrets (API keys, connection strings, certificates, etc.)
  - [ ] Set up automatic secret rotation policies
  - [ ] Enable soft delete and purge protection

- [ ] **Managed Identity Configuration**
  - [ ] Enable system-assigned managed identity on App Service
  - [ ] Create user-assigned managed identities (if needed for shared resources)
  - [ ] Grant managed identity permissions to Key Vault
  - [ ] Update application code to use managed identities instead of connection strings

- [ ] **Application Configuration**
  - [ ] Use Azure App Configuration service for non-sensitive configuration
  - [ ] Implement feature flags using App Configuration
  - [ ] Set up configuration refresh policies

### 2.4 Database Migration Strategy
- [ ] **Assess current database**
  - [ ] Determine optimal Azure database service (Azure SQL, Azure Database for PostgreSQL/MySQL, Azure Cosmos DB, etc.)
  - [ ] Plan database compatibility validation
  
- [ ] **Azure SQL Database (for SQL Server)**
  - [ ] Create target database with appropriate service tier
  - [ ] Use Azure Database Migration Service (DMS) for data migration
  - [ ] Enable Transparent Data Encryption (TDE)
  - [ ] Configure geo-replication for disaster recovery
  - [ ] Enable Advanced Threat Protection
  - [ ] Set up automated backups and retention policy
  - [ ] Configure Private Endpoint for network isolation

- [ ] **Azure Database for PostgreSQL/MySQL**
  - [ ] Migrate using Azure DMS
  - [ ] Enable SSL/TLS enforcement
  - [ ] Configure server parameters for performance
  - [ ] Enable audit logging
  - [ ] Set up read replicas for scaling (if applicable)

- [ ] **Connection String Management**
  - [ ] Remove hardcoded connection strings from application
  - [ ] Store connection strings in Azure Key Vault
  - [ ] Use managed identities for authentication (avoid storing passwords)
  - [ ] Configure connection pooling appropriately

### 2.5 File Storage & Persistence
- [ ] **For shared file storage:**
  - [ ] Use Azure Files (SMB) or Azure Blob Storage
  - [ ] Configure connection strings in Key Vault
  - [ ] Set up proper access control and RBAC
  
- [ ] **For application temp storage:**
  - [ ] Evaluate App Service storage (`/home` directory)
  - [ ] Ensure app is stateless (for horizontal scaling)
  - [ ] Move persistent data to Blob Storage or Managed Disks

- [ ] **Session Management:**
  - [ ] Store sessions in external store (Azure Cache for Redis, database)
  - [ ] Enable session stickiness if temporary local storage is used
  - [ ] Plan for session replication across instances

---

## Phase 3: Application Modernization

### 3.1 Code Updates
- [ ] Update Java version to LTS release (11, 17, 21, or latest LTS)
- [ ] Update Tomcat to latest supported version
- [ ] Update all Maven/Gradle dependencies to latest compatible versions
- [ ] Address any deprecated APIs or features
- [ ] Implement 12-factor app principles
- [ ] Externalize all configuration (environment variables, Key Vault)
- [ ] Remove environment-specific hardcoded values

### 3.2 Containerization (Optional but Recommended)
- [ ] Create Dockerfile for your application
  - [ ] Use official Java image as base (eclipse-temurin, openjdk, etc.)
  - [ ] Multi-stage build for optimization
  - [ ] Non-root user for security
  
- [ ] Build and test container locally
- [ ] Push container image to Azure Container Registry (ACR)
- [ ] Deploy to App Service using container image
- [ ] Or use built-in deployment with WAR/JAR files

### 3.3 Build Pipeline Updates
- [ ] Remove environment-specific configuration from build
- [ ] Update CI/CD to build and push container images (if containerized)
- [ ] Set up artifact signing for security
- [ ] Implement automated security scanning of artifacts

---

## Phase 4: Networking & Connectivity

### 4.1 Virtual Network Integration
- [ ] Deploy App Service to Virtual Network (VNet)
- [ ] Configure VNet integration for outbound traffic
- [ ] Use Private Endpoints for Azure resources (SQL, Key Vault, Storage)
- [ ] Configure Network Security Groups (NSGs) and User-Defined Routes (UDRs)

### 4.2 Hybrid Connectivity (if needed)
- [ ] Set up Azure VPN Gateway or Azure ExpressRoute for on-premises connectivity
- [ ] Configure site-to-site VPN or ExpressRoute connection
- [ ] Test connectivity to on-premises resources
- [ ] Plan for network latency and bandwidth requirements

### 4.3 API Management (Optional)
- [ ] Evaluate Azure API Management for API protection and exposure
- [ ] Configure API policies (rate limiting, authentication, logging)
- [ ] Set up developer portal (if applicable)

---

## Phase 5: Monitoring, Logging & Observability

### 5.1 Azure Monitor Setup
- [ ] Enable Application Insights for the App Service
- [ ] Configure diagnostic settings for logs
- [ ] Set up Log Analytics workspace
- [ ] Configure metric-based alerts
- [ ] Set up action groups for alert notifications

### 5.2 Application Logging
- [ ] Implement centralized logging (Application Insights or ELK stack)
- [ ] Configure log levels appropriately
- [ ] Enable SQL query logging (if needed)
- [ ] Implement structured logging (JSON format)

### 5.3 Performance Monitoring
- [ ] Set up performance counters
- [ ] Configure slow query logging for databases
- [ ] Monitor App Service CPU, memory, and I/O
- [ ] Set up custom metrics from application

### 5.4 Security Monitoring
- [ ] Enable Azure Defender for Cloud
- [ ] Monitor for vulnerabilities in dependencies
- [ ] Set up alerts for unauthorized access attempts
- [ ] Enable Azure SQL threat detection
- [ ] Monitor Key Vault access logs

---

## Phase 6: Backup & Disaster Recovery

### 6.1 Application Backup
- [ ] Enable automatic backups for App Service (7 days minimum)
- [ ] Test backup and restore process
- [ ] Plan backup retention policy

### 6.2 Database Backup
- [ ] Enable automated backups with appropriate retention
- [ ] Configure geo-replication for critical databases
- [ ] Test point-in-time restore procedures
- [ ] Document RTO and RPO requirements

### 6.3 Disaster Recovery Plan
- [ ] Document failover procedures
- [ ] Set up Traffic Manager for multi-region failover (if needed)
- [ ] Plan data synchronization strategy
- [ ] Create disaster recovery runbook

---

## Phase 7: Migration Execution

### 7.1 Pilot Migration
- [ ] Select non-critical application for pilot
- [ ] Create detailed migration plan for pilot app
- [ ] Document all issues and resolutions
- [ ] Conduct performance and load testing
- [ ] Get stakeholder sign-off

### 7.2 Production Migration Plan
- [ ] Schedule migration window
- [ ] Plan for rollback procedures
- [ ] Prepare communication plan
- [ ] Set up canary deployment (if using containers)
- [ ] Plan database migration and validation strategy
- [ ] Prepare cutover checklist

### 7.3 Cutover Execution
- [ ] Stop application on Tomcat/private cloud
- [ ] Back up all data (databases, files)
- [ ] Migrate/validate data on Azure
- [ ] Deploy application to Azure Web App
- [ ] Update DNS/routing to point to Azure
- [ ] Monitor application for issues
- [ ] Perform smoke tests
- [ ] Monitor error rates and performance metrics

---

## Phase 8: Post-Migration

### 8.1 Validation
- [ ] Verify all application functionality
- [ ] Test end-to-end workflows
- [ ] Validate authentication and authorization
- [ ] Confirm database connectivity
- [ ] Test backup and restore processes
- [ ] Validate scaling behavior under load
- [ ] Verify all integrations with external services

### 8.2 Performance Optimization
- [ ] Analyze performance metrics
- [ ] Optimize App Service Plan tier if needed
- [ ] Configure auto-scaling rules based on metrics
- [ ] Tune database performance (indexes, queries)
- [ ] Implement caching strategies (Redis, HTTP caching)
- [ ] Optimize container images (if containerized)

### 8.3 Cost Optimization
- [ ] Review Azure Cost Management reports
- [ ] Right-size App Service Plan
- [ ] Configure auto-shutdown for non-production environments
- [ ] Evaluate Reserved Instances for long-term savings
- [ ] Optimize database service tier
- [ ] Configure log retention policies to manage storage costs

### 8.4 Documentation & Knowledge Transfer
- [ ] Document Azure architecture and configuration
- [ ] Create runbooks for common operations
- [ ] Document scaling and capacity planning
- [ ] Create incident response procedures
- [ ] Document patching and update procedures
- [ ] Train operations team on Azure services
- [ ] Document troubleshooting guides

### 8.5 Decommissioning Old Infrastructure
- [ ] Back up final data from Tomcat/private cloud
- [ ] Archive logs and application data (if required for compliance)
- [ ] Update DNS and remove old endpoints
- [ ] Schedule infrastructure shutdown
- [ ] Document final state
- [ ] Release resources

---

## Phase 9: Azure-Native Best Practices

### 9.1 Security
- [ ] Implement Azure Entra ID for all authentication
- [ ] Use Managed Identities exclusively (no connection strings)
- [ ] Enable Azure Defender recommendations
- [ ] Implement network security best practices
- [ ] Enable encryption at rest and in transit
- [ ] Implement application security groups (ASGs)
- [ ] Enable Web Application Firewall (WAF) on Application Gateway (if needed)

### 9.2 Cost Management
- [ ] Implement tagging strategy for cost allocation
- [ ] Set up budget alerts
- [ ] Use Azure Cost Analysis for visibility
- [ ] Right-size resources based on actual usage
- [ ] Implement FinOps practices

### 9.3 DevOps & Infrastructure as Code
- [ ] Use Azure Resource Manager (ARM) templates or Terraform for IaC
- [ ] Implement CI/CD pipelines using Azure DevOps or GitHub Actions
- [ ] Automate deployment process
- [ ] Version control all infrastructure code
- [ ] Implement automated testing in pipelines

### 9.4 Governance & Compliance
- [ ] Implement Azure Policy for compliance enforcement
- [ ] Set up Azure Blueprints for consistent deployment
- [ ] Implement naming conventions and tagging standards
- [ ] Enable audit logging for compliance
- [ ] Configure RBAC with principle of least privilege
- [ ] Implement regular compliance audits

---

## Key Azure Services to Leverage

| Requirement | Azure Service | Notes |
|-------------|---------------|-------|
| **Authentication & Authorization** | Azure Entra ID | Native identity platform |
| **Secrets Management** | Azure Key Vault | Centralized secrets storage |
| **Web Hosting** | Azure App Service | PaaS for web applications |
| **Containers** | Azure Container Registry + App Service | For containerized deployments |
| **Databases** | Azure SQL / Azure Database for PostgreSQL/MySQL | Managed database services |
| **File Storage** | Azure Blob Storage / Azure Files | Persistent storage solutions |
| **Session Management** | Azure Cache for Redis | Distributed session storage |
| **Monitoring & Logging** | Application Insights + Log Analytics | Observability platform |
| **Configuration** | Azure App Configuration | Feature flags and settings |
| **Virtual Networking** | Azure Virtual Network | Network isolation and security |
| **Disaster Recovery** | Azure Traffic Manager, Geo-replication | High availability solutions |
| **CI/CD** | Azure DevOps / GitHub Actions | Automated deployment pipelines |
| **Security Monitoring** | Azure Defender | Threat detection and protection |

---

## Technology Stack Examples

### Spring Boot Applications
```
Tomcat WAR → Spring Boot with Embedded Tomcat
├── Azure Entra ID for Authentication (spring-cloud-azure-starter-active-directory)
├── Azure Key Vault for Secrets (spring-cloud-azure-starter-keyvault)
├── Azure SQL Database
├── Azure Cache for Redis
└── Application Insights
```

### Other Java Applications
- Consider Spring Integration or Quarkus for modernization
- Implement custom OAuth 2.0/OIDC using Microsoft libraries
- Use JDBC connection pooling with managed identities

---

## Common Pitfalls to Avoid

1. **Lifting and Shifting Without Modernization** - Make code changes to leverage Azure services
2. **Ignoring Secrets Management** - Never store credentials in application code
3. **Local File System Dependencies** - Move to Blob Storage or Azure Files
4. **Hardcoded Configuration** - Use environment variables and App Configuration
5. **Insufficient Logging** - Implement comprehensive monitoring from the start
6. **Not Testing Failover** - Regularly test disaster recovery procedures
7. **Ignoring Cost Implications** - Monitor costs throughout migration
8. **Inadequate Security Planning** - Implement security by design
9. **No Rollback Plan** - Always have documented rollback procedures
10. **Insufficient Load Testing** - Validate performance under expected loads

---

## Timeline Estimate

- **Assessment Phase**: 2-4 weeks
- **Design Phase**: 2-4 weeks
- **Modernization & Testing**: 4-8 weeks
- **Pilot Migration**: 2-4 weeks
- **Production Migration**: 1-2 weeks (varies by number of applications)
- **Post-Migration Validation**: 2-4 weeks
- **Stabilization & Optimization**: Ongoing

**Total Estimated Timeline**: 3-6 months for full enterprise migration

---

## Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Entra ID Documentation](https://docs.microsoft.com/azure/active-directory/)
- [Azure Key Vault Documentation](https://docs.microsoft.com/azure/key-vault/)
- [Azure Database Migration Service](https://docs.microsoft.com/azure/dms/)
- [Java on Azure Documentation](https://docs.microsoft.com/java/azure/)
- [Spring on Azure](https://docs.microsoft.com/azure/developer/java/spring-framework/)
- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)

