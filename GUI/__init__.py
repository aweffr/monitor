#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In this example, we create a simple
window in PyQt5.

author: Jan Bodnar
website: zetcode.com
last edited: January 2015
"""

import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QIcon


class Example(QWidget):
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(self.WIDTH, self.HEIGHT)
        self.center()
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('icon.png'))

        self.addButton()

        self.show()

    def closeEvent(self, event):
        # 这重写了右上角的关闭按钮的方法
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def addButton(self):
        btn = QPushButton('Button', self)
        btn.setToolTip("Useless Button.")
        btn.resize(btn.sizeHint())
        btn.move(200, self.HEIGHT // 2)

        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QCoreApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(400, self.HEIGHT // 2)

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
