# -*- coding: utf-8 -*-
"""
国际化模块 - 中英文双语支持
"""

class I18n:
    def __init__(self, lang="en"):
        self._lang = lang
        self._strings = _EN if lang == "en" else _ZH

    def set_language(self, lang):
        self._lang = lang
        self._strings = _EN if lang == "en" else _ZH

    def tr(self, key, default=None):
        return self._strings.get(key, default or key)

    @property
    def lang(self):
        return self._lang


_EN = {
    # Window Titles
    "window_title": "VLC Intelligent Demodulation System  v2.0",
    "main_title": "VLC INTELLIGENT DEMODULATION SYSTEM",
    "main_subtitle": "Visible Light Communication  \u00b7  Signal Intelligence Platform",
    "status_standby": "\u25cf  STANDBY",
    "status_running": "\u25cf  RUNNING",
    "status_ready": "\u25cf  READY",
    "status_error": "\u25cf  ERROR",

    # Tabs
    "tab_guide": "  OPERATION GUIDE  ",
    "tab_waveform": "WAVEFORM",
    "tab_constellation": "CONSTELLATION",
    "tab_eye": "EYE DIAGRAM",
    "tab_ber": "BER",
    "tab_settings": "  SETTINGS  ",

    # Left Panel
    "group_system_control": "System Control",
    "snr_label": "SNR (dB)",
    "data_length": "Data Length",
    "btn_run": "\u25b6  Run Simulation",
    "btn_train": "Train AI",
    "btn_ber_sweep": "BER Sweep",
    "btn_clear_log": "Clear Log",

    "group_system_params": "System Parameters",
    "param_modulation": "Modulation",
    "param_fft": "FFT Size",
    "param_cp": "Cyclic Prefix",
    "param_carriers": "Data Carriers",
    "param_led": "LED",
    "param_detector": "Detector",
    "param_channel": "Channel",

    "group_results": "Results",
    "result_tx_bits": "TX Bits",
    "result_errors": "Errors",
    "result_ber": "BER",
    "result_snr": "SNR",
    "result_confidence": "Confidence",
    "result_latency": "Latency",

    "log_label": "LOG",
    "default_value": "--",

    # Operation Guide
    "guide_header": "VLC Transmission Pipeline \u2014 Operation Guide",
    "guide_subtitle": "This guide describes each processing step in the Visible Light Communication (VLC) signal chain, from data generation through OFDM modulation, optical transmission, channel propagation, detection, demodulation, AI-based decoding, and final BER analysis.",

    # Settings Tab - Theme
    "settings_title": "System Settings",
    "settings_theme": "Theme & Colors",
    "settings_preset_light": "\u2600 Light Mode",
    "settings_preset_dark": "\u263e Dark Mode",
    "settings_preset_hc": "\u25a3 High Contrast",
    "settings_accent_color": "Accent Color",
    "settings_bg_color": "Background Color",
    "settings_text_color": "Text Color",
    "settings_tab_color": "Tab Selected Color",

    # Settings Tab - Fonts
    "settings_fonts": "Font & Typography",
    "settings_font_size": "Base Font Size",
    "settings_font_title": "Title Size",
    "settings_font_log": "Log Size",
    "settings_font_family": "Font Family",
    "settings_scale": "UI Scale",

    # Settings Tab - Simulation
    "settings_sim_presets": "Simulation Presets",
    "settings_save_preset": "Save Preset",
    "settings_load_preset": "Load Preset",
    "settings_delete_preset": "Delete Preset",
    "settings_reset_defaults": "Reset to Defaults",
    "settings_preset_name": "Preset Name",

    # Settings Tab - Log
    "settings_log": "Log & Output",
    "settings_log_level": "Log Level",
    "settings_error": "ERROR",
    "settings_info": "INFO",
    "settings_debug": "DEBUG",
    "settings_hide_log_guide": "Hide Log on Guide Tab",
    "settings_auto_save": "Auto-save Log",
    "settings_save_path": "Save Path",
    "settings_auto_export": "Auto-export Results",

    # Settings Tab - Language
    "settings_language": "Language / \u8bed\u8a00",
    "lang_en": "English",
    "lang_zh": "\u4e2d\u6587",

    # Settings Tab - Actions
    "btn_apply": "Apply Changes",
    "btn_reapply": "Apply & Restart",

    # Messages
    "msg_initialized": "System initialized. VLC Intelligent Demodulation Platform ready.",
    "msg_start_sim": "Starting VLC simulation...",
    "msg_sim_done": "Done | bits={bits} | BER={ber} | SNR={snr}dB | {time}ms",
    "msg_training": "Training AI demodulation model...",
    "msg_train_done": "AI model trained | accuracy={acc:.2%} | {time}ms",
    "msg_ber_sweep": "Running BER sweep...",
    "msg_ber_done": "BER scan complete | range={range}dB",
    "msg_config_saved": "Configuration saved.",
    "msg_config_loaded": "Configuration loaded.",
    "msg_preset_saved": "Preset \"{name}\" saved.",
    "msg_preset_loaded": "Preset \"{name}\" loaded.",
    "msg_preset_deleted": "Preset \"{name}\" deleted.",
    "msg_reset_done": "All settings reset to defaults.",
    "msg_theme_applied": "Theme applied: {theme}",
    "msg_lang_changed": "Language changed to {lang}.",
    "msg_log_saved": "Log saved to {path}",
    "msg_export_done": "Results exported to {path}",
    "msg_error": "Error: {msg}",
    "msg_restart_required": "Some changes will take effect after restart.",

    # Log level prefixes
    "log_error": "ERROR",
    "log_info": "INFO",
    "log_debug": "DEBUG",

    # Guide step titles
    "step_data": "Data Source Generation",
    "step_ofdm": "OFDM Modulation",
    "step_led": "LED Optical Transmission",
    "step_ch": "Optical Wireless Channel",
    "step_pd": "Photodetection (Receiver Front-End)",
    "step_demod": "OFDM Demodulation",
    "step_ai": "AI-Powered Decoding",
    "step_ber": "BER Analysis",

    # Modulations
    'mod_bpsk': 'BPSK',
    'mod_qpsk': 'QPSK',
    'mod_16qam': '16-QAM',
    'mod_64qam': '64-QAM',

    # AI Models
    'ai_mlp': 'MLP Neural Network',
    'ai_cnn': 'CNN-like Network',
    'ai_lstm': 'LSTM-like Network',

    # Export
    'btn_save': 'Save Result',
    'btn_export': 'Export Data',
    'btn_results': 'Results History',
    'msg_saved': 'Result saved: {name}',
    'msg_exported': 'Exported to: {path}',
    'results_title': 'Saved Results',
    'results_empty': 'No saved results yet.',
    'results_delete': 'Delete',
    'results_load': 'Load',
    'results_export': 'Export',
}

_ZH = {
    "window_title": "VLC\u667a\u80fd\u89e3\u8c03\u7cfb\u7edf  v2.0",
    "main_title": "VLC \u667a\u80fd\u89e3\u8c03\u7cfb\u7edf",
    "main_subtitle": "\u53ef\u89c1\u5149\u901a\u4fe1  \u00b7  \u4fe1\u53f7\u667a\u80fd\u5904\u7406\u5e73\u53f0",
    "status_standby": "\u25cf  \u5f85\u673a",
    "status_running": "\u25cf  \u8fd0\u884c\u4e2d",
    "status_ready": "\u25cf  \u5c31\u7eea",
    "status_error": "\u25cf  \u9519\u8bef",

    "tab_guide": "  \u64cd\u4f5c\u6307\u5357  ",
    "tab_waveform": "\u6ce2\u5f62",
    "tab_constellation": "\u661f\u5ea7\u56fe",
    "tab_eye": "\u773c\u56fe",
    "tab_ber": "BER\u66f2\u7ebf",
    "tab_settings": "  \u7cfb\u7edf\u8bbe\u7f6e  ",

    "group_system_control": "\u7cfb\u7edf\u63a7\u5236",
    "snr_label": "\u4fe1\u566a\u6bd4 SNR (dB)",
    "data_length": "\u6570\u636e\u957f\u5ea6",
    "btn_run": "\u25b6  \u5f00\u59cb\u4eff\u771f",
    "btn_train": "\u8bad\u7ec3 AI",
    "btn_ber_sweep": "BER \u626b\u63cf",
    "btn_clear_log": "\u6e05\u9664\u65e5\u5fd7",

    "group_system_params": "\u7cfb\u7edf\u53c2\u6570",
    "param_modulation": "\u8c03\u5236\u65b9\u5f0f",
    "param_fft": "FFT \u5927\u5c0f",
    "param_cp": "\u5faa\u73af\u524d\u7f00",
    "param_carriers": "\u6570\u636e\u8f7d\u6ce2",
    "param_led": "LED \u5149\u6e90",
    "param_detector": "\u68c0\u6d4b\u5668",
    "param_channel": "\u4fe1\u9053\u6a21\u578b",

    "group_results": "\u4eff\u771f\u7ed3\u679c",
    "result_tx_bits": "\u53d1\u9001\u6bd4\u7279",
    "result_errors": "\u8bef\u7801\u6570",
    "result_ber": "\u8bef\u7801\u7387 BER",
    "result_snr": "\u4fe1\u566a\u6bd4",
    "result_confidence": "\u53ef\u4fe1\u5ea6",
    "result_latency": "\u5ef6\u8fdf",

    "log_label": "\u65e5\u5fd7",
    "default_value": "--",

    "guide_header": "VLC \u4f20\u8f93\u6d41\u7a0b \u2014 \u64cd\u4f5c\u6307\u5357",
    "guide_subtitle": "\u672c\u6307\u5357\u63cf\u8ff0\u4e86\u53ef\u89c1\u5149\u901a\u4fe1\uff08VLC\uff09\u4fe1\u53f7\u94fe\u4e2d\u7684\u6bcf\u4e00\u4e2a\u5904\u7406\u6b65\u9aa4\uff0c\u4ece\u6570\u636e\u751f\u6210\u3001OFDM\u8c03\u5236\u3001\u5149\u4fe1\u53f7\u53d1\u5c04\u3001\u4fe1\u9053\u4f20\u64ad\u3001\u5149\u7535\u68c0\u6d4b\u3001\u89e3\u8c03\u3001AI\u667a\u80fd\u89e3\u7801\u5230\u6700\u7ec8\u7684BER\u5206\u6790\u3002",

    "settings_title": "\u7cfb\u7edf\u8bbe\u7f6e",
    "settings_theme": "\u4e3b\u9898\u4e0e\u914d\u8272",
    "settings_preset_light": "\u2600 \u6d45\u8272\u6a21\u5f0f",
    "settings_preset_dark": "\u263e \u6df1\u8272\u6a21\u5f0f",
    "settings_preset_hc": "\u25a3 \u9ad8\u5bf9\u6bd4\u5ea6",
    "settings_accent_color": "\u5f3a\u8c03\u8272",
    "settings_bg_color": "\u80cc\u666f\u8272",
    "settings_text_color": "\u6587\u672c\u989c\u8272",
    "settings_tab_color": "\u6807\u7b7e\u9009\u4e2d\u8272",

    "settings_fonts": "\u5b57\u4f53\u4e0e\u6392\u7248",
    "settings_font_size": "\u57fa\u7840\u5b57\u53f7",
    "settings_font_title": "\u6807\u9898\u5b57\u53f7",
    "settings_font_log": "\u65e5\u5fd7\u5b57\u53f7",
    "settings_font_family": "\u5b57\u4f53\u7c7b\u578b",
    "settings_scale": "\u754c\u9762\u7f29\u653e",

    "settings_sim_presets": "\u4eff\u771f\u9884\u8bbe",
    "settings_save_preset": "\u4fdd\u5b58\u9884\u8bbe",
    "settings_load_preset": "\u52a0\u8f7d\u9884\u8bbe",
    "settings_delete_preset": "\u5220\u9664\u9884\u8bbe",
    "settings_reset_defaults": "\u6062\u590d\u9ed8\u8ba4\u53c2\u6570",
    "settings_preset_name": "\u9884\u8bbe\u540d\u79f0",

    "settings_log": "\u65e5\u5fd7\u4e0e\u8f93\u51fa",
    "settings_log_level": "\u65e5\u5fd7\u7ea7\u522b",
    "settings_error": "\u9519\u8bef",
    "settings_info": "\u4fe1\u606f",
    "settings_debug": "\u8c03\u8bd5",
    "settings_hide_log_guide": "\u64cd\u4f5c\u6307\u5357\u9875\u9690\u85cf\u65e5\u5fd7",
    "settings_auto_save": "\u81ea\u52a8\u4fdd\u5b58\u65e5\u5fd7",
    "settings_save_path": "\u4fdd\u5b58\u8def\u5f84",
    "settings_auto_export": "\u81ea\u52a8\u5bfc\u51fa\u7ed3\u679c",

    "settings_language": "\u8bed\u8a00 / Language",
    "lang_en": "English",
    "lang_zh": "\u4e2d\u6587",

    "btn_apply": "\u5e94\u7528\u8bbe\u7f6e",
    "btn_reapply": "\u5e94\u7528\u5e76\u91cd\u542f",

    "msg_initialized": "\u7cfb\u7edf\u521d\u59cb\u5316\u5b8c\u6210\u3002VLC\u667a\u80fd\u89e3\u8c03\u5e73\u53f0\u5c31\u7eea\u3002",
    "msg_start_sim": "\u6b63\u5728\u542f\u52a8 VLC \u4eff\u771f...",
    "msg_sim_done": "\u5b8c\u6210 | \u6bd4\u7279\u6570={bits} | BER={ber} | SNR={snr}dB | {time}ms",
    "msg_training": "\u6b63\u5728\u8bad\u7ec3 AI \u89e3\u8c03\u6a21\u578b...",
    "msg_train_done": "AI \u6a21\u578b\u8bad\u7ec3\u5b8c\u6210 | \u51c6\u786e\u7387={acc:.2%} | {time}ms",
    "msg_ber_sweep": "\u6b63\u5728\u6267\u884c BER \u626b\u63cf...",
    "msg_ber_done": "BER \u626b\u63cf\u5b8c\u6210 | \u8303\u56f4={range}dB",
    "msg_config_saved": "\u914d\u7f6e\u5df2\u4fdd\u5b58\u3002",
    "msg_config_loaded": "\u914d\u7f6e\u5df2\u52a0\u8f7d\u3002",
    "msg_preset_saved": "\u9884\u8bbe\u201c{name}\u201d\u5df2\u4fdd\u5b58\u3002",
    "msg_preset_loaded": "\u9884\u8bbe\u201c{name}\u201d\u5df2\u52a0\u8f7d\u3002",
    "msg_preset_deleted": "\u9884\u8bbe\u201c{name}\u201d\u5df2\u5220\u9664\u3002",
    "msg_reset_done": "\u6240\u6709\u8bbe\u7f6e\u5df2\u6062\u590d\u9ed8\u8ba4\u3002",
    "msg_theme_applied": "\u4e3b\u9898\u5df2\u5e94\u7528\uff1a{theme}",
    "msg_lang_changed": "\u8bed\u8a00\u5df2\u5207\u6362\u4e3a {lang}\u3002\u90e8\u5206\u6807\u7b7e\u53ef\u80fd\u9700\u8981\u91cd\u542f\u540e\u751f\u6548\u3002",
    "msg_log_saved": "\u65e5\u5fd7\u5df2\u4fdd\u5b58\u5230 {path}",
    "msg_export_done": "\u7ed3\u679c\u5df2\u5bfc\u51fa\u5230 {path}",
    "msg_error": "\u9519\u8bef\uff1a{msg}",
    "msg_restart_required": "\u90e8\u5206\u8bbe\u7f6e\u5c06\u5728\u91cd\u542f\u540e\u751f\u6548\u3002",

    "log_error": "\u9519\u8bef",
    "log_info": "\u4fe1\u606f",
    "log_debug": "\u8c03\u8bd5",

    "step_data": "\u6570\u636e\u6e90\u751f\u6210",
    "step_ofdm": "OFDM \u8c03\u5236",
    "step_led": "LED \u5149\u53d1\u5c04",
    "step_ch": "\u5149\u4fe1\u9053\u4f20\u64ad",
    "step_pd": "\u5149\u7535\u68c0\u6d4b",
    "step_demod": "OFDM \u89e3\u8c03",
    "step_ai": "AI \u667a\u80fd\u89e3\u7801",
    "step_ber": "BER \u8bef\u7801\u7387\u5206\u6790",

    # Modulations
    'mod_bpsk': 'BPSK',
    'mod_qpsk': 'QPSK',
    'mod_16qam': '16-QAM',
    'mod_64qam': '64-QAM',

    # AI Models
    'ai_mlp': 'MLP Neural Network',
    'ai_cnn': 'CNN-like Network',
    'ai_lstm': 'LSTM-like Network',

    # Export
    'btn_save': 'Save Result',
    'btn_export': 'Export Data',
    'btn_results': 'Results History',
    'msg_saved': 'Result saved: {name}',
    'msg_exported': 'Exported to: {path}',
    'results_title': 'Saved Results',
    'results_empty': 'No saved results yet.',
    'results_delete': 'Delete',
    'results_load': 'Load',
    'results_export': 'Export',

    # Modulations
    'mod_bpsk': 'BPSK',
    'mod_qpsk': 'QPSK',
    'mod_16qam': '16-QAM',
    'mod_64qam': '64-QAM',

    # AI Models
    'ai_mlp': '神经网络 MLP',
    'ai_cnn': '卷积网络 CNN',
    'ai_lstm': '循环网络 LSTM',

    # Export
    'btn_save': '保存结果',
    'btn_export': '导出数据',
    'btn_results': '历史记录',
    'msg_saved': '结果已保存: {name}',
    'msg_exported': '已导出到: {path}',
    'results_title': '已保存的结果',
    'results_empty': '暂无保存的记录。',
    'results_delete': '删除',
    'results_load': '加载',
    'results_export': '导出',
}


_i18n_instance = None


def get_i18n():
    global _i18n_instance
    if _i18n_instance is None:
        from .config_manager import get_config
        cfg = get_config()
        _i18n_instance = I18n(cfg.config.get("language", "en"))
    return _i18n_instance


def reload_i18n():
    global _i18n_instance
    from .config_manager import get_config
    cfg = get_config()
    _i18n_instance = I18n(cfg.config.get("language", "en"))
