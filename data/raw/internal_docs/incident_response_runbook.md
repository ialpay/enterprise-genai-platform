# Incident Response Runbook

Version: 1.0  
Owner: Platform Operations Team  
Last Updated: 2026-03-08  

---

# 1. Purpose

This runbook defines the operational procedures for responding to production incidents affecting platform services.

The objective of the incident response process is to:

- restore service as quickly as possible
- minimise customer impact
- ensure clear communication
- identify root causes and prevent recurrence

This runbook applies to all production services operated by the platform team.

---

# 2. Incident Severity Levels

Incidents are classified based on business impact.

## Severity 1 (Critical)

Definition:

- Major customer-facing outage
- Core platform service unavailable
- Security breach or data exposure

Examples:

- authentication service unavailable
- payment processing failure
- widespread API outage

Response requirements:

- immediate incident declaration
- incident commander assigned
- executive notification

Target response time:

- 15 minutes

---

## Severity 2 (High)

Definition:

- Significant service degradation
- Partial outage affecting a large user group

Examples:

- elevated API latency
- failure in a non-critical dependency

Response requirements:

- incident declared
- engineering teams notified

Target response time:

- 30 minutes

---

## Severity 3 (Medium)

Definition:

- limited service disruption
- degraded internal functionality

Examples:

- background job failure
- monitoring alert without user impact

Target response time:

- 2 hours

---

## Severity 4 (Low)

Definition:

- minor issue with minimal operational impact

Examples:

- non-critical monitoring alert
- documentation or tooling issue

Target response time:

- next business day

---

# 3. Incident Roles

During a major incident, the following roles must be assigned.

## Incident Commander

Responsibilities:

- lead incident response
- coordinate teams
- make operational decisions
- ensure updates are communicated

---

## Communications Lead

Responsibilities:

- provide internal status updates
- communicate with customer support
- prepare external incident updates if required

---

## Technical Lead

Responsibilities:

- guide technical investigation
- coordinate engineering remediation actions
- validate recovery steps

---

# 4. Incident Detection

Incidents are typically detected through monitoring and alerting systems.

Approved monitoring platforms include:

- Datadog
- Prometheus
- Cloud monitoring services

Alerts should trigger when:

- service health checks fail
- error rates exceed thresholds
- latency exceeds defined SLO limits

---

# 5. Initial Response Procedure

When an incident is detected:

1. Verify the alert is legitimate.
2. Determine the severity level.
3. Declare the incident in the incident management system.
4. Assign an incident commander.
5. Notify relevant engineering teams.
6. Begin investigation.

All incidents must be logged in the incident tracking system.

---

# 6. Investigation Process

The investigation phase focuses on identifying the cause of the issue.

Typical investigation steps include:

- reviewing recent deployments
- checking system metrics
- analysing error logs
- verifying dependency health
- confirming infrastructure status

Engineering teams should avoid making multiple simultaneous changes during investigation to reduce additional risk.

---

# 7. Service Recovery

Once the root cause is identified, teams should prioritise service restoration.

Possible recovery actions include:

- rolling back a deployment
- restarting affected services
- scaling infrastructure
- disabling faulty feature flags

Recovery actions must be documented in the incident timeline.

---

# 8. Communication Guidelines

Communication must be clear, frequent, and factual.

Status updates should include:

- current system status
- known impact
- actions being taken
- next update time

Updates should be provided at least every 30 minutes during major incidents.

---

# 9. Post-Incident Review

After service restoration, a post-incident review must be conducted.

The review should include:

- incident timeline
- root cause analysis
- contributing factors
- remediation actions

The outcome of the review must produce actionable improvements.

---

# 10. Preventive Actions

Typical preventive improvements include:

- improved monitoring
- additional alerting
- better deployment validation
- architectural resilience improvements

Action items must be tracked until completion.

---

# 11. Documentation

All incidents must be documented and stored in the central incident management repository.

Documentation must include:

- incident description
- timeline of events
- remediation steps
- lessons learned

This documentation is used to improve operational maturity and system resilience.