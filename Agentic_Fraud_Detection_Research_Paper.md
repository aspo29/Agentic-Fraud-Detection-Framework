# Agentic Fraud Detection Framework: A Multi-Agent Machine Learning Approach

**Track B — Security & Fraud**

## Abstract
A multi-agent ML system designed to evaluate each transaction through multiple specialized models, synthesize verdicts via a context-aware orchestrator, and trigger dual-path OTP verification when fraudulent activity is suspected. This framework addresses the critical latency and accuracy requirements of modern digital finance by distributing the risk assessment across highly specialized, independent AI agents.

## 1. Introduction
With the rapid acceleration of digital transactions, financial institutions face unprecedented challenges in accurately identifying fraud in real-time. Traditional rule-based systems and monolithic machine learning models often struggle to balance high detection rates with low false-positive rates (customer friction). 

The **Agentic Fraud Detection Framework** introduces a modular, multi-agent architecture where specialized AI agents evaluate different aspects of a transaction in parallel. A context-aware orchestrator synthesizes these independent signals, optimizing the decision-making process to either allow, instantly block, or trigger an adaptive friction mechanism such as a Dual-Path OTP Interlock.

### Real-World Scenario
Consider an active account belonging to "Sita." Her account shows an NRs 85,000 eSewa transfer to an unfamiliar merchant at 2:14 AM. This sharply deviates from her historical pattern of daytime grocery payments. In our framework:
- The **Velocity Agent** flags the high-frequency nature of the transfer.
- The **Geo Agent** detects an anomaly: a new device fingerprint in Dharan, while her registered phone's last known location is Kathmandu.
- The **Synthesis Agent** weighs these signals based on the transaction context (P2P transfer vs. merchant payment) and decides the next step: block instantly, trigger a dual-path OTP, or allow it to pass.

## 2. Agent Pipeline & Architecture

The framework distributes cognitive load across four specialized agents:

### 2.1 Velocity Agent 🔢
- **Role**: Transaction frequency rules and sliding-window anomaly detection.
- **Mechanism**: Monitors transaction frequency in sliding time windows using Redis-backed caching. Flags accounts showing unusual bursts—e.g., 10 transactions in 2 minutes versus the user's average of 1 per hour.
- **Innovation**: Employs an ultra-low latency Lua script execution on Redis clusters to evaluate complex temporal rules without network round-trips.

### 2.2 Geo Agent 🌍
- **Role**: Location anomaly and impossible travel detection.
- **Mechanism**: Detects geolocation impossibilities (e.g., a user transacting in Kathmandu and Dharan within 30 minutes) and new device fingerprints not seen in the account's history.
- **Innovation**: Utilizes geospatial indexing combined with device fingerprint embeddings to identify sophisticated location-spoofing techniques.

### 2.3 Behavior Agent 🧠
- **Role**: User pattern ML and sequence modeling.
- **Mechanism**: An LSTM (Long Short-Term Memory) model trained on each user's personal transaction history (merchant categories, time-of-day, typical transaction amounts). Scores how "normal" a new transaction looks against the individual's baseline.
- **Innovation**: Transitions from global thresholding to hyper-personalized behavior baselines. To address the cold-start problem, new users are assigned to behavioral cohorts using k-means clustering until sufficient personal data is gathered.

### 2.4 Synthesis Agent 🔀
- **Role**: Context-aware verdict synthesis.
- **Mechanism**: Context-aware weighted voting. The nature of the transaction dynamically determines model weights. For instance, high-value P2P transfers heavily weight the Graph Neural Net (account linkage), while QR payments place more emphasis on the Velocity Agent.
- **Innovation**: Replaces static ensemble averaging with a dynamic Attention Mechanism, allowing the Synthesis Agent to "focus" on the most relevant sub-agent based on the transaction's metadata.

### 2.5 OTP Interlock 🔒
- **Role**: Email + SMS dual-path verification.
- **Mechanism**: Both Email OTP and SMS OTP must be confirmed within a specific time window. If either channel fails (e.g., due to a SIM-swap attack), the system automatically escalates the case to full manual account review.
- **Innovation**: Mitigates single-point-of-failure vulnerabilities in traditional 2FA systems, significantly raising the barrier for successful account takeovers (ATO).

## 3. Technical Specifications

### 3.1 ML Models
- **Isolation Forest**: Utilized for unsupervised anomaly detection (e.g., identifying outliers in amount and frequency).
- **LSTM (Long Short-Term Memory)**: Captures sequential behavioral patterns over time.
- **Random Forest**: Serves as a robust ensemble for evaluating explicit and derived rules.
- **Graph Neural Network (GNN)**: Analyzes account linkages (Neo4j) to uncover coordinated fraud rings and money laundering networks.

### 3.2 Synthesis Logic
- **Context-Aware Weighted Voting**: Transaction context dynamically scales the importance of each agent. A deep learning meta-model predicts the optimal weight distribution for the current transaction type in real-time.

### 3.3 Security Protocol
- **Dual-Path Interlock**: Enforces an AND condition for Email OTP and SMS OTP confirmation within a strict TTL. If compromised, escalates to Step-Up authentication or manual review.

### 3.4 Latency Targets
- **End-to-End Verdict**: < 800ms (p95) for real-time transaction blocking. The pipeline leverages asynchronous processing and gRPC/Kafka to ensure minimal overhead.

## 4. Suggested Tech Stack
- **Deep Learning**: PyTorch / TensorFlow
- **Event Streaming**: Apache Kafka (Real-time data ingestion and inter-service communication)
- **Caching & State**: Redis (ZSETs for sliding velocity windows)
- **Graph Database**: Neo4j (Entity linkage and GNN feature extraction)
- **Communications**: Twilio / Sparrow SMS (Dual-path OTP delivery)
- **Model Lifecycle**: MLflow (Tracking experiments, model registry, and performance drift)
- **API & Backend**: FastAPI / Python

## 5. Key Challenges & Innovative Solutions

### Challenge 1: Minimizing False Positives (Legitimate customers blocked = churn)
**Solution**: The implementation of the *Behavior Agent* allows the system to recognize that what is abnormal for the general population might be perfectly normal for a specific high-net-worth individual. Furthermore, instead of outright blocking ambiguous transactions, the *Synthesis Agent* triggers the *OTP Interlock*, offering a frictionless recovery path for legitimate users.

### Challenge 2: Context-Aware Weight Adaptation
**Solution**: The *Synthesis Agent* utilizes a self-attention layer trained on historical fraud data. If the transaction is a remittance, the attention layer shifts focus to the GNN (to verify recipient trustworthiness). If it's a POS transaction, it shifts to the Geo Agent.

### Challenge 3: The Cold-Start Problem (New users with no behavioral history)
**Solution**: Implementation of *Cohort-Based Baselines*. Upon onboarding, a user is classified into a micro-segment based on KYC data (e.g., "urban student", "rural merchant"). The Behavior Agent applies the cohort's baseline to evaluate the user's transactions until enough personalized data points are collected to fine-tune an individualized LSTM model.

### Challenge 4: SIM-Swap Attacks
**Solution**: The *Dual-Path OTP Interlock* specifically mitigates SIM-swaps. Since SMS can be intercepted by an attacker who port-outs a user's number, the requirement for a simultaneous Email OTP (which requires separate credentials and often its own 2FA) ensures the attacker cannot complete the transaction with just the compromised phone number.

## 6. Conclusion
The Agentic Fraud Detection Framework represents a paradigm shift from monolithic scoring systems to a decentralized, agent-based intelligence architecture. By breaking down the complex problem of fraud detection into independent, specialized domains (Velocity, Geo, Behavior), and intelligently synthesizing their outputs, financial institutions can achieve state-of-the-art security without compromising the user experience.
