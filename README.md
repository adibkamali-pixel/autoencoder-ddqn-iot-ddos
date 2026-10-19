# Autoencoder-Guided Double DQN for Adaptive IoT DDoS Mitigation

> A leakage-aware research framework combining normal-only anomaly detection and cost-sensitive reinforcement learning for adaptive DDoS mitigation in IoT networks.

## Project Status

**Research design / work in progress.**

This repository currently documents the proposed methodology and experimental protocol. Model implementation, experiments, and numerical results will be added progressively. No performance claims are made at this stage.

## Overview

Distributed Denial-of-Service (DDoS) attacks remain a significant threat to Internet of Things (IoT) networks. Conventional supervised classifiers require labeled attack samples and usually produce only a binary normal/attack decision. They do not directly determine how the network should respond to suspicious traffic.

This project proposes a two-stage framework:

1. An **autoencoder**, trained primarily on normal traffic, learns a representation of legitimate network behavior and produces an anomaly score.
2. A **Double Deep Q-Network (Double DQN)** uses that score and temporal traffic statistics to select a graded mitigation action.

The intended outcome is a mitigation policy that balances attack suppression against disruption to legitimate IoT traffic.

## Proposed Architecture

```text
IoT network traffic
        |
        v
Leakage-aware preprocessing
        |
        v
Temporal feature construction
        |
        v
Normal-only autoencoder
        |
        v
Anomaly score
        |
        v
Cost-sensitive Double DQN
        |
        v
Allow | Monitor | Light rate-limit | Strong rate-limit | Temporary block
```

## Dataset

The primary dataset is **UL-ECE-DDoS-H-IoT-Datasets2025**, containing labeled MQTT and UDP traffic generated using Cooja and ns-3 simulations.

| Subset | Protocol | Samples | Normal | Attack |
|---|---:|---:|---:|---:|
| UL-ECE-MQTT-DDoS-H-IoT2025 | MQTT | 20,080 | 8,950 | 11,130 |
| UL-ECE-UDP-DDoS-H-IoT2025 | UDP | 99,887 | 47,994 | 51,893 |
| **Total** | MQTT + UDP | **119,967** | **56,944** | **63,023** |

Although the dataset originates from a healthcare-IoT simulation, this project focuses on traffic-level DDoS mitigation for MQTT/UDP-based IoT networks in general. It does not use medical or patient data.

Dataset repository: [mirzaakhi/UL-ECE-DDoS-H-IoT-Datasets2025](https://github.com/mirzaakhi/UL-ECE-DDoS-H-IoT-Datasets2025)

## Motivation

The dataset inspection identified an important evaluation risk: device identifiers are strongly associated with the target label. A model may therefore learn which node acted as an attacker instead of learning transferable attack behavior.

The main experiments will exclude raw identifiers such as:

- `node` and `node_id`
- Source and destination IP addresses
- Textual IP descriptions
- Constant protocol and payload columns
- Global counters that may reveal the simulation order

An identifier-based experiment will be retained only as an ablation study to quantify information leakage.

## Feature Strategy

### Candidate observed features

- Current message frequency
- Mean and monitoring frequency
- Per-node message count
- Monitoring-window message count
- Ratio of node messages to total messages

### Derived temporal features

- Frequency change
- Rolling mean
- Rolling standard deviation
- Temporal window statistics
- Autoencoder reconstruction error/anomaly score

MQTT and UDP use different original schemas. Cross-protocol experiments will therefore use an explicitly aligned shared feature space rather than silently treating both schemas as identical.

## Reinforcement-Learning Formulation

### State

The initial state representation is planned to contain:

```text
[
  anomaly_score,
  current_frequency,
  frequency_change,
  rolling_mean,
  rolling_standard_deviation,
  node_message_ratio,
  previous_action
]
```

### Actions

| ID | Action |
|---:|---|
| 0 | Allow |
| 1 | Monitor |
| 2 | Light rate-limit |
| 3 | Strong rate-limit |
| 4 | Temporary block |

### Initial reward design

| Traffic condition | Action | Initial reward |
|---|---|---:|
| Normal | Allow | +2 |
| Normal | Monitor | 0 |
| Normal | Light rate-limit | -2 |
| Normal | Strong rate-limit | -5 |
| Normal | Temporary block | -8 |
| Attack | Allow | -6 |
| Attack | Monitor | -3 |
| Attack | Light rate-limit | +2 |
| Attack | Strong rate-limit | +4 |
| Attack | Temporary block | +5 |

An additional penalty of `-0.5` is initially assigned to excessive action switching. These values are hypotheses, not final parameters, and will be evaluated through reward-sensitivity analysis.

## Experimental Protocol

The planned evaluation includes:

1. **Chronological splitting** as the main train/validation/test strategy.
2. Random splitting only as a comparison with conventional evaluation.
3. Experiments with and without device identifiers to quantify leakage.
4. Rare-attack scenarios containing 10%, 5%, and 1% attack traffic.
5. MQTT-to-UDP and UDP-to-MQTT cross-protocol evaluation.
6. Autoencoder-only versus autoencoder-guided mitigation.
7. DQN versus Double DQN.
8. Reward-function sensitivity and mitigation-cost analysis.
9. Ablation of temporal and monitoring features.

## Baselines

| Category | Methods |
|---|---|
| Unsupervised detection | Isolation Forest, One-Class SVM, Autoencoder |
| Supervised reference | Random Forest, XGBoost |
| Rule-based mitigation | Static threshold |
| Adaptive decision-making | Contextual bandit, DQN, Double DQN |

## Evaluation Metrics

Detection performance:

- Macro-F1
- Precision–Recall AUC
- Matthews Correlation Coefficient
- False-positive rate
- False-negative rate

Mitigation performance:

- Attack mitigation rate
- Legitimate traffic preservation rate
- Average mitigation cost
- Cumulative reward
- Action-switching rate
- Decision latency

Accuracy will not be used as the primary metric in rare-attack experiments.

## Research Questions

- **RQ1:** Can an autoencoder trained on normal traffic identify anomalous DDoS behavior without relying heavily on labeled attack samples?
- **RQ2:** Does Double DQN improve mitigation decisions compared with static thresholds, contextual bandits, and standard DQN?
- **RQ3:** How robust is the framework when attack traffic is rare?
- **RQ4:** How much do device-identity features inflate measured performance?
- **RQ5:** Can the learned representation and mitigation policy generalize between MQTT and UDP traffic?

## Methodological Boundaries

This repository distinguishes detection from mitigation and avoids treating ordinary CSV classification as true online reinforcement learning.

- If an action does not affect the next network state, the experiment will be described as a **contextual-bandit or offline policy simulation**.
- Claims of sequential online RL require an interactive simulator or testbed in which mitigation actions change subsequent traffic, latency, packet loss, or service availability.
- The project will not claim zero-day detection from binary normal/DDoS data alone.
- The project will not claim real-world deployment or QoS improvement without simulator/testbed evidence.

## Planned Repository Structure

```text
.
|-- README.md
|-- requirements.txt
|-- configs/
|   |-- autoencoder.yaml
|   `-- ddqn.yaml
|-- data/
|   `-- README.md
|-- notebooks/
|   |-- 01_data_audit.ipynb
|   `-- 02_leakage_analysis.ipynb
|-- src/
|   |-- data/
|   |-- features/
|   |-- models/
|   |-- agents/
|   |-- environment/
|   `-- evaluation/
|-- tests/
`-- results/
```

The original dataset will not be committed unless its distribution terms and file size are appropriate. Reproducible download/preparation instructions will be provided instead.

## Roadmap

- [x] Inspect dataset structure and class distribution
- [x] Identify identity leakage and constant features
- [x] Define research questions and evaluation guardrails
- [ ] Implement reproducible preprocessing
- [ ] Implement chronological and rare-attack splits
- [ ] Train and evaluate the normal-only autoencoder
- [ ] Implement the contextual-bandit baseline
- [ ] Implement DQN and Double DQN agents
- [ ] Add reward-sensitivity and ablation studies
- [ ] Add an interactive ns-3/Cooja or controlled testbed environment
- [ ] Publish reproducible results and statistical analysis

## Expected Contributions

1. Normal-only anomaly representation learning for IoT traffic.
2. Cost-sensitive selection of graded DDoS mitigation actions.
3. Leakage-aware evaluation excluding device identities from the main model.
4. Rare-attack and MQTT/UDP cross-protocol evaluation.
5. A clear distinction between offline policy evaluation and interactive reinforcement learning.

## Citation

If you use the dataset, cite its associated article:

```bibtex
@article{akhi2025tcn,
  author  = {M. Akhi and C. Eising and L. Luxmi Dhirani},
  title   = {TCN-Based DDoS Detection and Mitigation in 5G Healthcare-IoT:
             A Frequency Monitoring and Dynamic Threshold Approach},
  journal = {IEEE Access},
  volume  = {13},
  pages   = {12709--12733},
  year    = {2025},
  doi     = {10.1109/ACCESS.2025.3531659}
}
```

## License

The code license for this repository has not yet been selected. The dataset is distributed separately under its original license and must be cited according to the dataset authors' requirements.

## Author

**Adib Kamali**  
GitHub: [@adibkamali-pixel](https://github.com/adibkamali-pixel)

