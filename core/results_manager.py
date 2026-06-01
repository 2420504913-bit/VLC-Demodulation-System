# -*- coding: utf-8 -*-
"""
结果管理器 - 保存/加载/导出仿真结果
"""

import json
import os
import time
import numpy as np

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


def _ensure_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def _timestamp():
    return time.strftime("%Y%m%d_%H%M%S")


def save_result(result, name=None):
    """保存仿真结果到JSON文件"""
    _ensure_dir()
    ts = _timestamp()
    label = name or f"sim_{ts}"
    filename = f"{label}.json"
    filepath = os.path.join(RESULTS_DIR, filename)

    # Extract serializable data
    data = {
        "name": label,
        "timestamp": ts,
        "snr_db": result.get("snr_db", 0),
        "ber": float(result.get("ber", 0)),
        "n_bits": len(result.get("tx_bits", [])),
        "n_errors": int(np.sum(np.array(result.get("tx_bits", [])[:len(result.get("rx_bits", []))]) != np.array(result.get("rx_bits", [])))),
        "modulation": result.get("modulation", "QPSK"),
        "ai_model": result.get("ai_model", "MLP"),
        "tx_bits": result.get("tx_bits", []).tolist() if hasattr(result.get("tx_bits"), 'tolist') else list(result.get("tx_bits", [])),
        "rx_bits": result.get("rx_bits", []).tolist() if hasattr(result.get("rx_bits"), 'tolist') else list(result.get("rx_bits", [])),
        "ber_curve_snrs": result.get("ber_curve_snrs", []),
        "ber_curve_bers": result.get("ber_curve_bers", []),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath, label


def list_results():
    """列出所有已保存的结果"""
    _ensure_dir()
    files = sorted(
        [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")],
        reverse=True
    )
    entries = []
    for fname in files:
        fpath = os.path.join(RESULTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries.append({
                "file": fname,
                "path": fpath,
                "name": data.get("name", fname),
                "timestamp": data.get("timestamp", ""),
                "snr_db": data.get("snr_db", 0),
                "ber": data.get("ber", 0),
                "n_bits": data.get("n_bits", 0),
                "n_errors": data.get("n_errors", 0),
                "modulation": data.get("modulation", "QPSK"),
                "ai_model": data.get("ai_model", "MLP"),
            })
        except Exception:
            pass
    return entries


def load_result(filepath):
    """加载指定结果文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_result(filepath):
    """删除结果文件"""
    if os.path.exists(filepath):
        os.remove(filepath)


def export_result_text(filepath, output_path):
    """导出结果为可读文本"""
    data = load_result(filepath)
    lines = [
        "=" * 60,
        "VLC Simulation Results Export",
        "=" * 60,
        f"Name:       {data.get('name', 'N/A')}",
        f"Timestamp:  {data.get('timestamp', 'N/A')}",
        f"Modulation: {data.get('modulation', 'QPSK')}",
        f"AI Model:   {data.get('ai_model', 'MLP')}",
        f"SNR:        {data.get('snr_db', 0)} dB",
        f"Bits:       {data.get('n_bits', 0)}",
        f"Errors:     {data.get('n_errors', 0)}",
        f"BER:        {data.get('ber', 0):.6e}",
        "-" * 60,
        "TX Bits (first 64):",
        "".join(str(b) for b in data.get("tx_bits", [])[:64]),
        "",
        "RX Bits (first 64):",
        "".join(str(b) for b in data.get("rx_bits", [])[:64]),
        "-" * 60,
    ]
    if data.get("ber_curve_snrs"):
        lines.append("BER Curve:")
        for s, b in zip(data["ber_curve_snrs"], data["ber_curve_bers"]):
            lines.append(f"  SNR={s:2d}dB  BER={b:.6e}")
        lines.append("-" * 60)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path
