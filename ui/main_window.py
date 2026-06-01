# -*- coding: utf-8 -*-
"主窗口 - VLC智能解调系统 (优化版)"

import sys
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

from .styles import MONO_STYLE, get_theme_stylesheet
from .settings_tab import SettingsTab
from core.vlc_simulator import VLCSystemSimulator
from core.ai_demodulator import AIDemodulator
from core.signal_processing import SignalGenerator
from core.config_manager import get_config
from core.i18n import get_i18n, reload_i18n


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4.5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#ffffff")
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumHeight(200)

    def style_ax(self, ax):
        colors = get_config().get_theme_colors()
        ax.set_facecolor(colors.get("bg_primary", "#fafafa"))
        ax.tick_params(colors=colors.get("text_muted", "#888888"), labelsize=8)
        ax.grid(True, alpha=0.25, color=colors.get("border", "#dddddd"), linestyle="-", linewidth=0.5)
        for spine in ax.spines.values():
            spine.set_color(colors.get("border", "#dddddd"))
            spine.set_linewidth(0.5)

    def apply_theme(self):
        colors = get_config().get_theme_colors()
        bg = colors.get("bg_primary", "#fafafa")
        border = colors.get("border", "#dddddd")
        muted = colors.get("text_muted", "#888888")
        self.fig.set_facecolor(colors.get("bg_secondary", "#ffffff"))
        for ax in self.fig.axes:
            ax.set_facecolor(bg)
            ax.tick_params(colors=muted, labelsize=8)
            ax.grid(True, alpha=0.25, color=border)
            for spine in ax.spines.values():
                spine.set_color(border)
        self.draw()


def build_all_workflows_tab():
    """Build a single comprehensive Operation Guide tab with all 8 workflow steps."""
    i18n = get_i18n()
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(16)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    inner = QWidget()
    inner.setStyleSheet("background: transparent;")
    inner_layout = QVBoxLayout(inner)
    inner_layout.setContentsMargins(0, 0, 0, 0)
    inner_layout.setSpacing(24)

    # Header
    header = QLabel(i18n.tr("guide_header"))
    header.setStyleSheet("font-size: 22px; font-weight: 700; color: #1a1a1a; padding-bottom: 8px; background: transparent;")
    inner_layout.addWidget(header)

    subtitle = QLabel(i18n.tr("guide_subtitle"))
    subtitle.setWordWrap(True)
    subtitle.setStyleSheet("font-size: 16px; color: #666; line-height: 1.8; background: transparent;")
    inner_layout.addWidget(subtitle)

    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet("background-color: #d0d0d0; max-height: 1px;")
    inner_layout.addWidget(sep)

    steps = [
        ("01", "DATA", "step_data", "step_data_desc"),
        ("02", "OFDM", "step_ofdm", "step_ofdm_desc"),
        ("03", "LED", "step_led", "step_led_desc"),
        ("04", "CH", "step_ch", "step_ch_desc"),
        ("05", "PD", "step_pd", "step_pd_desc"),
        ("06", "ODEM", "step_demod", "step_demod_desc"),
        ("07", "AI", "step_ai", "step_ai_desc"),
        ("08", "OUT", "step_ber", "step_ber_desc"),
    ]

    for num, key, title_key, desc_key in steps:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 0px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(8)

        hdr = QHBoxLayout()
        num_label = QLabel(num)
        num_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #4a7aaa; background: transparent;")
        hdr.addWidget(num_label)
        hdr.addSpacing(8)

        key_label = QLabel(key)
        key_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #222; background: transparent;")
        hdr.addWidget(key_label)
        hdr.addSpacing(8)

        title_label = QLabel(i18n.tr(title_key))
        title_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #555; background: transparent;")
        hdr.addWidget(title_label)
        hdr.addStretch()
        card_layout.addLayout(hdr)

        desc_label = QLabel(i18n.tr(desc_key))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 14px; color: #555; line-height: 1.8; background: transparent; padding-left: 2px;")
        card_layout.addWidget(desc_label)

        inner_layout.addWidget(card)

    inner_layout.addStretch()
    scroll.setWidget(inner)
    layout.addWidget(scroll)
    return w


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cfg = get_config()
        self._i18n = get_i18n()
        self.simulator = VLCSystemSimulator(modulation='QPSK')
        self.ai_demod = AIDemodulator(model_type='MLP', modulation='QPSK')
        self.current_result = None
        self.trained = False
        self.init_ui()
        self._apply_saved_theme()
        self.log_message(self._i18n.tr("msg_initialized"))

    def tr(self, key):
        return self._i18n.tr(key)

    def _update_log_visibility(self):
        idx = self.tabs.currentIndex()
        # Hide log on OPERATION GUIDE (0) and SETTINGS (5)
        if idx == 0 or idx == 5:
            self.log_bar.hide()
        else:
            self.log_bar.show()

    def _apply_language(self):
        """Refresh ALL UI text to match current language setting"""
        i18n = self._i18n
        # Window title
        self.setWindowTitle(i18n.tr("window_title"))
        # Title bar
        self.title_label.setText(i18n.tr("main_title"))
        self.sub_label.setText(i18n.tr("main_subtitle"))
        self.status_indicator.setText(i18n.tr("status_standby"))
        # Tab labels
        tab_labels = ["tab_guide", "tab_waveform", "tab_constellation", "tab_eye", "tab_ber", "tab_settings"]
        for i, key in enumerate(tab_labels):
            text = i18n.tr(key).strip()
            if key in ("tab_guide", "tab_settings"):
                text = "  " + text + "  "
            self.tabs.setTabText(i, text)
        # Rebuild OPERATION GUIDE tab (index 0) with new language
        guide_text = '  ' + i18n.tr('tab_guide').strip() + '  '
        new_guide = build_all_workflows_tab()
        self.tabs.removeTab(0)
        self.tabs.insertTab(0, new_guide, guide_text)
        # Left panel: rebuild group box titles
        groups = self.findChildren(QGroupBox)
        group_keys = ["group_system_control", "group_system_params", "group_results"]
        for gb, key in zip(groups[:3], group_keys):
            gb.setTitle(i18n.tr(key))
        self.btn_run.setText(i18n.tr("btn_run"))
        self.btn_train.setText(i18n.tr("btn_train"))
        self.btn_ber.setText(i18n.tr("btn_ber_sweep"))
        self.btn_clear.setText(i18n.tr("btn_clear_log"))
        self.btn_save.setText(i18n.tr("btn_save"))
        self.btn_results.setText(i18n.tr("btn_results"))
        # Log label
        for child in self.log_bar.findChildren(QLabel):
            if child.objectName() == "" and child.text() in ("LOG", "日志", self._i18n.tr("log_label")):
                child.setText(i18n.tr("log_label"))
                break
        # Settings tab
        self.settings_tab.retranslate_all()

    def init_ui(self):
        self.setWindowTitle("VLC Intelligent Demodulation System  v2.0")
        self.setGeometry(60, 30, 1480, 860)
        self.setStyleSheet(MONO_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # --- Title Bar ---
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        tl = QHBoxLayout(title_bar)
        tl.setContentsMargins(16, 4, 16, 4)

        # Accent bar: colored strip on the left
        accent_bar = QFrame()
        accent_bar.setFixedSize(4, 28)
        accent_bar.setStyleSheet("background-color: #4a7aaa; border: none; border-radius: 2px;")
        accent_bar.setObjectName("accentBar")
        tl.addWidget(accent_bar)
        tl.addSpacing(12)

        # Main title
        self.title_label = QLabel("VLC INTELLIGENT DEMODULATION SYSTEM")
        self.title_label.setObjectName("mainTitle")
        tl.addWidget(self.title_label)
        tl.addSpacing(16)

        sep = QLabel("|")
        sep.setStyleSheet("color: #cccccc; font-size: 16px; background: transparent;")
        tl.addWidget(sep)
        tl.addSpacing(12)

        self.sub_label = QLabel("Visible Light Communication  ·  Signal Intelligence Platform")
        self.sub_label.setObjectName("mainSubtitle")
        tl.addWidget(self.sub_label)
        tl.addStretch()

        self.status_indicator = QLabel("●  STANDBY")
        self.status_indicator.setStyleSheet("color: #999999; font-size: 10px; font-weight: 600; letter-spacing: 1px; background: transparent;")
        tl.addWidget(self.status_indicator)

        root.addWidget(title_bar)

        # --- Body ---
        body = QWidget()
        body.setStyleSheet("background-color: #f5f5f5;")
        bl = QHBoxLayout(body)
        bl.setSpacing(8)
        bl.setContentsMargins(12, 8, 12, 8)

        # ===== LEFT PANEL (unchanged) =====
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(270)
        left_panel.setMinimumWidth(250)
        ll = QVBoxLayout(left_panel)
        ll.setSpacing(6)
        ll.setContentsMargins(10, 8, 10, 8)

        cg = QGroupBox("System Control")
        cg.setStyleSheet("QGroupBox { font-size: 11px; } QGroupBox::title { font-size: 10px; }")
        cg_grid = QGridLayout(cg)
        cg_grid.setSpacing(8)
        cg_grid.setContentsMargins(8, 14, 8, 6)

        lbl_snr = QLabel("SNR (dB)"); lbl_snr.setStyleSheet("font-size: 12px; font-weight: 600; color: #333;")
        cg_grid.addWidget(lbl_snr, 0, 0)
        self.snr_slider = QSlider(Qt.Horizontal)
        self.snr_slider.setRange(0, 30)
        self.snr_slider.setValue(20)
        cg_grid.addWidget(self.snr_slider, 0, 1)
        self.snr_value = QLabel("20")
        self.snr_value.setStyleSheet("font-size: 14px; font-weight: 700; color: #4a7aaa; min-width: 30px;")
        cg_grid.addWidget(self.snr_value, 0, 2)
        self.snr_slider.valueChanged.connect(lambda v: self.snr_value.setText(str(v)))

        lbl_bits = QLabel("Data Length"); lbl_bits.setStyleSheet("font-size: 12px; font-weight: 600; color: #333;")
        cg_grid.addWidget(lbl_bits, 1, 0)
        self.bits_combo = QComboBox()
        self.bits_combo.addItems(["512", "1024", "2048", "4096"])
        self.bits_combo.setCurrentText("1024")
        cg_grid.addWidget(self.bits_combo, 1, 1, 1, 2)
        lbl_mod = QLabel("Modulation"); lbl_mod.setStyleSheet("font-size: 12px; font-weight: 600; color: #333;")
        cg_grid.addWidget(lbl_mod, 4, 0)
        self.mod_combo = QComboBox()
        self.mod_combo.addItems(['BPSK', 'QPSK', '16-QAM', '64-QAM'])
        self.mod_combo.setCurrentText("QPSK")
        self.mod_combo.currentTextChanged.connect(self._on_modulation_changed)
        cg_grid.addWidget(self.mod_combo, 4, 1, 1, 2)

        lbl_ai = QLabel("AI Model"); lbl_ai.setStyleSheet("font-size: 12px; font-weight: 600; color: #333;")
        cg_grid.addWidget(lbl_ai, 5, 0)
        self.ai_combo = QComboBox()
        self.ai_combo.addItems(['MLP', 'CNN', 'LSTM'])
        self.ai_combo.setCurrentText("MLP")
        self.ai_combo.currentTextChanged.connect(self._on_ai_model_changed)
        cg_grid.addWidget(self.ai_combo, 5, 1, 1, 2)


        br1 = QHBoxLayout()
        self.btn_run = QPushButton("\u25b6  Run Simulation")
        self.btn_run.setObjectName("btnPrimary")
        self.btn_run.clicked.connect(self.run_simulation)
        br1.addWidget(self.btn_run)
        self.btn_train = QPushButton("Train AI")
        self.btn_train.setObjectName("btnSecondary")
        self.btn_train.clicked.connect(self.train_ai_model)
        br1.addWidget(self.btn_train)
        cg_grid.addLayout(br1, 6, 0, 1, 3)

        br2 = QHBoxLayout()
        self.btn_ber = QPushButton("BER Sweep")
        self.btn_ber.setObjectName("btnSecondary")
        self.btn_ber.clicked.connect(self.run_ber_sweep)
        br2.addWidget(self.btn_ber)
        self.btn_clear = QPushButton("Clear Log")
        self.btn_clear.setObjectName("btnSecondary")
        self.btn_clear.clicked.connect(lambda: self.log_output.clear())
        br2.addWidget(self.btn_clear)
        cg_grid.addLayout(br2, 7, 0, 1, 3)

        ll.addWidget(cg)

        ig = QGroupBox("System Parameters")
        ig.setStyleSheet("QGroupBox { font-size: 11px; } QGroupBox::title { font-size: 10px; }")
        ig_grid = QGridLayout(ig)
        ig_grid.setSpacing(5)
        ig_grid.setContentsMargins(8, 14, 8, 6)

        params = [
            ("Modulation", "OFDM-QPSK"),
            ("FFT Size", "64"),
            ("Cyclic Prefix", "16 (25%)"),
            ("Data Carriers", "48"),
            ("LED", "Blue 450nm"),
            ("Detector", "PIN Photodiode"),
            ("Channel", "LOS + AWGN"),
        ]
        for i, (k, v) in enumerate(params):
            lk = QLabel(k); lk.setStyleSheet("font-size: 12px; color: #555;")
            ig_grid.addWidget(lk, i, 0)
            lv = QLabel(v); lv.setStyleSheet("font-size: 12px; font-weight: 600; color: #333;")
            ig_grid.addWidget(lv, i, 1)

        ll.addWidget(ig)

        rg = QGroupBox("Results")
        rg.setStyleSheet("QGroupBox { font-size: 11px; } QGroupBox::title { font-size: 10px; }")
        rg_grid = QGridLayout(rg)
        rg_grid.setSpacing(5)
        rg_grid.setContentsMargins(8, 14, 8, 6)

        self.result_labels = {}
        stats = [
            ("TX Bits", "tx_bits"),
            ("Errors", "err_bits"),
            ("BER", "ber"),
            ("SNR", "snr_db"),
            ("Confidence", "confidence"),
            ("Latency", "proc_time"),
        ]
        for i, (label, key) in enumerate(stats):
            lk = QLabel(label); lk.setStyleSheet("font-size: 12px; color: #555;")
            rg_grid.addWidget(lk, i, 0)
            lv = QLabel("--")
            lv.setStyleSheet("font-size: 13px; font-weight: 700; color: #1a1a1a;")
            rg_grid.addWidget(lv, i, 1)
            self.result_labels[key] = lv

        # Save & Results buttons
        br_res = QHBoxLayout()
        self.btn_save = QPushButton("Save Result")
        self.btn_save.setObjectName("btnSecondary")
        self.btn_save.clicked.connect(self._save_current_result)
        br_res.addWidget(self.btn_save)
        self.btn_results = QPushButton("Results History")
        self.btn_results.setObjectName("btnSecondary")
        self.btn_results.clicked.connect(self._show_results_history)
        br_res.addWidget(self.btn_results)
        rg_grid.addLayout(br_res, 6, 0, 1, 2)


        ll.addWidget(rg)
        ll.addStretch()
        bl.addWidget(left_panel)

        # ===== CENTRE =====
        centre = QWidget()
        centre.setStyleSheet("background-color: #f5f5f5;")
        cl = QVBoxLayout(centre)
        cl.setSpacing(6)
        cl.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        # Tab styling is handled in MONO_STYLE (styles.py)

        # Operation Guide tab (collapsed from 8 individual workflow tabs)
        self.tabs.addTab(build_all_workflows_tab(), "  OPERATION GUIDE  ")

        # Analysis tabs
        wt = QWidget()
        wl = QVBoxLayout(wt); wl.setContentsMargins(6, 6, 6, 6)
        self.fig_wave = MplCanvas(self, width=7, height=4.5)
        self.wave_ax = self.fig_wave.fig.add_subplot(111)
        self.fig_wave.style_ax(self.wave_ax)
        self.wave_ax.set_title("Signal Waveform", fontsize=10, fontweight="600", color="#444")
        self.wave_ax.set_xlabel("Sample", fontsize=9, color="#888")
        self.wave_ax.set_ylabel("Amplitude", fontsize=9, color="#888")
        wl.addWidget(self.fig_wave)
        self.tabs.addTab(wt, "WAVEFORM")

        ct = QWidget()
        const_layout = QVBoxLayout(ct); const_layout.setContentsMargins(6, 6, 6, 6)
        self.fig_const = MplCanvas(self, width=7, height=4.5)
        self.const_ax = self.fig_const.fig.add_subplot(111)
        self.fig_const.style_ax(self.const_ax)
        self.const_ax.set_title("Constellation Diagram", fontsize=10, fontweight="600", color="#444")
        self.const_ax.set_xlabel("In-Phase", fontsize=9, color="#888")
        self.const_ax.set_ylabel("Quadrature", fontsize=9, color="#888")
        self.const_ax.set_aspect("equal")
        const_layout.addWidget(self.fig_const)
        self.tabs.addTab(ct, "CONSTELLATION")

        et = QWidget()
        eye_layout = QVBoxLayout(et); eye_layout.setContentsMargins(6, 6, 6, 6)
        self.fig_eye = MplCanvas(self, width=7, height=4.5)
        self.eye_ax = self.fig_eye.fig.add_subplot(111)
        self.fig_eye.style_ax(self.eye_ax)
        self.eye_ax.set_title("Eye Diagram", fontsize=10, fontweight="600", color="#444")
        eye_layout.addWidget(self.fig_eye)
        self.tabs.addTab(et, "EYE DIAGRAM")

        bt = QWidget()
        ber_layout = QVBoxLayout(bt); ber_layout.setContentsMargins(6, 6, 6, 6)
        self.fig_ber = MplCanvas(self, width=7, height=4.5)
        self.ber_ax = self.fig_ber.fig.add_subplot(111)
        self.fig_ber.style_ax(self.ber_ax)
        self.ber_ax.set_title("BER Performance", fontsize=10, fontweight="600", color="#444")
        self.ber_ax.set_xlabel("SNR (dB)", fontsize=9, color="#888")
        self.ber_ax.set_ylabel("Bit Error Rate", fontsize=9, color="#888")
        ber_layout.addWidget(self.fig_ber)
        self.tabs.addTab(bt, self._i18n.tr("tab_ber"))

        # SETTINGS
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "  " + self._i18n.tr("tab_settings").strip() + "  ")

        # Connect settings signals
        self.settings_tab.themeChanged.connect(self._on_theme_changed)
        self.settings_tab.fontChanged.connect(self._on_font_changed)
        self.settings_tab.languageChanged.connect(self._on_language_changed)
        self.settings_tab.presetLoaded.connect(self._on_preset_loaded)
        self.settings_tab.logSettingsChanged.connect(self._on_log_settings_changed)

        # Log visibility follows tab switches
        self.tabs.currentChanged.connect(self._update_log_visibility)

        cl.addWidget(self.tabs, 4)

        # --- Log Bar ---
        self.log_bar = QWidget()
        self.log_bar.setObjectName("logBar")
        self.log_bar.setStyleSheet("background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px;")
        self.log_bar.setMinimumHeight(100)
        log_layout = QHBoxLayout(self.log_bar)
        log_layout.setContentsMargins(8, 6, 8, 6)
        log_layout.setSpacing(8)

        log_tag = QLabel("LOG")
        log_tag.setStyleSheet("font-size: 10px; font-weight: 700; color: #999; letter-spacing: 2px; background: transparent;")
        log_tag.setFixedWidth(30)
        log_tag.setAlignment(Qt.AlignTop)
        log_layout.addWidget(log_tag)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.log_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        log_layout.addWidget(self.log_output)

        cl.addWidget(self.log_bar, 1)
        bl.addWidget(centre, 1)
        root.addWidget(body, 1)

        # Force initial log visibility state
        self._update_log_visibility()
        # Apply saved language to all UI
        self._apply_language()

    # --- Theme / Settings Methods ---

    def _on_theme_changed(self, colors):
        stylesheet = get_theme_stylesheet(colors)
        self.setStyleSheet(stylesheet)
        accent = self.findChild(QFrame, "accentBar")
        if accent:
            accent.setStyleSheet("background-color: " + colors.get("accent", "#4a7aaa") + "; border: none; border-radius: 2px;")
        for canvas in [self.fig_wave, self.fig_const, self.fig_eye, self.fig_ber]:
            if hasattr(canvas, "apply_theme"):
                canvas.apply_theme()
        self.log_message(self._i18n.tr("msg_theme_applied").format(theme=colors.get("preset", "custom")))

    def _apply_saved_theme(self):
        colors = self._cfg.get_theme_colors()
        stylesheet = get_theme_stylesheet(colors)
        self.setStyleSheet(stylesheet)
        for canvas in [self.fig_wave, self.fig_const, self.fig_eye, self.fig_ber]:
            if hasattr(canvas, "apply_theme"):
                canvas.apply_theme()

    def _on_font_changed(self, fonts):
        app = QApplication.instance()
        if app:
            family = fonts.get("family", "Microsoft YaHei")
            size = fonts.get("size_base", 12)
            app.setFont(QFont(family, size))
        self.log_message("Font updated: " + fonts.get("family", "?") + ", " + str(fonts.get("size_base", 12)) + "px")

    def _on_language_changed(self, lang):
        self._i18n = get_i18n()
        self._apply_language()
        self.log_message("Language changed to " + lang + ".")

    def _rebuild_left_panel(self):
        groups = self.findChildren(QGroupBox)
        keys = ["group_system_control", "group_system_params", "group_results"]
        for gb, key in zip(groups[:3], keys):
            gb.setTitle(self._i18n.tr(key))
        self.btn_run.setText(self._i18n.tr("btn_run"))
        self.btn_train.setText(self._i18n.tr("btn_train"))
        self.btn_ber.setText(self._i18n.tr("btn_ber_sweep"))
        self.btn_clear.setText(self._i18n.tr("btn_clear_log"))
        self.btn_save.setText(self._i18n.tr("btn_save"))
        self.btn_results.setText(self._i18n.tr("btn_results"))

    def _on_preset_loaded(self, params):
        if "snr_range_end" in params:
            self.snr_slider.setRange(params.get("snr_range_start", 0), params.get("snr_range_end", 30))
            self.snr_slider.setValue(params.get("snr_range_end", 30) // 2)
        self.log_message(self._i18n.tr("msg_preset_loaded").format(name=""))

    def _on_log_settings_changed(self, settings):
        self._update_log_visibility()

    def _show_results_history(self):
        from core.results_manager import list_results, load_result, export_result_text, delete_result
        entries = list_results()
        if not entries:
            QMessageBox.information(self, "Saved Results", "No saved results yet.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Saved Results")
        dialog.resize(700, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Modulation", "AI Model", "SNR", "BER"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for row, entry in enumerate(entries):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(entry.get("name", "")))
            table.setItem(row, 1, QTableWidgetItem(entry.get("modulation", "")))
            table.setItem(row, 2, QTableWidgetItem(entry.get("ai_model", "")))
            table.setItem(row, 3, QTableWidgetItem(str(entry.get("snr_db", "")) + " dB"))
            ber = entry.get("ber", 0)
            table.setItem(row, 4, QTableWidgetItem(f"{ber:.6e}" if ber > 0 else "0"))
        layout.addWidget(table)

        def on_load():
            row = table.currentRow()
            if row < 0: return
            self.log_message("Loaded: " + entries[row]["name"])
            dialog.accept()

        def on_export():
            row = table.currentRow()
            if row < 0: return
            from PyQt5.QtWidgets import QFileDialog
            fpath, _ = QFileDialog.getSaveFileName(dialog, "Export", entries[row]["name"] + ".txt", "Text (*.txt)")
            if fpath:
                export_result_text(entries[row]["path"], fpath)
                self.log_message("Exported to: " + fpath)

        def on_delete():
            row = table.currentRow()
            if row < 0: return
            delete_result(entries[row]["path"])
            table.removeRow(row)
            self.log_message("Deleted: " + entries[row]["name"])

        btn_row = QHBoxLayout()
        btn_load = QPushButton("Load")
        btn_load.clicked.connect(on_load)
        btn_export = QPushButton("Export")
        btn_export.clicked.connect(on_export)
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(on_delete)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.reject)
        btn_row.addWidget(btn_load)
        btn_row.addWidget(btn_export)
        btn_row.addWidget(btn_delete)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
        dialog.exec_()

    def _on_modulation_changed(self, mod):
        self.simulator.set_modulation(mod)
        self.ai_demod.modulation = mod
        self.ai_demod.constellation = self.ai_demod._get_constellation()
        if self.ai_demod.trained:
            self.ai_demod.trained = False
            self.log_message("AI model reset due to modulation change. Please retrain.")
        self.log_message("Modulation changed to " + mod)

    def _on_ai_model_changed(self, model_type):
        self.ai_demod.model_type = model_type
        if self.ai_demod.trained:
            self.ai_demod.trained = False
            self.log_message("AI model reset due to model type change. Please retrain.")
        self.log_message("AI model changed to " + model_type)

    def _save_current_result(self):
        result = self.current_result
        if result is None:
            self.log_message("No simulation result to save. Run simulation first.")
            return
        from core.results_manager import save_result
        result["modulation"] = self.mod_combo.currentText()
        result["ai_model"] = self.ai_combo.currentText()
        fpath, label = save_result(result)
        self.log_message("Result saved: " + label)

    def run_simulation(self):
        try:
            self.status_indicator.setText("●  RUNNING")
            colors = self._cfg.get_theme_colors()
            self.status_indicator.setStyleSheet("color: " + colors.get("accent", "#4a7aaa") + "; font-size: 10px; font-weight: 600; background: transparent;")
            self.log_message("Starting VLC simulation...")
            QApplication.processEvents()

            n_bits = int(self.bits_combo.currentText())
            snr = self.snr_slider.value()
            import time
            start = time.time()
            result = self.simulator.run_simulation(n_bits=n_bits, snr_db=snr)
            self.current_result = result
            elapsed = (time.time() - start) * 1000

            tx_syms = result["tx_symbols"]
            if len(tx_syms) > 0:
                predictions, confidence = self.ai_demod.demodulate(tx_syms)
                conf = float(np.mean(confidence)) if len(confidence) > 0 else 0
            else:
                conf = 0

            n_err = int(np.sum(np.array(result["tx_bits"][:len(result["rx_bits"])]) != np.array(result["rx_bits"][:len(result["rx_bits"])])))
            self.result_labels["tx_bits"].setText(str(n_bits))
            self.result_labels["err_bits"].setText(str(n_err))
            self.result_labels["ber"].setText(f'{result["ber"]:.6f}')
            self.result_labels["snr_db"].setText(f"{snr} dB")
            self.result_labels["confidence"].setText(f"{conf:.2%}")
            self.result_labels["proc_time"].setText(f"{elapsed:.1f} ms")
            self._update_plots(result)

            self.log_message(f"Done | bits={n_bits} | BER={result['ber']:.6f} | SNR={snr}dB | {elapsed:.1f}ms")
            self.status_indicator.setText("●  READY")
            colors = self._cfg.get_theme_colors()
            self.status_indicator.setStyleSheet("color: " + colors.get("text_muted", "#888888") + "; font-size: 10px; font-weight: 600; background: transparent;")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            self.status_indicator.setText("●  ERROR")
            colors = self._cfg.get_theme_colors()
            self.status_indicator.setStyleSheet("color: " + colors.get("error", "#c05555") + "; font-size: 10px; font-weight: 600; background: transparent;")

    def train_ai_model(self):
        try:
            self.log_message("Training AI demodulation model...")
            QApplication.processEvents()
            constellation = SignalGenerator.qpsk_constellation()
            n_syms = 5000
            bits = SignalGenerator.generate_random_bits(n_syms * 2)
            symbols = SignalGenerator.bits_to_symbols(bits, constellation)
            labels = np.zeros(n_syms, dtype=int)
            for i in range(n_syms):
                labels[i] = (bits[2*i] << 1) | bits[2*i+1]
            noise = 0.3 * (np.random.randn(n_syms) + 1j * np.random.randn(n_syms))
            self.ai_demod.train(symbols + noise, labels)
            self.trained = True
            self.log_message("AI model trained (5000 samples)")
            self.result_labels["confidence"].setText("TRAINED")
        except Exception as e:
            self.log_message(f"Training error: {str(e)}")

    def run_ber_sweep(self):
        try:
            self.log_message("Running BER sweep...")
            QApplication.processEvents()
            results = self.simulator.run_ber_sweep()
            snrs = [r["snr_db"] for r in results]; bers = [r["ber"] for r in results]

            self.ber_ax.clear()
            self.ber_ax.set_facecolor("#fafafa")
            self.ber_ax.semilogy(snrs, bers, "o-", color="#4a7aaa", linewidth=1.8, markersize=5, label="Measured BER")
            self.ber_ax.set_title("BER Performance", fontsize=10, fontweight="600", color="#444")
            self.ber_ax.set_xlabel("SNR (dB)", fontsize=9, color="#888")
            self.ber_ax.set_ylabel("Bit Error Rate", fontsize=9, color="#888")
            self.ber_ax.tick_params(colors="#888888", labelsize=8)
            self.ber_ax.grid(True, alpha=0.25, color="#dddddd")
            for spine in self.ber_ax.spines.values():
                spine.set_color("#dddddd")
            self.ber_ax.legend(facecolor="#ffffff", edgecolor="#dddddd", labelcolor="#444", fontsize=8)
            self.fig_ber.draw()

            self.log_message(f"BER sweep complete | range={snrs[0]}-{snrs[-1]}dB")
            self.tabs.setCurrentIndex(11)
        except Exception as e:
            self.log_message(f"BER sweep error: {str(e)}")

    def _update_plots(self, result):
        try:
            signal = result["received_signal"]
            tx_syms = result["tx_symbols"]; rx_syms = result["rx_symbols"]
            constellation = result["constellation"]
            n_samples = min(200, len(signal))
            time_axis = np.arange(n_samples)

            self.wave_ax.clear(); self.wave_ax.set_facecolor("#fafafa")
            orig = result["ofdm_signal"][:n_samples]
            self.wave_ax.plot(time_axis, np.real(orig), color="#555555", linewidth=1, alpha=0.8, label="TX")
            received = signal[:n_samples]
            self.wave_ax.plot(time_axis[:len(received)], np.real(received), color="#4a7aaa", linewidth=0.9, alpha=0.9, label="RX")
            self.wave_ax.set_title("Signal Waveform", fontsize=10, fontweight="600", color="#444")
            self.wave_ax.set_xlabel("Sample", fontsize=9, color="#888")
            self.wave_ax.set_ylabel("Amplitude", fontsize=9, color="#888")
            self.wave_ax.tick_params(colors="#888888", labelsize=8)
            self.wave_ax.grid(True, alpha=0.25, color="#dddddd")
            for spine in self.wave_ax.spines.values():
                spine.set_color("#dddddd")
            self.wave_ax.legend(facecolor="#ffffff", edgecolor="#dddddd", labelcolor="#444", fontsize=8)
            self.fig_wave.draw()

            self.const_ax.clear(); self.const_ax.set_facecolor("#fafafa")
            n_show = min(200, len(tx_syms))
            self.const_ax.plot(np.real(constellation), np.imag(constellation), "+",
                              color="#888888", markersize=10, label="Ideal")
            self.const_ax.plot(np.real(tx_syms[:n_show]), np.imag(tx_syms[:n_show]), ".",
                              color="#555555", alpha=0.4, markersize=3, label="TX")
            self.const_ax.plot(np.real(rx_syms[:n_show]), np.imag(rx_syms[:n_show]), ".",
                              color="#4a7aaa", alpha=0.6, markersize=3, label="RX")
            self.const_ax.set_title(f"Constellation  (SNR={result['snr_db']}dB)", fontsize=10, fontweight="600", color="#444")
            self.const_ax.set_xlabel("In-Phase", fontsize=9, color="#888")
            self.const_ax.set_ylabel("Quadrature", fontsize=9, color="#888")
            self.const_ax.tick_params(colors="#888888", labelsize=8)
            self.const_ax.grid(True, alpha=0.25, color="#dddddd")
            self.const_ax.set_aspect("equal")
            for spine in self.const_ax.spines.values():
                spine.set_color("#dddddd")
            self.const_ax.legend(facecolor="#ffffff", edgecolor="#dddddd", labelcolor="#444", fontsize=8)
            self.fig_const.draw()

            self.eye_ax.clear(); self.eye_ax.set_facecolor("#fafafa")
            signal_real = np.real(signal); n_sps = 8
            n_plot = len(signal_real) // n_sps * n_sps
            if n_plot >= n_sps * 3:
                for i in range(40):
                    start = int(np.random.randint(0, max(1, n_plot - n_sps * 2)))
                    eye_data = signal_real[start:start + n_sps * 2]
                    if len(eye_data) >= n_sps * 2:
                        self.eye_ax.plot(np.linspace(0, 2, len(eye_data)), eye_data, color="#4a7aaa", alpha=0.2, linewidth=0.6)
            self.eye_ax.set_title("Eye Diagram", fontsize=10, fontweight="600", color="#444")
            self.eye_ax.set_xlabel("Symbol Period", fontsize=9, color="#888")
            self.eye_ax.set_ylabel("Amplitude", fontsize=9, color="#888")
            self.eye_ax.tick_params(colors="#888888", labelsize=8)
            self.eye_ax.grid(True, alpha=0.25, color="#dddddd")
            self.eye_ax.set_xlim(0, 2)
            for spine in self.eye_ax.spines.values():
                spine.set_color("#dddddd")
            self.fig_eye.draw()
        except Exception as e:
            self.log_message(f"Plot update error: {str(e)}")

    def log_message(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        colors = self._cfg.get_theme_colors()
        preset = self._cfg.get("theme", "preset", default="light")
        # Log default color - distinct from main text per theme
        if preset == "dark":
            default_color = "#8a9aaa"
            ts_color = "#5a6a7a"
        elif preset == "high_contrast":
            default_color = "#b0c0d0"
            ts_color = "#888888"
        else:
            default_color = "#6a7a8a"
            ts_color = "#a0a0a0"
        color = default_color
        if "error" in msg.lower() or "fail" in msg.lower():
            color = "#cc5555" if preset == "dark" else "#bb4444" if preset == "high_contrast" else colors.get("error", "#8b3a3a")
        elif "complete" in msg.lower() or "success" in msg.lower():
            color = "#55bb88" if preset == "dark" else "#44cc66" if preset == "high_contrast" else colors.get("success", "#2a6a4a")
        elif "sweep" in msg.lower() or "run" in msg.lower() or "train" in msg.lower():
            color = "#55aadd" if preset == "dark" else "#44aaff" if preset == "high_contrast" else colors.get("accent", "#3a6a8a")
        elif "initialized" in msg.lower() or "ready" in msg.lower():
            color = "#55bb88" if preset == "dark" else "#44cc66" if preset == "high_contrast" else colors.get("success", "#5a7a5a")
        html = f'<span style="color:{ts_color};">[{ts}]</span> <span style="color:{color};">{msg}</span>'
        self.log_output.append(html)
        sb = self.log_output.verticalScrollBar()
        sb.setValue(sb.maximum())


    def closeEvent(self, event):
        self._cfg.save()
        super().closeEvent(event)
