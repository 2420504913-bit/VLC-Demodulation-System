# -*- coding: utf-8 -*-
"UI样式 - 主题生成器 + 预设主题"

from core.config_manager import get_config


def generate_styles(colors=None):
    """根据颜色配置动态生成完整样式表"""
    if colors is None:
        cfg = get_config()
        colors = cfg.get_theme_colors()

    c = colors  # shorthand

    return f"""
/* ===== GLOBAL ===== */
QMainWindow, QDialog {{
    background-color: {c["bg_primary"]};
    color: {c["text_primary"]};
    font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
}}

/* ===== TITLE BAR ===== */
#titleBar {{
    background-color: {c["bg_secondary"]};
    border-bottom: 1px solid {c["border"]};
    border-radius: 0px;
    min-height: 42px;
    padding: 0px;
}}

#mainTitle {{
    color: {c["text_primary"]};
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 3px;
    background: transparent;
    padding: 0px;
}}

#mainSubtitle {{
    color: {c["text_muted"]};
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 1px;
    background: transparent;
}}

#accentBar {{
    background-color: {c["accent"]};
    border: none;
    border-radius: 2px;
}}

/* ===== LEFT PANEL ===== */
#leftPanel, QWidget#leftPanel {{
    background-color: {c["card_bg"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
}}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background-color: {c["bg_primary"]};
    border: 1px solid {c["border"]};
    border-radius: 5px;
    margin-top: 14px;
    padding: 12px 10px 8px 10px;
    font-weight: 600;
    color: {c["text_secondary"]};
    font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0px 8px;
    background-color: {c["bg_secondary"]};
    border: 1px solid {c["border"]};
    border-radius: 3px;
    color: {c["text_primary"]};
    font-size: 11px;
    letter-spacing: 1px;
}}
QGroupBox:hover {{
    border-color: {c["accent"]};
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: {c["input_bg"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: 600;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: {c["accent_light"]};
    border-color: {c["accent"]};
}}
QPushButton:pressed {{
    background-color: {c["accent_hover"]};
    color: #ffffff;
}}
QPushButton:disabled {{
    background-color: transparent;
    color: {c["text_muted"]};
    border-color: {c["border"]};
}}

#btnPrimary {{
    background-color: {c["accent_light"]};
    border-color: {c["accent"]};
    color: {c["accent"]};
}}
#btnPrimary:hover {{
    background-color: {c["accent"]};
    border-color: {c["accent_hover"]};
    color: #ffffff;
}}
#btnPrimary:pressed {{
    background-color: {c["accent_hover"]};
}}

#btnSecondary {{
    background-color: {c["input_bg"]};
    border-color: {c["border"]};
    color: {c["text_secondary"]};
}}
#btnSecondary:hover {{
    background-color: {c["accent_light"]};
    border-color: {c["accent"]};
    color: {c["accent"]};
}}

/* ===== LABELS ===== */
QLabel {{
    color: {c["text_secondary"]};
    font-size: 12px;
    background-color: transparent;
}}
QLabel[heading="true"] {{
    color: {c["text_primary"]};
    font-size: 13px;
    font-weight: 700;
}}
QLabel[value="true"] {{
    color: {c["text_primary"]};
    font-size: 13px;
    font-weight: 700;
}}
QLabel[accent="true"] {{
    color: {c["accent"]};
    font-weight: 700;
}}
QLabel[muted="true"] {{
    color: {c["text_muted"]};
    font-size: 11px;
}}

/* ===== COMBO BOX ===== */
QComboBox {{
    background-color: {c["input_bg"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border"]};
    border-radius: 3px;
    padding: 2px 6px;
    min-height: 22px;
    font-size: 12px;
}}
QComboBox:hover {{
    border-color: {c["accent"]};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {c["text_muted"]};
    margin-right: 4px;
}}
QComboBox QAbstractItemView {{
    background-color: {c["input_bg"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border"]};
    selection-background-color: {c["accent_light"]};
    selection-color: {c["text_primary"]};
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    background-color: {c["input_bg"]};
    color: {c["text_primary"]};
    padding: 4px 8px;
    min-height: 22px;
    border: none;
}}
QComboBox QAbstractItemView::item:hover,
QComboBox QAbstractItemView::item:selected {{
    background-color: {c["accent_light"]};
    color: {c["accent"]};
}}
QComboBox QAbstractItemView QScrollBar:vertical {{
    background: {c["bg_primary"]};
    width: 8px;
}}
QComboBox QAbstractItemView QScrollBar::handle:vertical {{
    background: {c["border"]};
    border-radius: 4px;
    min-height: 20px;
}}

/* ===== SLIDER ===== */
QSlider::groove:horizontal {{
    height: 4px;
    background: {c["border"]};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {c["accent_light"]};
    border: 1px solid {c["accent"]};
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{
    background: {c["accent"]};
    border-color: {c["accent_hover"]};
}}
QSlider::sub-page:horizontal {{
    background: {c["accent"]};
    border-radius: 2px;
}}

/* ===== SPIN BOX ===== */
QSpinBox {{
    background-color: {c["input_bg"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border"]};
    border-radius: 3px;
    padding: 2px 4px;
    min-height: 22px;
}}
QSpinBox:focus {{
    border-color: {c["accent"]};
}}

/* ===== LINE EDIT ===== */
QLineEdit {{
    background-color: {c["input_bg"]};
    color: {c["text_primary"]};
    border: 1px solid {c["border"]};
    border-radius: 3px;
    padding: 3px 6px;
}}
QLineEdit:focus {{
    border-color: {c["accent"]};
}}

/* ===== CHECK BOX ===== */
QCheckBox {{
    color: {c["text_secondary"]};
    font-size: 12px;
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border-radius: 2px;
    border: 1px solid {c["border"]};
    background-color: {c["input_bg"]};
}}
QCheckBox::indicator:checked {{
    background-color: {c["accent"]};
    border-color: {c["accent_hover"]};
}}
QCheckBox:hover {{
    color: {c["text_primary"]};
}}

/* ===== RADIO BUTTON ===== */
QRadioButton {{
    color: {c["text_secondary"]};
    font-size: 12px;
    spacing: 6px;
}}
QRadioButton::indicator {{
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 1px solid {c["border"]};
    background-color: {c["input_bg"]};
}}
QRadioButton::indicator:checked {{
    background-color: {c["accent"]};
    border-color: {c["accent_hover"]};
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    background-color: {c["bg_secondary"]};
    border: 1px solid {c["border"]};
    border-top: none;
    border-radius: 0px 0px 4px 4px;
}}
QTabBar {{
    background-color: {c["bg_primary"]};
    padding: 0px;
    border-bottom: 1px solid {c["border"]};
}}
QTabBar::tab {{
    background-color: {c["bg_primary"]};
    color: {c["text_muted"]};
    padding: 7px 18px;
    border: none;
    border-right: 1px solid {c["border"]};
    font-size: 11px;
    font-weight: 600;
    min-width: 70px;
}}
QTabBar::tab:hover {{
    background-color: {c["accent_light"]};
    color: {c["accent"]};
}}
QTabBar::tab:selected {{
    background-color: {c["bg_secondary"]};
    color: {c["text_primary"]};
    border-bottom: 3px solid {c["tab_selected"]};
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QTabBar::tab:first {{
    font-size: 12px;
    font-weight: 700;
    color: {c["accent"]};
    background-color: {c["accent_light"]};
    min-width: 130px;
    padding: 7px 22px;
}}
QTabBar::tab:first:selected {{
    background-color: {c["bg_secondary"]};
    color: {c["text_primary"]};
    border-bottom: 3px solid {c["tab_selected"]};
}}
QTabBar::tab:first:hover {{
    background-color: {c["accent_light"]};
    color: {c["accent"]};
}}

/* ===== TEXT EDIT (LOG) ===== */
QTextEdit, QPlainTextEdit {{
    background-color: {c["bg_primary"]};
    color: {c["text_secondary"]};
    border: 1px solid {c["border"]};
    border-radius: 3px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    padding: 4px 6px;
    selection-background-color: {c["accent_light"]};
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {c["accent"]};
}}

/* ===== SCROLL BARS ===== */
QScrollBar:vertical {{
    background: {c["bg_primary"]};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {c["border"]};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c["accent"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {c["bg_primary"]};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {c["border"]};
    border-radius: 4px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {c["accent"]};
}}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    background-color: {c["bg_primary"]};
    border: 1px solid {c["border"]};
    border-radius: 3px;
    text-align: center;
    color: {c["text_muted"]};
    height: 16px;
    font-size: 10px;
}}
QProgressBar::chunk {{
    background-color: {c["accent"]};
    border-radius: 2px;
}}

/* ===== SCROLL AREA ===== */
QScrollArea {{
    border: none;
    background: transparent;
}}
"""


# Default light mode styles (static, for backward compatibility and initial load)
MONO_STYLE = generate_styles({
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
})


def get_theme_stylesheet(colors=None):
    """获取当前主题的样式表"""
    if colors is None:
        cfg = get_config()
        colors = cfg.get_theme_colors()
    return generate_styles(colors)
