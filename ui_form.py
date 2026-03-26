# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QStackedWidget,
    QStatusBar, QTextBrowser, QTextEdit, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1230, 727)
        MainWindow.setStyleSheet(u"\n"
"/* ====== GLOBAL APPLICATION STYLE (DARK THEME) ====== */\n"
"\n"
"/* --- MAIN WINDOW BACKGROUND --- */\n"
"QMainWindow, QWidget#centralwidget {\n"
"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #1a1a2e);\n"
"}\n"
"\n"
"QStackedWidget {\n"
"    background: transparent;\n"
"}\n"
"\n"
"/* --- NAVIGATION BUTTONS --- */\n"
"QPushButton#btnTureng, QPushButton#btnTranslate, QPushButton#btnMyWords {\n"
"    background-color: rgba(30, 30, 50, 0.8);\n"
"    color: #a0a4b0;\n"
"    border: none;\n"
"    border-bottom: 3px solid transparent;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    font-weight: bold;\n"
"    padding: 12px 20px;\n"
"    border-radius: 0px;\n"
"}\n"
"\n"
"QPushButton#btnTureng:hover, QPushButton#btnTranslate:hover, QPushButton#btnMyWords:hover {\n"
"    background-color: rgba(40, 40, 65, 0.9);\n"
"    color: #6c9fff;\n"
"    border-bottom: 3px solid #6c9fff;\n"
"    border-radius: 0px;\n"
"}\n"
"\n"
""
                        "/* --- GENERAL TEXT AREAS --- */\n"
"QTextEdit, QTextBrowser {\n"
"    background-color: transparent;\n"
"    color: #e0e0e0;\n"
"    border: none;\n"
"    font-size: 15px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"/* --- GENERAL LINE EDIT --- */\n"
"QLineEdit {\n"
"    background-color: #2b2b3d;\n"
"    color: #e0e0e0;\n"
"    border: 1px solid #3a3a50;\n"
"    border-radius: 8px;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 8px 16px;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border: 2px solid #6c9fff;\n"
"}\n"
"\n"
"/* --- GENERAL COMBOBOX --- */\n"
"QComboBox {\n"
"    background-color: transparent;\n"
"    color: #a0a4b0;\n"
"    border: none;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 6px 12px;\n"
"}\n"
"\n"
"/* --- GENERAL LABEL --- */\n"
"QLabel {\n"
"    color: #e0e0e0;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    background: transparent;\n"
"}\n"
"\n"
"/* --- ST"
                        "ATUS BAR --- */\n"
"QStatusBar {\n"
"    background-color: rgba(20, 20, 35, 0.8);\n"
"    color: #a0a4b0;\n"
"    font-size: 12px;\n"
"    border-top: 1px solid #2a2a40;\n"
"}\n"
"   ")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, 60, 1231, 661))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setStyleSheet(u"\n"
"/* --- TURENG PAGE STYLE (DARK THEME) --- */\n"
"QWidget#page {\n"
"    background: transparent;\n"
"}\n"
"\n"
"/* --- SEARCH CARD --- */\n"
"QWidget#turengSearchCard {\n"
"    background-color: #2b2b3d;\n"
"    border-radius: 12px;\n"
"    border: 1px solid #3a3a50;\n"
"}\n"
"\n"
"/* --- SEARCH INPUT --- */\n"
"QLineEdit#turengInput {\n"
"    background-color: transparent;\n"
"    color: #e0e0e0;\n"
"    border: none;\n"
"    border-bottom: 2px solid #3a3a50;\n"
"    border-radius: 0px;\n"
"    font-size: 16px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 12px 20px;\n"
"}\n"
"\n"
"QLineEdit#turengInput:focus {\n"
"    border: none;\n"
"    border-bottom: 2px solid #6c9fff;\n"
"}\n"
"\n"
"/* --- TRANSLATE BUTONU --- */\n"
"QPushButton#turengTranslateBtn {\n"
"    background-color: #4a7fd4;\n"
"    color: #ffffff;\n"
"    border-radius: 8px;\n"
"    padding: 10px 24px;\n"
"    font-weight: bold;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    border: none;"
                        "\n"
"}\n"
"\n"
"QPushButton#turengTranslateBtn:hover {\n"
"    background-color: #6c9fff;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"/* --- RESULT CARD --- */\n"
"QWidget#turengResultCard {\n"
"    background-color: #2b2b3d;\n"
"    border-radius: 12px;\n"
"    border: 1px solid #3a3a50;\n"
"}\n"
"\n"
"QTextBrowser#turengResults {\n"
"    background-color: transparent;\n"
"    color: #e0e0e0;\n"
"    border: none;\n"
"    font-size: 15px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 16px 20px;\n"
"}\n"
"\n"
"/* --- TITLE LABEL --- */\n"
"QLabel#label {\n"
"    color: #6c9fff;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    font-weight: bold;\n"
"    background: transparent;\n"
"}\n"
"      ")
        self.turengSearchCard = QWidget(self.page)
        self.turengSearchCard.setObjectName(u"turengSearchCard")
        self.turengSearchCard.setGeometry(QRect(120, 30, 990, 80))
        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        self.label.setEnabled(True)
        self.label.setGeometry(QRect(140, 42, 120, 50))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(22)
        font.setBold(True)
        font.setKerning(True)
        self.label.setFont(font)
        self.turengInput = QLineEdit(self.page)
        self.turengInput.setObjectName(u"turengInput")
        self.turengInput.setGeometry(QRect(270, 45, 580, 45))
        self.turengTranslateBtn = QPushButton(self.page)
        self.turengTranslateBtn.setObjectName(u"turengTranslateBtn")
        self.turengTranslateBtn.setGeometry(QRect(870, 45, 220, 45))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setBold(True)
        self.turengTranslateBtn.setFont(font1)
        self.turengTranslateBtn.setAutoDefault(False)
        self.turengResultCard = QWidget(self.page)
        self.turengResultCard.setObjectName(u"turengResultCard")
        self.turengResultCard.setGeometry(QRect(120, 130, 990, 490))
        self.turengResults = QTextBrowser(self.page)
        self.turengResults.setObjectName(u"turengResults")
        self.turengResults.setGeometry(QRect(122, 132, 986, 486))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        self.turengResults.setFont(font2)
        self.stackedWidget.addWidget(self.page)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setStyleSheet(u"\n"
"/* --- PAGE BACKGROUND (DARK THEME) --- */\n"
"QWidget#page_3 {\n"
"    background: transparent;\n"
"}\n"
"\n"
"/* --- LANGUAGE SELECTION COMBOBOX --- */\n"
"QComboBox#inputBox, QComboBox#outputBox {\n"
"    background-color: #2b2b3d;\n"
"    color: #c0c4d0;\n"
"    border: 1.5px solid #3a3a50;\n"
"    border-radius: 8px;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    font-weight: 600;\n"
"    padding: 8px 14px;\n"
"}\n"
"\n"
"QComboBox#inputBox:hover, QComboBox#outputBox:hover {\n"
"    border: 1.5px solid #6c9fff;\n"
"    color: #6c9fff;\n"
"}\n"
"\n"
"QComboBox#inputBox::drop-down, QComboBox#outputBox::drop-down {\n"
"    border: none;\n"
"    width: 24px;\n"
"    subcontrol-position: center right;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QComboBox#inputBox::down-arrow, QComboBox#outputBox::down-arrow {\n"
"    image: none;\n"
"    border-left: 5px solid transparent;\n"
"    border-right: 5px solid transparent;\n"
"    border-top: 6px solid #a0a4b0;\n"
"    margin-rig"
                        "ht: 6px;\n"
"}\n"
"\n"
"QComboBox#inputBox QAbstractItemView, QComboBox#outputBox QAbstractItemView {\n"
"    background-color: #2b2b3d;\n"
"    color: #c0c4d0;\n"
"    border: 1px solid #3a3a50;\n"
"    border-radius: 8px;\n"
"    padding: 4px;\n"
"    selection-background-color: #3a4a6b;\n"
"    selection-color: #6c9fff;\n"
"}\n"
"\n"
"/* --- SWAP BUTONU --- */\n"
"QPushButton#reverseButton {\n"
"    background-color: transparent;\n"
"    color: #a0a4b0;\n"
"    border: none;\n"
"    font-size: 18px;\n"
"    border-radius: 18px;\n"
"}\n"
"\n"
"QPushButton#reverseButton:hover {\n"
"    background-color: #3a3a50;\n"
"    border-radius: 18px;\n"
"}\n"
"\n"
"/* --- INPUT CARD --- */\n"
"QWidget#inputCardWidget {\n"
"    background-color: #2b2b3d;\n"
"    border-radius: 12px;\n"
"    border: 1px solid #3a3a50;\n"
"}\n"
"\n"
"/* --- OUTPUT CARD --- */\n"
"QWidget#outputCardWidget {\n"
"    background-color: #242436;\n"
"    border-radius: 12px;\n"
"    border: 1px solid #3a3a50;\n"
"}\n"
"\n"
"/* --- TEXT AREAS --"
                        "- */\n"
"QTextEdit#translateInput {\n"
"    background-color: transparent;\n"
"    color: #e0e0e0;\n"
"    border: none;\n"
"    font-size: 16px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 16px 20px;\n"
"}\n"
"\n"
"QTextBrowser#translateOutput {\n"
"    background-color: transparent;\n"
"    color: #e0e0e0;\n"
"    border: none;\n"
"    font-size: 16px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    padding: 16px 20px;\n"
"}\n"
"\n"
"/* --- VOICE BUTTONS --- */\n"
"QPushButton#inputVoiceBtn, QPushButton#outputVoiceBtn {\n"
"    background-color: transparent;\n"
"    color: #8a8e9a;\n"
"    border: none;\n"
"    font-size: 18px;\n"
"    border-radius: 18px;\n"
"}\n"
"\n"
"QPushButton#inputVoiceBtn:hover, QPushButton#outputVoiceBtn:hover {\n"
"    background-color: #3a3a50;\n"
"    border-radius: 18px;\n"
"}\n"
"\n"
"/* --- CHARACTER COUNTER --- */\n"
"QLabel#charCountLabel {\n"
"    color: #6a6e7a;\n"
"    font-size: 13px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    backg"
                        "round-color: transparent;\n"
"    border: none;\n"
"}\n"
"      ")
        self.inputBox = QComboBox(self.page_3)
        self.inputBox.addItem("")
        self.inputBox.addItem("")
        self.inputBox.setObjectName(u"inputBox")
        self.inputBox.setGeometry(QRect(420, 10, 160, 36))
        self.reverseButton = QPushButton(self.page_3)
        self.reverseButton.setObjectName(u"reverseButton")
        self.reverseButton.setGeometry(QRect(600, 10, 36, 36))
        font3 = QFont()
        self.reverseButton.setFont(font3)
        self.outputBox = QComboBox(self.page_3)
        self.outputBox.addItem("")
        self.outputBox.setObjectName(u"outputBox")
        self.outputBox.setGeometry(QRect(650, 10, 160, 36))
        self.inputCardWidget = QWidget(self.page_3)
        self.inputCardWidget.setObjectName(u"inputCardWidget")
        self.inputCardWidget.setGeometry(QRect(40, 60, 565, 560))
        self.translateInput = QTextEdit(self.page_3)
        self.translateInput.setObjectName(u"translateInput")
        self.translateInput.setGeometry(QRect(42, 62, 561, 495))
        self.inputVoiceBtn = QPushButton(self.page_3)
        self.inputVoiceBtn.setObjectName(u"inputVoiceBtn")
        self.inputVoiceBtn.setGeometry(QRect(52, 572, 36, 36))
        self.charCountLabel = QLabel(self.page_3)
        self.charCountLabel.setObjectName(u"charCountLabel")
        self.charCountLabel.setGeometry(QRect(510, 576, 80, 28))
        self.charCountLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.outputCardWidget = QWidget(self.page_3)
        self.outputCardWidget.setObjectName(u"outputCardWidget")
        self.outputCardWidget.setGeometry(QRect(625, 60, 565, 560))
        self.translateOutput = QTextBrowser(self.page_3)
        self.translateOutput.setObjectName(u"translateOutput")
        self.translateOutput.setGeometry(QRect(627, 62, 561, 495))
        self.translateOutput.setFont(font2)
        self.outputVoiceBtn = QPushButton(self.page_3)
        self.outputVoiceBtn.setObjectName(u"outputVoiceBtn")
        self.outputVoiceBtn.setGeometry(QRect(637, 572, 36, 36))
        self.stackedWidget.addWidget(self.page_3)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setStyleSheet(u"\n"
"QWidget#page_2 {\n"
"    background: transparent;\n"
"}\n"
"\n"
"QWidget#myWordsCard {\n"
"    background-color: #2b2b3d;\n"
"    border-radius: 12px;\n"
"    border: 1px solid #3a3a50;\n"
"}\n"
"\n"
"QLabel#myWordsPlaceholder {\n"
"    color: #6a6e7a;\n"
"    font-size: 18px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"    background: transparent;\n"
"}\n"
"      ")
        self.myWordsCard = QWidget(self.page_2)
        self.myWordsCard.setObjectName(u"myWordsCard")
        self.myWordsCard.setGeometry(QRect(120, 30, 990, 590))
        self.myWordsPlaceholder = QLabel(self.page_2)
        self.myWordsPlaceholder.setObjectName(u"myWordsPlaceholder")
        self.myWordsPlaceholder.setGeometry(QRect(120, 280, 990, 60))
        self.myWordsPlaceholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.addWidget(self.page_2)
        self.btnTureng = QPushButton(self.centralwidget)
        self.btnTureng.setObjectName(u"btnTureng")
        self.btnTureng.setGeometry(QRect(0, 0, 241, 61))
        self.btnTureng.setFont(font1)
        self.btnTranslate = QPushButton(self.centralwidget)
        self.btnTranslate.setObjectName(u"btnTranslate")
        self.btnTranslate.setGeometry(QRect(240, 0, 241, 61))
        self.btnTranslate.setFont(font1)
        self.btnMyWords = QPushButton(self.centralwidget)
        self.btnMyWords.setObjectName(u"btnMyWords")
        self.btnMyWords.setGeometry(QRect(480, 0, 241, 61))
        self.btnMyWords.setFont(font1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Translator", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Word :", None))
        self.turengInput.setText("")
        self.turengInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search a word...", None))
        self.turengTranslateBtn.setText(QCoreApplication.translate("MainWindow", u"\U0001f50d  Translate", None))
        self.inputBox.setItemText(0, QCoreApplication.translate("MainWindow", u"English", None))
        self.inputBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Turkish", None))

        self.reverseButton.setText(QCoreApplication.translate("MainWindow", u"\u21c6", None))
        self.outputBox.setItemText(0, QCoreApplication.translate("MainWindow", u"English", None))

        self.translateInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type or paste text to translate", None))
        self.inputVoiceBtn.setText(QCoreApplication.translate("MainWindow", u"\U0001f50a", None))
        self.charCountLabel.setText(QCoreApplication.translate("MainWindow", u"0 / 500", None))
        self.outputVoiceBtn.setText(QCoreApplication.translate("MainWindow", u"\U0001f50a", None))
        self.myWordsPlaceholder.setText(QCoreApplication.translate("MainWindow", u"\U0001f4da  Your saved words will appear here", None))
        self.btnTureng.setText(QCoreApplication.translate("MainWindow", u"\U0001f4d6  Tureng", None))
        self.btnTranslate.setText(QCoreApplication.translate("MainWindow", u"\U0001f310  Translate", None))
        self.btnMyWords.setText(QCoreApplication.translate("MainWindow", u"\U0001f4dd  My Words", None))
    # retranslateUi

