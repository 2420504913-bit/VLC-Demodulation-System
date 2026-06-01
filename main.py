# -*- coding: utf-8 -*-
'VLC智能解调系统 - 主入口'

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei', 9))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()