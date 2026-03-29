# Platform Architecture Standard

Version: 1.0  
Owner: Platform Engineering Team  
Last Updated: 2026-03-08  

---

# 1. Purpose

This document defines the standard architecture principles for platform and application workloads deployed within the organisation's cloud and on-premise environments.

The goal of this standard is to ensure that systems are:

- secure
- resilient
- observable
- scalable
- cost controlled

All new platform and application architectures must align with these principles unless an exception is formally approved.

---

# 2. Architectural Principles

The following principles apply to all systems deployed on the enterprise platform.

## 2.1 Infrastructure as Code

All infrastructure must be provisioned using Infrastructure as Code (IaC).

Approved tools include:

- Terraform
- AWS CloudFormation
- CDK (where appropriate)

Manual infrastructure changes in production environments are not permitted.

---

## 2.2 Immutable Infrastructure

Infrastructure components should be treated as immutable.

Key guidelines:

- Instances must not be manually modified
- Configuration changes must be applied via redeployment
- Container images must be versioned and immutable

---

## 2.3 Container-First Deployment

Application workloads should be deployed using containers.

Preferred orchestration platform:

- Kubernetes

Containers must follow these requirements:

- minimal base images
- non-root execution
- image scanning before deployment

---

# 3. Security Requirements

Security must be embedded into all architecture designs.

## 3.1 Least Privilege Access

Access to systems must follow the principle of least privilege.

Requirements:

- IAM roles must be scoped to the minimum required permissions
- access keys should not be embedded in application code
- temporary credentials should be used whenever possible

---

## 3.2 Network Segmentation

All production systems must operate within controlled network boundaries.

Recommended model:

- private subnets for application workloads
- restricted inbound access via API gateways or load balancers
- outbound traffic controlled using egress policies

---

## 3.3 Secrets Management

Secrets must never be stored in:

- source code
- container images
- configuration files committed to repositories

Approved secret storage solutions:

- AWS Secrets Manager
- HashiCorp Vault

---

# 4. Reliability and Resilience

Systems must be designed to tolerate failure.

## 4.1 Multi-AZ Deployment

Production systems must run across multiple availability zones.

Single-zone deployments are only acceptable for development environments.

---

## 4.2 Automated Recovery

Systems must support automated recovery mechanisms such as:

- health checks
- auto-scaling
- automatic restarts

---

## 4.3 Disaster Recovery

Critical services must define recovery objectives:

- RTO (Recovery Time Objective)
- RPO (Recovery Point Objective)

These objectives must be documented and tested annually.

---

# 5. Observability Standards

All services must expose operational telemetry.

Required telemetry types:

- logs
- metrics
- traces

Approved observability tools include:

- Datadog
- Prometheus
- OpenTelemetry

---

# 6. CI/CD Requirements

All software must be delivered through automated pipelines.

Pipelines must include:

- unit testing
- security scanning
- container image scanning
- infrastructure validation

Manual production deployments are not allowed.

---

# 7. AI Platform Considerations

AI-enabled services must meet additional governance requirements.

Key requirements:

- traceability of model outputs
- logging of prompts and responses where permitted
- protection against prompt injection attacks
- monitoring of model behaviour

AI services must be reviewed by the platform architecture board before production deployment.

---

# 8. Architecture Review Process

All new platform architectures must be reviewed by the Architecture Review Board (ARB).

Review includes evaluation of:

- security posture
- operational readiness
- resilience strategy
- cost model

Architecture documentation must include diagrams and operational runbooks.

---

# 9. Exceptions

Exceptions to this standard may be requested through the Architecture Exception Process.

Requests must include:

- justification
- risk assessment
- mitigation plan