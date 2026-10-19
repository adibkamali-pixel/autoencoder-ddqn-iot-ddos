"""Blueprint penelitian Autoencoder-Guided Double DQN untuk mitigasi DDoS IoT.

File ini sengaja merupakan rangkuman desain, bukan implementasi model final.
Tujuannya menjaga formulasi penelitian tetap konsisten dan menghindari klaim
bahwa klasifikasi CSV biasa adalah reinforcement learning yang sesungguhnya.
"""

from pprint import pprint


RESEARCH = {
    "title": (
        "Autoencoder-Guided Double Deep Q-Network for Adaptive DDoS "
        "Detection and Mitigation in IoT Networks"
    ),
    "objective": (
        "Mempelajari pola trafik normal dengan autoencoder dan memilih tindakan "
        "mitigasi adaptif menggunakan cost-sensitive Double DQN."
    ),
    "dataset": {
        "name": "UL-ECE-DDoS-H-IoT-Datasets2025",
        "mqtt": {"rows": 20_080, "normal": 8_950, "attack": 11_130},
        "udp": {"rows": 99_887, "normal": 47_994, "attack": 51_893},
        "positioning": (
            "Dataset berasal dari simulasi healthcare-IoT, tetapi framework "
            "diposisikan untuk jaringan IoT berbasis MQTT/UDP secara umum."
        ),
    },
    "pipeline": [
        "IoT traffic",
        "Leakage-aware preprocessing",
        "Temporal feature construction",
        "Normal-only autoencoder",
        "Anomaly score",
        "Double DQN mitigation agent",
        "Allow / Monitor / Light rate-limit / Strong rate-limit / Temporary block",
    ],
}


FEATURE_POLICY = {
    "mqtt_keep": [
        "frequency",
        "total_messages_each_node",
    ],
    "udp_keep": [
        "frequency",
        "mean_frequency",
        "monitoring_frequency",
        "total_messages_same_node",
        "monitoring_total_messages_same_node",
    ],
    "derived_features": [
        "frequency_change",
        "rolling_mean",
        "rolling_standard_deviation",
        "node_message_ratio",
        "autoencoder_anomaly_score",
    ],
    "exclude_from_main_experiment": [
        "node",
        "node_id",
        "source_ip",
        "source_ip_des",
        "destination_ip",
        "destination_ip_des",
        "protocol_des",
        "constant columns",
        "global counters that reveal experiment order",
    ],
    "reason": (
        "Identifier dan beberapa counter sangat berkorelasi dengan label sehingga "
        "dapat menyebabkan model menghafal identitas attacker."
    ),
}


RL_DESIGN = {
    "state": [
        "anomaly_score",
        "current_frequency",
        "frequency_change",
        "rolling_mean",
        "rolling_standard_deviation",
        "node_message_ratio",
        "previous_action",
    ],
    "actions": {
        0: "allow",
        1: "monitor",
        2: "light_rate_limit",
        3: "strong_rate_limit",
        4: "temporary_block",
    },
    "initial_reward": {
        ("normal", "allow"): 2.0,
        ("normal", "monitor"): 0.0,
        ("normal", "light_rate_limit"): -2.0,
        ("normal", "strong_rate_limit"): -5.0,
        ("normal", "temporary_block"): -8.0,
        ("attack", "allow"): -6.0,
        ("attack", "monitor"): -3.0,
        ("attack", "light_rate_limit"): 2.0,
        ("attack", "strong_rate_limit"): 4.0,
        ("attack", "temporary_block"): 5.0,
    },
    "action_switch_penalty": -0.5,
    "reward_note": (
        "Reward adalah konfigurasi awal dan wajib diuji melalui sensitivity analysis."
    ),
}


EXPERIMENTS = [
    "E1: Random split hanya sebagai pembanding, bukan hasil utama.",
    "E2: Chronological train/validation/test split.",
    "E3: Ablation dengan dan tanpa identifier untuk mengukur leakage.",
    "E4: Rare-attack ratios 10%, 5%, dan 1%.",
    "E5: Train MQTT lalu test UDP menggunakan shared feature space.",
    "E6: Train UDP lalu test MQTT menggunakan shared feature space.",
    "E7: Autoencoder-only versus autoencoder + mitigation agent.",
    "E8: DQN versus Double DQN.",
    "E9: Reward sensitivity dan action-cost analysis.",
]


BASELINES = {
    "anomaly_detection": ["Isolation Forest", "One-Class SVM", "Autoencoder"],
    "supervised_reference": ["Random Forest", "XGBoost"],
    "mitigation": ["Static threshold", "Contextual bandit", "DQN", "Double DQN"],
}


METRICS = {
    "detection": ["Macro-F1", "PR-AUC", "MCC", "FPR", "FNR"],
    "mitigation": [
        "attack_mitigation_rate",
        "legitimate_traffic_preservation_rate",
        "average_mitigation_cost",
    ],
    "rl": ["cumulative_reward", "action_switching_rate", "decision_latency"],
}


METHODOLOGICAL_GUARDRAILS = [
    "Jangan menyebut CSV replay sebagai online RL atau real-world deployment.",
    "Jika action tidak memengaruhi next state, sebut formulasi sebagai contextual bandit.",
    "True sequential RL memerlukan simulator/testbed agar tindakan mengubah jaringan.",
    "Jangan mengklaim zero-day; gunakan unseen-node atau cross-protocol generalization.",
    "Jangan memakai accuracy sebagai metrik utama pada rare-attack setting.",
    "Jangan melaporkan hasil final sebelum eksperimen dan statistical testing selesai.",
]


ABSTRACT_SUMMARY = (
    "Penelitian mengusulkan framework deteksi dan mitigasi DDoS adaptif untuk IoT. "
    "Autoencoder dilatih hanya pada trafik normal untuk menghasilkan anomaly score. "
    "Double DQN kemudian memilih tindakan mitigasi bertingkat dengan reward yang "
    "menghukum false blocking lebih berat. Evaluasi utama menggunakan chronological "
    "split, penghapusan fitur identitas, rare-attack scenarios, cross-protocol testing, "
    "dan ablation study."
)


def print_blueprint() -> None:
    """Cetak rangkuman penelitian dalam format yang mudah dibaca."""
    sections = {
        "RESEARCH": RESEARCH,
        "ABSTRACT SUMMARY": ABSTRACT_SUMMARY,
        "FEATURE POLICY": FEATURE_POLICY,
        "RL DESIGN": RL_DESIGN,
        "EXPERIMENTS": EXPERIMENTS,
        "BASELINES": BASELINES,
        "METRICS": METRICS,
        "METHODOLOGICAL GUARDRAILS": METHODOLOGICAL_GUARDRAILS,
    }
    for title, content in sections.items():
        print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")
        pprint(content, sort_dicts=False, width=100)


if __name__ == "__main__":
    print_blueprint()
