# -*- coding: utf-8 -*-
"""
配置管理器 - JSON持久化配置
管理主题、仿真参数、语言等所有设置项
"""

import json
import os
import copy

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_CONFIG = {
    "theme": {
        "preset": "light",
        "colors": {
            "bg_primary": "#f5f5f5",
            "bg_secondary": "#ffffff",
            "text_primary": "#1a1a1a",
            "text_secondary": "#666666",
            "text_muted": "#999999",
            "accent": "#4a7aaa",
            "accent_hover": "#3a6a9a",
            "accent_light": "#eaf4fc",
            "tab_selected": "#4a7aaa",
            "border": "#e0e0e0",
            "card_bg": "#ffffff",
            "input_bg": "#ffffff",
            "success": "#2a6a4a",
            "error": "#8b3a3a",
            "warn": "#b8860b"
        },
        "fonts": {
            "size_base": 12,
            "size_title": 16,
            "size_log": 11,
            "size_label": 12,
            "size_small": 10,
            "family": "Microsoft YaHei",
            "scale": 1.0
        }
    },
    "simulation": {
        "snr_range_start": 0,
        "snr_range_end": 26,
        "snr_range_step": 2,
        "modulation": "QPSK",
        "fft_size": 64,
        "cp_len": 16,
        "n_data_carriers": 48,
        "led_power_mw": 100,
        "led_wavelength_nm": 450,
        "led_beam_angle_deg": 120,
        "pd_responsivity": 0.5,
        "pd_area_mm2": 10,
        "pd_dark_current_nA": 10,
        "channel_multipath": False,
        "los_attenuation": 0.7
    },
    "presets": {
        "Standard Simulation": {
            "snr_range_start": 0, "snr_range_end": 26, "snr_range_step": 2,
            "modulation": "QPSK", "fft_size": 64, "cp_len": 16, "n_data_carriers": 48,
            "led_power_mw": 100, "led_wavelength_nm": 450, "led_beam_angle_deg": 120,
            "pd_responsivity": 0.5, "pd_area_mm2": 10, "pd_dark_current_nA": 10,
            "channel_multipath": False, "los_attenuation": 0.7
        },
        "Teaching Demo": {
            "snr_range_start": 0, "snr_range_end": 30, "snr_range_step": 5,
            "modulation": "QPSK", "fft_size": 64, "cp_len": 16, "n_data_carriers": 48,
            "led_power_mw": 50, "led_wavelength_nm": 450, "led_beam_angle_deg": 120,
            "pd_responsivity": 0.3, "pd_area_mm2": 5, "pd_dark_current_nA": 20,
            "channel_multipath": False, "los_attenuation": 0.5
        }
    },
    "log": {
        "level": "INFO",
        "show_on_guide": False,
        "auto_save": False,
        "save_path": "exports",
        "auto_export_results": False
    },
    "language": "en"
}

# Dark Theme Colors
DARK_COLORS = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "text_primary": "#e0e0e0",
    "text_secondary": "#a0a0b0",
    "text_muted": "#6a6a7a",
    "accent": "#4fc3f7",
    "accent_hover": "#29b6f6",
    "accent_light": "#1a2a4a",
    "tab_selected": "#4fc3f7",
    "border": "#2a2a4a",
    "card_bg": "#16213e",
    "input_bg": "#0f3460",
    "success": "#66bb6a",
    "error": "#ef5350",
    "warn": "#ffa726"
}

HIGH_CONTRAST_COLORS = {
    "bg_primary": "#000000",
    "bg_secondary": "#1a1a1a",
    "text_primary": "#ffffff",
    "text_secondary": "#cccccc",
    "text_muted": "#aaaaaa",
    "accent": "#00ccff",
    "accent_hover": "#00aadd",
    "accent_light": "#002244",
    "tab_selected": "#00ccff",
    "border": "#555555",
    "card_bg": "#1a1a1a",
    "input_bg": "#222222",
    "success": "#00ff88",
    "error": "#ff4444",
    "warn": "#ffaa00"
}


class ConfigManager:
    """管理所有配置项的持久化"""

    def __init__(self):
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self._filepath = CONFIG_PATH
        self._load()

    def _load(self):
        if os.path.exists(self._filepath):
            try:
                with open(self._filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._merge(loaded)
            except Exception:
                pass

    def _merge(self, loaded):
        """深度合并加载的配置到默认配置上"""
        def deep_merge(base, override):
            for k, v in override.items():
                if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                    deep_merge(base[k], v)
                else:
                    base[k] = v
        deep_merge(self.config, loaded)

    def save(self):
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, *keys, default=None):
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
                if val is None:
                    return default
            else:
                return default
        return val

    def set(self, *args):
        if len(args) < 2:
            return
        val = self.config
        for k in args[:-2]:
            if k not in val:
                val[k] = {}
            val = val[k]
        key = args[-2]
        val[key] = args[-1]

    def get_theme_colors(self):
        preset = self.get("theme", "preset")
        if preset == "dark":
            return DARK_COLORS
        elif preset == "high_contrast":
            return HIGH_CONTRAST_COLORS
        return self.get("theme", "colors")

    def apply_preset_theme(self, preset_name):
        self.set("theme", "preset", preset_name)
        if preset_name == "dark":
            for k, v in DARK_COLORS.items():
                self.set("theme", "colors", k, v)
        elif preset_name == "high_contrast":
            for k, v in HIGH_CONTRAST_COLORS.items():
                self.set("theme", "colors", k, v)

    def reset_to_defaults(self):
        self.config = copy.deepcopy(DEFAULT_CONFIG)

    def save_preset(self, name, params):
        self.config.setdefault("presets", {})[name] = params

    def delete_preset(self, name):
        self.config.get("presets", {}).pop(name, None)

    def get_preset_names(self):
        return list(self.config.get("presets", {}).keys())

    def get_preset(self, name):
        return self.config.get("presets", {}).get(name, {})


# Singleton
_config_instance = None


def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
