# CLAUDE.md

# AI Powered Banking Risk & Production Incident Monitoring Application

## Product Vision
Build an enterprise-grade AI-powered banking risk and production incident monitoring platform that analyzes banking transactions, customer/account data, production incidents, API logs, application logs, test execution results, and reference datasets to proactively identify fraud risks, operational failures, SLA breaches, data-quality issues, technical hotspots, and governance violations.

The platform must provide explainable AI insights, actionable recommendations, governance validation, evaluation metrics, and a human-in-the-loop decision framework through a modern Streamlit dashboard.

---

## UI Banner Requirement

At the top of the application display a horizontal moving marquee banner:

AI Powered Banking Risk Application

Style:
- Banking-grade professional UI
- Dark blue enterprise theme
- Smooth scrolling left-to-right animation
- Responsive across desktop and tablet
- Visible on every dashboard page

---

# Business Problem

Modern banks generate millions of transactional and technical events every day.

These events are spread across:
- Customer systems
- Banking transactions
- Core banking accounts
- KYC records
- Production incidents
- API monitoring systems
- Application logs
- Testing platforms

Manually identifying risk signals is expensive, inconsistent, and slow.

Examples:

### Normal Transaction
₹12,500
→ Active Account
→ Verified KYC
→ Normal Customer Behaviour
→ Low Risk

### Suspicious Transaction
₹9,50,000
→ Closed Account
→ KYC Risk Customer
→ Unusual Behaviour Pattern
→ High Risk

Similarly:

### Healthy API Call
450 ms
HTTP 200
No Incident
No SLA Breach

### High-Risk Operational Event
4500 ms
HTTP 500
Linked Production Incident
SLA Breach

The objective is to automatically separate important cases from normal activity and provide explainable reasoning for every decision.

---

# Dataset Summary

| Dataset | Size | Purpose |
|----------|----------|----------|
| Customers | 10,000 | Customer profiling, KYC validation, risk analysis |
| Accounts | 15,000 | Account relationship and status validation |
| Transactions | 25,000 | Fraud detection and anomaly analysis |
| Production Incidents | 10,000 | SLA and incident intelligence |
| API Logs | 15,000 | API performance and failure monitoring |
| Application Logs | 20,000 | Error analytics and root-cause identification |
| Test Cases | 5,000 | Quality and release-risk assessment |
| Reference Data | Multiple | Business-rule validation and governance |

---

# Known Problematic Scenarios Present In Dataset

The dataset intentionally contains anomalies including:

## Banking Risks
- High-value transactions
- Duplicate transactions
- Invalid customer relationships
- Rejected KYC customers
- Expired KYC customers
- Closed account activity
- Dormant account activity
- Blocked account activity
- Invalid beneficiaries
- Suspicious customer-account mappings

## Data Quality Issues
- Future dates
- Duplicate identifiers
- Missing IP addresses
- Invalid currencies
- Invalid customer IDs
- Missing mandatory fields

## Production Risks
- HTTP 500 failures
- HTTP 502 failures
- HTTP 503 failures
- HTTP 504 failures
- Slow APIs
- Service unavailable events
- Database failures
- Authentication failures
- Rate limits
- Upstream timeouts

## Testing Failures
- Failed test cases
- Environment unavailable
- Authentication failures
- Assertion failures
- Timeout failures
- Data mismatch issues

---

# Application Workflow

Banking Data
↓
Data Validation
↓
Feature Engineering
↓
Rule Engine
+
AI Anomaly Detection
↓
Risk Scoring
↓
Incident Intelligence
↓
AI Insights
↓
Recommendations
↓
Human Review
↓
Final Decision

Principle:

AI Detects and Recommends
Human Reviews
Human Makes Final Banking Decision

---

# Core AI Capabilities

## 1. Risk & Anomaly Detection

Detect:
- Fraud-like transactions
- Behavioural anomalies
- High-value outliers
- Risky customer activity
- Abnormal account usage
- Suspicious beneficiary patterns
- Closed account transactions
- Dormant account activity

Techniques:
- Isolation Forest
- Local Outlier Factor
- Autoencoders
- Statistical Outlier Detection
- Rule-Based Detection
- Hybrid Risk Models

---

## 2. Operational Intelligence

Analyze:
- Incidents
- API Logs
- Application Logs
- Test Results

Detect:
- SLA breaches
- Incident hotspots
- Operational bottlenecks
- Slow APIs
- Error spikes
- Failed releases
- Repeated incidents
- Service degradation

---

## 3. Explainable AI

Every prediction must include a reason.

Example:

Transaction TX10234
Risk Score: 88/100
Classification: High Risk

Reasons:
- Closed account transaction
- High-value amount
- Expired KYC
- Unusual customer pattern

Recommendation:
Prioritize manual investigation and validate customer identity and account status before processing.

---

# Data Validation Rules

## Customer Rules

Validate:
- Customer ID exists
- KYC status validity
- Account status validity
- Future onboarding dates
- Duplicate customer records

## Account Rules

Validate:
- Account ownership
- Closed accounts
- Blocked accounts
- Dormant accounts
- Invalid relationships

## Transaction Rules

Validate:
- Negative amounts
- Duplicate transactions
- Future dates
- Invalid currencies
- Settlement inconsistencies
- Suspicious transaction patterns

## API Validation

Validate:
- Response time thresholds
- HTTP failures
- Timeout spikes
- Error-code frequencies

## Incident Validation

Validate:
- SLA breaches
- Resolution delays
- Missing RCA
- Missing ownership

## Test Validation

Validate:
- Failed test cases
- Blocked executions
- Repeated defects
- Release-readiness gaps

---

# Risk Scoring Framework

Score Range:

0–30     Low Risk
31–60    Medium Risk
61–80    High Risk
81–100   Critical Risk

Example Contributors:

| Factor | Weight |
|----------|----------|
| KYC Risk | 20 |
| Closed Account | 20 |
| Transaction Amount | 15 |
| Behavioural Anomaly | 15 |
| Fraud Signals | 15 |
| Governance Violations | 15 |

---

# Dashboard Requirements

## Executive Overview

Display:
- Total customers
- Total accounts
- Total transactions
- Total incidents
- Failed tests
- APIs monitored
- Risk distribution

## Banking Risk Dashboard

Display:
- Risk scores
- Anomaly heatmaps
- Customer risk segmentation
- Account risk analysis
- Fraud indicators

## Operational Dashboard

Display:
- SLA breaches
- Open incidents
- Incident severity trends
- Mean resolution time
- Team-wise incident analysis

## API Monitoring

Display:
- Slow APIs
- HTTP failures
- Response time trends
- Service health score

## Application Log Intelligence

Display:
- Error-code analysis
- Root-cause breakdown
- Failure trends
- Correlation analysis

## Test Analytics

Display:
- Failed tests
- Pass rate
- Quality score
- Release readiness

## AI Recommendations

Display:
- Prioritized actions
- Risk explanations
- Remediation guidance
- Confidence score

## Governance Dashboard

Display:
- DPDP compliance status
- RBI control status
- PII exposure checks
- Audit trail validations
- Explainability score

## Observability & Traceability Dashboard

Display:
- Pipeline run history (timestamp, duration, status, rows processed)
- Per-stage execution timing (data validation, feature engineering, risk
  scoring, incident/API/log/test enrichment, governance checks)
- Row counts processed per dataset for each run
- Anomaly-detection model parameters (Isolation Forest, Local Outlier Factor,
  ensemble weights)
- End-to-end entity trace for any transaction or incident: raw record →
  engineered features → triggered rules (with category and points) →
  anomaly score → final risk score/bucket → recommendation → human decision

---

# Governance Requirements

## DPDP Act Compliance

Mandatory:
- Data minimization
- Purpose limitation
- Consent awareness
- PII masking
- Access controls
- Data retention controls
- Auditability

## RBI Governance Controls

Mandatory:
- Risk governance
- Operational resilience
- Incident monitoring
- Model explainability
- Human approval workflow
- Audit trails
- Traceability
- Data-quality monitoring

---

# Model Evaluation

Evaluate Against Ground Truth

Metrics:
- Precision
- Recall
- F1 Score
- ROC AUC
- False Positive Rate
- False Negative Rate

Operational Metrics:
- SLA detection accuracy
- Incident prioritization accuracy
- Slow API detection rate
- Failed-test prediction accuracy

Governance Metrics:
- Explainability coverage
- Audit completeness
- Compliance score

---

# Technical Stack

Frontend:
- Streamlit
- Plotly
- AgGrid

Backend:
- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost

Visualization:
- Plotly
- Altair
- Streamlit Charts

Monitoring:
- MLflow
- Logging Framework

---

# Success Criteria

The solution is considered successful when it can:

- Detect suspicious banking activity
- Detect SLA breaches automatically
- Detect slow APIs and failures
- Detect recurring production incidents
- Detect data-quality issues
- Explain every risk decision
- Generate actionable recommendations
- Pass governance checks
- Support human review workflow
- Produce measurable evaluation metrics

The system must remain explainable, auditable, compliant, and suitable for enterprise banking environments.
