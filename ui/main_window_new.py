# -*- coding: utf-8 -*-
"主窗口 - VLC智能解调系统 (集成设置页+主题联动)"

import sys
import numpy as np
from datetime import datetime
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt

from .styles import MONO_STYLE, get_theme_stylesheet
from .settings_tab import SettingsTab
from core.vlc_simulator import VLCSystemSimulator
from core.ai_demodulator import AIDemodulator
from core.signal_processing import SignalGenerator
from core.config_manager import get_config
from core.i18n import get_i18n, reload_i18n

plt.rcParams["axes.unicode_minus"] = False


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
    """Build Operation Guide tab"""
    i18n = get_i18n()
    w = QWidget()
    layout = QVBoxLayout(w)
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

    header = QLabel(i18n.tr("guide_header"))
    header.setStyleSheet("font-size: 16px; font-weight: 700; color: #1a1a1a; padding-bottom: 4px; background: transparent;")
    inner_layout.addWidget(header)

    subtitle = QLabel(i18n.tr("guide_subtitle"))
    subtitle.setWordWrap(True)
    subtitle.setStyleSheet("font-size: 12px; color: #666; line-height: 1.6; background: transparent;")
    inner_layout.addWidget(subtitle)

    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet("background-color: #d0d0d0; max-height: 1px;")
    inner_layout.addWidget(sep)

    steps = [
        ("01", "DATA", i18n.tr("step_data"),
         "Generates random binary data as the source for VLC transmission. "
         "Supports configurable data lengths of 512, 1024, 2048, or 4096 bits, "
         "selectable from the left control panel. Each bit stream is framed and "
         "prepared for QPSK symbol mapping (2 bits per symbol). The generated data "
         "serves as the ground truth for end-to-end BER evaluation."),
        ("02", "OFDM", i18n.tr("step_ofdm"),
         "Orthogonal Frequency Division Multiplexing (OFDM) is employed to combat "
         "inter-symbol interference in the optical channel. The system uses 64-point "
         "FFT with 48 active data subcarriers and a cyclic prefix of 16 samples (25% "
         "overhead). QPSK symbols are mapped to subcarriers, transformed via IFFT to "
         "the time domain, and the cyclic prefix is prepended to each OFDM symbol."),
        ("03", "LED", i18n.tr("step_led"),
         "Intensity modulation is used to drive a blue InGaN LED (450 nm wavelength, "
         "100 mW optical power, 120-degree beam angle). The time-domain OFDM signal is "
         "normalised and biased to operate within the LED linear region, ensuring minimal "
         "non-linear distortion. The LED converts the electrical signal into visible light "
         "for free-space propagation."),
        ("04", "CH", i18n.tr("step_ch"),
         "The optical signal propagates through a free-space line-of-sight (LOS) channel. "
         "Path loss, ambient light interference, shot noise, and thermal noise are modelled. "
         "The signal-to-noise ratio (SNR) is configurable from 0 to 30 dB via the slider "
         "control. Additive white Gaussian noise (AWGN) is applied to simulate realistic "
         "channel conditions."),
        ("05", "PD", i18n.tr("step_pd"),
         "A PIN photodiode at the receiver converts the incoming optical signal back to an "
         "electrical current. Key parameters include a responsivity of 0.5 A/W, "
         "detection area of 10 mm\u00b2, and dark current of 10 nA. The photodiode is "
         "modelled with linear response characteristics and thermal noise contributions."),
        ("06", "DEMOD", i18n.tr("step_demod"),
         "The received time-domain signal is segmented into OFDM symbols. The cyclic prefix "
         "is removed from each symbol, and a 64-point FFT transforms the signal back to the "
         "frequency domain. QPSK symbols are extracted from the 48 active subcarriers "
         "for constellation demapping and bit recovery."),
        ("07", "AI", i18n.tr("step_ai"),
         "A neural network-based demodulator complements the standard OFDM demodulator. "
         "The MLP classifier (64 -> 32 hidden layers) is trained on noisy QPSK symbols to "
         "learn optimal decision boundaries. After training, it provides enhanced "
         "demodulation accuracy with confidence estimates for each symbol decision."),
        ("08", "BER", i18n.tr("step_ber"),
         "End-to-end performance is evaluated via Bit Error Rate (BER) analysis. "
         "The transmitted and received bit sequences are compared to compute the BER. "
         "A sweep over SNR values from 0-30 dB generates a BER vs SNR curve, "
         "characterising the system performance under various channel conditions."),
    ]

    for num, tag, title, desc in steps:
        card = QFrame()
        card.setStyleSheet("background-color: #fafafa; border: 1px solid #e8e8e8; border-radius: 6px; "
                          "border-left: 4px solid #4a7aaa;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)
        header_row = QHBoxLayout()
        num_label = QLabel(num)
        num_label.setStyleSheet("font-size: 11px; font-weight: 700; color: #4a7aaa; background: transparent;")
        num_label.setFixedWidth(24)
        header_row.addWidget(num_label)
        tag_label = QLabel(tag)
        tag_label.setStyleSheet("font-size: 10px; font-weight: 700; color: #ffffff; "
                               "background-color: #4a7aaa; padding: 1px 8px; border-radius: 3px;")
        tag_label.setFixedHeight(18)
        header_row.addWidget(tag_label)
        header_row.addSpacing(8)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #222; background: transparent;")
        header_row.addWidget(title_label)
        header_row.addStretch()
        card_layout.addLayout(header_row)
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 11px; color: #666; line-height: 1.5; background: transparent;")
        card_layout.addWidget(desc_label)
        inner_layout.addWidget(card)

    inner_layout.addStretch()
    scroll.setWidget(inner)
    layout.addWidget(scroll)
    return w
