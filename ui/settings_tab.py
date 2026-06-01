# -*- coding: utf-8 -*-
"""
系统设置标签页 - 集成主题预设、字体、仿真预设、日志、语言配置
"""

import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.config_manager import get_config, DARK_COLORS, HIGH_CONTRAST_COLORS
from core.i18n import get_i18n, reload_i18n


class SettingsTab(QWidget):
    """系统设置标签页"""

    # Signal: parent main_window should connect to this
    themeChanged = pyqtSignal(dict)       # color dict
    fontChanged = pyqtSignal(dict)        # font settings
    presetLoaded = pyqtSignal(dict)       # sim params
    languageChanged = pyqtSignal(str)     # "en" or "zh"
    restartRequired = pyqtSignal()
    logSettingsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cfg = get_config()
        self._i18n = get_i18n()
        self._init_ui()
        self._load_config()

    def tr(self, key):
        return self._i18n.tr(key)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(16)

        # ===== Theme Section =====
        theme_group = QGroupBox(self.tr("settings_theme"))
        theme_grid = QGridLayout(theme_group)
        theme_grid.setSpacing(8)
        theme_grid.setContentsMargins(12, 20, 12, 12)

        # Theme presets row
        self.btn_light = QPushButton(self.tr("settings_preset_light"))
        self.btn_light.setObjectName("btnSecondary")
        self.btn_light.clicked.connect(lambda: self._apply_preset("light"))

        self.btn_dark = QPushButton(self.tr("settings_preset_dark"))
        self.btn_dark.setObjectName("btnSecondary")
        self.btn_dark.clicked.connect(lambda: self._apply_preset("dark"))

        self.btn_hc = QPushButton(self.tr("settings_preset_hc"))
        self.btn_hc.setObjectName("btnSecondary")
        self.btn_hc.clicked.connect(lambda: self._apply_preset("high_contrast"))

        preset_row = QHBoxLayout()
        preset_row.addWidget(self.btn_light)
        preset_row.addWidget(self.btn_dark)
        preset_row.addWidget(self.btn_hc)
        preset_row.addStretch()
        theme_grid.addLayout(preset_row, 0, 0, 1, 3)

        # Color pickers
        theme_grid.addWidget(QLabel(self.tr("settings_accent_color") + ":"), 1, 0)
        self.accent_picker = QLineEdit("#4a7aaa")
        self.accent_picker.setMaxLength(7)
        self.accent_picker.setFixedWidth(100)
        self.btn_accent_pick = QPushButton("\u25a0")
        self.btn_accent_pick.setFixedSize(28, 28)
        self.btn_accent_pick.clicked.connect(lambda: self._pick_color("accent"))
        pick_row1 = QHBoxLayout()
        pick_row1.addWidget(self.accent_picker)
        pick_row1.addWidget(self.btn_accent_pick)
        pick_row1.addStretch()
        theme_grid.addLayout(pick_row1, 1, 1, 1, 2)

        theme_grid.addWidget(QLabel(self.tr("settings_bg_color") + ":"), 2, 0)
        self.bg_picker = QLineEdit("#f5f5f5")
        self.bg_picker.setMaxLength(7)
        self.bg_picker.setFixedWidth(100)
        self.btn_bg_pick = QPushButton("\u25a0")
        self.btn_bg_pick.setFixedSize(28, 28)
        self.btn_bg_pick.clicked.connect(lambda: self._pick_color("bg"))
        pick_row2 = QHBoxLayout()
        pick_row2.addWidget(self.bg_picker)
        pick_row2.addWidget(self.btn_bg_pick)
        pick_row2.addStretch()
        theme_grid.addLayout(pick_row2, 2, 1, 1, 2)

        theme_grid.addWidget(QLabel(self.tr("settings_text_color") + ":"), 3, 0)
        self.text_picker = QLineEdit("#1a1a1a")
        self.text_picker.setMaxLength(7)
        self.text_picker.setFixedWidth(100)
        self.btn_text_pick = QPushButton("\u25a0")
        self.btn_text_pick.setFixedSize(28, 28)
        self.btn_text_pick.clicked.connect(lambda: self._pick_color("text"))
        pick_row3 = QHBoxLayout()
        pick_row3.addWidget(self.text_picker)
        pick_row3.addWidget(self.btn_text_pick)
        pick_row3.addStretch()
        theme_grid.addLayout(pick_row3, 3, 1, 1, 2)

        theme_grid.addWidget(QLabel(self.tr("settings_tab_color") + ":"), 4, 0)
        self.tab_picker = QLineEdit("#4a7aaa")
        self.tab_picker.setMaxLength(7)
        self.tab_picker.setFixedWidth(100)
        self.btn_tab_pick = QPushButton("\u25a0")
        self.btn_tab_pick.setFixedSize(28, 28)
        self.btn_tab_pick.clicked.connect(lambda: self._pick_color("tab"))
        pick_row4 = QHBoxLayout()
        pick_row4.addWidget(self.tab_picker)
        pick_row4.addWidget(self.btn_tab_pick)
        pick_row4.addStretch()
        theme_grid.addLayout(pick_row4, 4, 1, 1, 2)

        inner_layout.addWidget(theme_group)

        # ===== Font Section =====
        font_group = QGroupBox(self.tr("settings_fonts"))
        font_grid = QGridLayout(font_group)
        font_grid.setSpacing(8)
        font_grid.setContentsMargins(12, 20, 12, 12)

        font_grid.addWidget(QLabel(self.tr("settings_font_size") + ":"), 0, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_grid.addWidget(self.font_size_spin, 0, 1)

        font_grid.addWidget(QLabel(self.tr("settings_font_title") + ":"), 1, 0)
        self.title_size_spin = QSpinBox()
        self.title_size_spin.setRange(10, 32)
        self.title_size_spin.setValue(16)
        font_grid.addWidget(self.title_size_spin, 1, 1)

        font_grid.addWidget(QLabel(self.tr("settings_font_log") + ":"), 2, 0)
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(8, 20)
        self.log_size_spin.setValue(11)
        font_grid.addWidget(self.log_size_spin, 2, 1)

        font_grid.addWidget(QLabel(self.tr("settings_font_family") + ":"), 3, 0)
        self.font_family_combo = QComboBox()
        self.font_family_combo.setView(QListView())
        self.font_family_combo.addItems(["Microsoft YaHei", "SimHei", "Segoe UI", "Arial", "Consolas", "Courier New"])
        self.font_family_combo.setEditable(True)
        font_grid.addWidget(self.font_family_combo, 3, 1)

        font_grid.addWidget(QLabel(self.tr("settings_scale") + ":"), 4, 0)
        self.scale_combo = QComboBox()
        self.scale_combo.setView(QListView())
        self.scale_combo.addItems(["75%", "90%", "100%", "110%", "125%", "150%"])
        self.scale_combo.setCurrentText("100%")
        font_grid.addWidget(self.scale_combo, 4, 1)

        inner_layout.addWidget(font_group)

        # ===== Simulation Presets Section =====
        sim_group = QGroupBox(self.tr("settings_sim_presets"))
        sim_layout = QVBoxLayout(sim_group)
        sim_layout.setSpacing(8)
        sim_layout.setContentsMargins(12, 20, 12, 12)

        preset_sel_row = QHBoxLayout()
        preset_sel_row.addWidget(QLabel(self.tr("settings_load_preset") + ":"))
        self.preset_combo = QComboBox()
        self.preset_combo.setView(QListView())
        self.preset_combo.setMinimumWidth(200)
        self.preset_combo.currentTextChanged.connect(self._on_preset_selected)
        preset_sel_row.addWidget(self.preset_combo)
        self.btn_load_preset = QPushButton(self.tr("settings_load_preset"))
        self.btn_load_preset.setObjectName("btnSecondary")
        self.btn_load_preset.clicked.connect(self._load_preset)
        preset_sel_row.addWidget(self.btn_load_preset)
        self.btn_delete_preset = QPushButton(self.tr("settings_delete_preset"))
        self.btn_delete_preset.setObjectName("btnSecondary")
        self.btn_delete_preset.clicked.connect(self._delete_preset)
        preset_sel_row.addWidget(self.btn_delete_preset)
        preset_sel_row.addStretch()
        sim_layout.addLayout(preset_sel_row)

        save_row = QHBoxLayout()
        save_row.addWidget(QLabel(self.tr("settings_preset_name") + ":"))
        self.preset_name_input = QLineEdit()
        self.preset_name_input.setPlaceholderText("Custom Preset")
        self.preset_name_input.setMinimumWidth(200)
        save_row.addWidget(self.preset_name_input)
        self.btn_save_preset = QPushButton(self.tr("settings_save_preset"))
        self.btn_save_preset.setObjectName("btnPrimary")
        self.btn_save_preset.clicked.connect(self._save_preset)
        save_row.addWidget(self.btn_save_preset)
        save_row.addStretch()
        sim_layout.addLayout(save_row)

        # Defaults button
        defaults_row = QHBoxLayout()
        self.btn_reset_defaults = QPushButton(self.tr("settings_reset_defaults"))
        self.btn_reset_defaults.setObjectName("btnSecondary")
        self.btn_reset_defaults.clicked.connect(self._reset_defaults)
        defaults_row.addWidget(self.btn_reset_defaults)
        defaults_row.addStretch()
        sim_layout.addLayout(defaults_row)

        inner_layout.addWidget(sim_group)

        # ===== Log Section =====
        log_group = QGroupBox(self.tr("settings_log"))
        log_grid = QGridLayout(log_group)
        log_grid.setSpacing(8)
        log_grid.setContentsMargins(12, 20, 12, 12)

        log_grid.addWidget(QLabel(self.tr("settings_log_level") + ":"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.setView(QListView())
        self.log_level_combo.addItems(["ERROR", "INFO", "DEBUG"])
        self.log_level_combo.setCurrentText("INFO")
        log_grid.addWidget(self.log_level_combo, 0, 1)

        self.hide_log_cb = QCheckBox(self.tr("settings_hide_log_guide"))
        log_grid.addWidget(self.hide_log_cb, 1, 0, 1, 2)

        self.auto_save_cb = QCheckBox(self.tr("settings_auto_save"))
        log_grid.addWidget(self.auto_save_cb, 2, 0, 1, 2)

        log_grid.addWidget(QLabel(self.tr("settings_save_path") + ":"), 3, 0)
        path_row = QHBoxLayout()
        self.save_path_input = QLineEdit("exports")
        self.save_path_input.setMinimumWidth(200)
        path_row.addWidget(self.save_path_input)
        self.btn_browse_path = QPushButton("...")
        self.btn_browse_path.setFixedWidth(32)
        self.btn_browse_path.clicked.connect(self._browse_path)
        path_row.addWidget(self.btn_browse_path)
        path_row.addStretch()
        log_grid.addLayout(path_row, 3, 1)

        self.auto_export_cb = QCheckBox(self.tr("settings_auto_export"))
        log_grid.addWidget(self.auto_export_cb, 4, 0, 1, 2)

        inner_layout.addWidget(log_group)

        # ===== Language Section =====
        lang_group = QGroupBox(self.tr("settings_language"))
        lang_layout = QHBoxLayout(lang_group)
        lang_layout.setContentsMargins(12, 20, 12, 12)

        self.lang_en_radio = QRadioButton(self.tr("lang_en"))
        self.lang_zh_radio = QRadioButton(self.tr("lang_zh"))
        self.lang_en_radio.toggled.connect(lambda checked: self._on_lang_change("en") if checked else None)
        self.lang_zh_radio.toggled.connect(lambda checked: self._on_lang_change("zh") if checked else None)

        lang_layout.addWidget(self.lang_en_radio)
        lang_layout.addWidget(self.lang_zh_radio)
        lang_layout.addStretch()

        inner_layout.addWidget(lang_group)

        # ===== Apply Button =====
        self.btn_apply = QPushButton(self.tr("btn_apply"))
        self.btn_apply.setObjectName("btnPrimary")
        self.btn_apply.setMinimumHeight(36)
        self.btn_apply.clicked.connect(self._apply_all)
        inner_layout.addWidget(self.btn_apply)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

    def _pick_color(self, target):
        picker_map = {
            "accent": self.accent_picker,
            "bg": self.bg_picker,
            "text": self.text_picker,
            "tab": self.tab_picker,
        }
        edit = picker_map.get(target)
        if not edit:
            return
        color = QColorDialog.getColor(QColor(edit.text()) if QColor(edit.text()).isValid() else Qt.white, self, "Pick Color")
        if color.isValid():
            edit.setText(color.name())

    def _apply_preset(self, preset_name):
        self._cfg.apply_preset_theme(preset_name)
        colors = self._cfg.get_theme_colors()
        # Update pickers
        self.accent_picker.setText(colors.get("accent", "#4a7aaa"))
        self.bg_picker.setText(colors.get("bg_primary", "#f5f5f5"))
        self.text_picker.setText(colors.get("text_primary", "#1a1a1a"))
        self.tab_picker.setText(colors.get("tab_selected", "#4a7aaa"))
        self.themeChanged.emit(colors)
        self._cfg.save()
        self._i18n = get_i18n()
        self._retranslate()

    def _on_lang_change(self, lang):
        self._cfg.set("language", lang)
        self._cfg.save()
        reload_i18n()
        self._i18n = get_i18n()
        self.languageChanged.emit(lang)
        self._retranslate()

    def _retranslate(self):
        """Update all static labels with current language"""
        self.btn_light.setText(self.tr("settings_preset_light"))
        self.btn_dark.setText(self.tr("settings_preset_dark"))
        self.btn_hc.setText(self.tr("settings_preset_hc"))
        self.btn_apply.setText(self.tr("btn_apply"))
        self.btn_load_preset.setText(self.tr("settings_load_preset"))
        self.btn_delete_preset.setText(self.tr("settings_delete_preset"))
        self.btn_save_preset.setText(self.tr("settings_save_preset"))
        self.btn_reset_defaults.setText(self.tr("settings_reset_defaults"))

        # Rebuild guides - simple approach: iterate child widgets
        self._apply_retranslate_to_group_boxes()

    def _apply_retranslate_to_group_boxes(self):
        """Update GroupBox titles - find them by index"""
        # Find all group boxes in the scroll content and update their titles
        groups = self.findChildren(QGroupBox)
        titles = [
            "settings_theme", "settings_fonts", "settings_sim_presets",
            "settings_log", "settings_language"
        ]
        for gb, key in zip(groups, titles):
            gb.setTitle(self.tr(key))

    def _on_preset_selected(self, name):
        pass  # preview if needed

    def _save_preset(self):
        name = self.preset_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a preset name.")
            return
        params = self._gather_sim_params()
        self._cfg.save_preset(name, params)
        self._cfg.save()
        self._refresh_preset_list()
        self.preset_combo.setCurrentText(name)
        self._i18n = get_i18n()
        self.log_message(f"Preset \"{name}\" saved.")

    def _load_preset(self):
        name = self.preset_combo.currentText()
        if not name:
            return
        params = self._cfg.get_preset(name)
        if params:
            self.presetLoaded.emit(params)
            self._i18n = get_i18n()
            self.log_message(f"Preset \"{name}\" loaded.")

    def _delete_preset(self):
        name = self.preset_combo.currentText()
        if not name:
            return
        self._cfg.delete_preset(name)
        self._cfg.save()
        self._refresh_preset_list()
        self._i18n = get_i18n()
        self.log_message(f"Preset \"{name}\" deleted.")

    def _reset_defaults(self):
        self._cfg.reset_to_defaults()
        self._cfg.save()
        self._load_config()
        self._apply_all()
        self._i18n = get_i18n()
        self.log_message("All settings reset to defaults.")

    def _browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Path")
        if folder:
            self.save_path_input.setText(folder)

    def _gather_sim_params(self):
        return {
            "snr_range_start": self._cfg.get("simulation", "snr_range_start"),
            "snr_range_end": self._cfg.get("simulation", "snr_range_end"),
            "snr_range_step": self._cfg.get("simulation", "snr_range_step"),
            "modulation": self._cfg.get("simulation", "modulation"),
            "fft_size": self._cfg.get("simulation", "fft_size"),
            "cp_len": self._cfg.get("simulation", "cp_len"),
            "n_data_carriers": self._cfg.get("simulation", "n_data_carriers"),
        }

    def _load_config(self):
        colors = self._cfg.get_theme_colors()
        self.accent_picker.setText(colors.get("accent", "#4a7aaa"))
        self.bg_picker.setText(colors.get("bg_primary", "#f5f5f5"))
        self.text_picker.setText(colors.get("text_primary", "#1a1a1a"))
        self.tab_picker.setText(colors.get("tab_selected", "#4a7aaa"))

        fonts = self._cfg.get("theme", "fonts") or {}
        self.font_size_spin.setValue(fonts.get("size_base", 12))
        self.title_size_spin.setValue(fonts.get("size_title", 16))
        self.log_size_spin.setValue(fonts.get("size_log", 11))
        self.font_family_combo.setCurrentText(fonts.get("family", "Microsoft YaHei"))
        scale_val = fonts.get("scale", 1.0)
        self.scale_combo.setCurrentText(f"{int(scale_val * 100)}%")

        log_cfg = self._cfg.get("log") or {}
        self.log_level_combo.setCurrentText(log_cfg.get("level", "INFO"))
        self.hide_log_cb.setChecked(log_cfg.get("show_on_guide", False))
        self.auto_save_cb.setChecked(log_cfg.get("auto_save", False))
        self.save_path_input.setText(log_cfg.get("save_path", "exports"))
        self.auto_export_cb.setChecked(log_cfg.get("auto_export_results", False))

        lang = self._cfg.get("language", "en")
        if lang == "zh":
            self.lang_zh_radio.setChecked(True)
        else:
            self.lang_en_radio.setChecked(True)

        self._refresh_preset_list()

    def _refresh_preset_list(self):
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItems(self._cfg.get_preset_names())
        self.preset_combo.blockSignals(False)

    def _apply_all(self):
        """Apply all settings from the UI to config and emit signals"""
        # Colors
        colors = self._cfg.get("theme", "colors")
        colors["accent"] = self.accent_picker.text()
        colors["bg_primary"] = self.bg_picker.text()
        colors["text_primary"] = self.text_picker.text()
        colors["tab_selected"] = self.tab_picker.text()
        self._cfg.set("theme", "preset", "custom")

        # Fonts
        fonts = self._cfg.get("theme", "fonts")
        fonts["size_base"] = self.font_size_spin.value()
        fonts["size_title"] = self.title_size_spin.value()
        fonts["size_log"] = self.log_size_spin.value()
        fonts["family"] = self.font_family_combo.currentText()
        scale_text = self.scale_combo.currentText().replace("%", "")
        fonts["scale"] = int(scale_text) / 100.0

        # Log
        self._cfg.set("log", "level", self.log_level_combo.currentText())
        self._cfg.set("log", "show_on_guide", self.hide_log_cb.isChecked())
        self._cfg.set("log", "auto_save", self.auto_save_cb.isChecked())
        self._cfg.set("log", "save_path", self.save_path_input.text())
        self._cfg.set("log", "auto_export_results", self.auto_export_cb.isChecked())

        self._cfg.save()

        # Emit signals
        self.themeChanged.emit(colors)
        self.fontChanged.emit(fonts)
        self.logSettingsChanged.emit(self._cfg.get("log"))

        self.log_message("Configuration applied and saved.")

    def log_message(self, msg):
        """Forward message to parent's log if available"""
        parent = self.parent()
        while parent and not hasattr(parent, "log_message"):
            parent = parent.parent()
        if parent and hasattr(parent, "log_message"):
            parent.log_message(msg)

    def retranslate_all(self):
        """Called from main_window when language changes"""
        self._i18n = get_i18n()
        self._retranslate()
