import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QPlainTextEdit)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot


class StdoutRedirector(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        if text:
            self.text_written.emit(str(text))

    def flush(self):
        pass


class AuthDialog(QDialog):
    auth_complete = pyqtSignal()
    auth_data = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tiến trình...")
        self.setGeometry(300, 300, 500, 400)
        self.setModal(True)

        self.setup_ui()

        self.stdout_redirector = StdoutRedirector()
        self.stdout_redirector.text_written.connect(self.handle_stdout)
        sys.stdout = self.stdout_redirector

        self.waiting_for_code = False
        self.waiting_for_phone = False
        self.phone_number = ""

    def setup_ui(self):
        layout = QVBoxLayout()

        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        layout.addWidget(QLabel("Tiến trình:"))
        layout.addWidget(self.console_output)

        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Số điện thoại:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+84xxxxxxxxxx - có mã quốc gia")
        phone_layout.addWidget(self.phone_input)
        self.submit_phone_btn = QPushButton("Gửi")
        self.submit_phone_btn.clicked.connect(self.submit_phone)
        phone_layout.addWidget(self.submit_phone_btn)
        layout.addLayout(phone_layout)

        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("Mã xác thực:"))
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Nhập mã xác thực được gửi về Telegram")
        code_layout.addWidget(self.code_input)
        self.submit_code_btn = QPushButton("Gửi")
        self.submit_code_btn.clicked.connect(self.submit_code)
        code_layout.addWidget(self.submit_code_btn)
        layout.addLayout(code_layout)

        self.code_input.setEnabled(False)
        self.submit_code_btn.setEnabled(False)

        self.setLayout(layout)

    @pyqtSlot(str)
    def handle_stdout(self, text):
        self.console_output.appendPlainText(text.rstrip())

        if "Vui lòng nhập số điện thoại để đăng nhập" in text:
            self.waiting_for_phone = True
            self.phone_input.setEnabled(True)
            self.submit_phone_btn.setEnabled(True)
            self.code_input.setEnabled(False)
            self.submit_code_btn.setEnabled(False)

        elif "Vui lòng nhập mã xác thực được gửi về Telegram" in text:
            self.waiting_for_code = True
            self.phone_input.setEnabled(False)
            self.submit_phone_btn.setEnabled(False)
            self.code_input.setEnabled(True)
            self.submit_code_btn.setEnabled(True)
            self.code_input.setFocus()

        elif "Đã xác thực thành công" in text:
            self.phone_input.setEnabled(False)
            self.submit_phone_btn.setEnabled(False)
            self.code_input.setEnabled(False)
            self.submit_code_btn.setEnabled(False)

    def submit_phone(self):
        phone = self.phone_input.text().strip()
        if not phone:
            self.console_output.appendPlainText("Lỗi: Vui lòng nhập số điện thoại")
            return

        if not phone.startswith("+"):
            self.console_output.appendPlainText("Warning: Số điện thoại phải bắt đầu bằng dấu + và mã quốc gia (VN: +84)")

        self.phone_number = phone
        self.phone_input.setEnabled(False)
        self.submit_phone_btn.setEnabled(False)
        self.waiting_for_phone = False

        self.auth_data.emit(self.phone_number, "")

    def submit_code(self):
        code = self.code_input.text().strip()
        if not code:
            self.console_output.appendPlainText("Lỗi: Vui lòng nhập mã xác thực")
            return

        self.code_input.setEnabled(False)
        self.submit_code_btn.setEnabled(False)
        self.waiting_for_code = False

        self.auth_data.emit(self.phone_number, code)
        self.console_output.appendPlainText("Đã gửi mã xác thực")
