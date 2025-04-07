import sys
import os
import json
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QCheckBox,
                             QComboBox, QPushButton, QSpinBox, QGroupBox,
                             QMessageBox, QFileDialog, QPlainTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QThread

from auth import AuthDialog, StdoutRedirector


class TelegramWorker(QThread):
    finished = pyqtSignal(bool)

    def run(self):
        from start import run_telegram_client
        success = run_telegram_client()
        self.finished.emit(success)


class TelegramScraperUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lọc mem Telegram")
        self.setGeometry(100, 100, 600, 600)

        self.config = {
            'bot_token': '',
            'api_hash': '',
            'api_id': '',
            'chat_id': '',
            'phone_number': '',
            'group_link': '',
            'messages_limit': 1000,
            'member_limit': 1000,
            'day_target': 0,
            'locmess': True,
            'locmember': True,
            'locavatar': False,
            'locphonenum': False
        }

        self.config_file = 'telegram_scraper_config.json'
        self.load_config()

        self.setup_ui()

        self.worker_thread = None
        self.auth_dialog = None

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.create_api_credentials_group(main_layout)

        self.create_chat_settings_group(main_layout)

        self.create_filters_group(main_layout)

        self.create_console_group(main_layout)

        action_layout = QHBoxLayout()

        save_button = QPushButton("Lưu cấu hình")
        save_button.clicked.connect(self.save_config)
        action_layout.addWidget(save_button)

        run_button = QPushButton("Bắt đầu lọc")
        run_button.clicked.connect(self.run_scraper)
        action_layout.addWidget(run_button)

        main_layout.addLayout(action_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.stdout_redirector = StdoutRedirector()
        self.stdout_redirector.text_written.connect(self.append_to_console)
        sys.stdout = self.stdout_redirector

    def create_api_credentials_group(self, parent_layout):
        group_box = QGroupBox("API")
        layout = QVBoxLayout()

        bot_layout = QHBoxLayout()
        bot_layout.addWidget(QLabel("Bot Token:"))
        self.bot_token_input = QLineEdit(self.config['bot_token'])
        bot_layout.addWidget(self.bot_token_input)
        self.save_bot_token_cb = QCheckBox("Save")
        self.save_bot_token_cb.setChecked(bool(self.config['bot_token']))
        bot_layout.addWidget(self.save_bot_token_cb)
        layout.addLayout(bot_layout)

        api_hash_layout = QHBoxLayout()
        api_hash_layout.addWidget(QLabel("API Hash:"))
        self.api_hash_input = QLineEdit(self.config['api_hash'])
        api_hash_layout.addWidget(self.api_hash_input)
        self.save_api_hash_cb = QCheckBox("Save")
        self.save_api_hash_cb.setChecked(bool(self.config['api_hash']))
        api_hash_layout.addWidget(self.save_api_hash_cb)
        layout.addLayout(api_hash_layout)

        api_id_layout = QHBoxLayout()
        api_id_layout.addWidget(QLabel("API ID:"))
        self.api_id_input = QLineEdit(self.config['api_id'])
        api_id_layout.addWidget(self.api_id_input)
        self.save_api_id_cb = QCheckBox("Save")
        self.save_api_id_cb.setChecked(bool(self.config['api_id']))
        api_id_layout.addWidget(self.save_api_id_cb)
        layout.addLayout(api_id_layout)

        chat_id_layout = QHBoxLayout()
        chat_id_layout.addWidget(QLabel("Chat ID:"))
        self.chat_id_input = QLineEdit(self.config['chat_id'])
        chat_id_layout.addWidget(self.chat_id_input)
        self.save_chat_id_cb = QCheckBox("Save")
        self.save_chat_id_cb.setChecked(bool(self.config['chat_id']))
        chat_id_layout.addWidget(self.save_chat_id_cb)
        layout.addLayout(chat_id_layout)

        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Số điện thoại:"))
        self.phone_input = QLineEdit(self.config['phone_number'])
        phone_layout.addWidget(self.phone_input)
        self.save_phone_cb = QCheckBox("Save")
        self.save_phone_cb.setChecked(bool(self.config['phone_number']))
        phone_layout.addWidget(self.save_phone_cb)
        layout.addLayout(phone_layout)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def create_chat_settings_group(self, parent_layout):
        group_box = QGroupBox("Cấu hình lọc")
        layout = QVBoxLayout()

        group_link_layout = QHBoxLayout()
        group_link_layout.addWidget(QLabel("Link group:"))
        self.group_link_input = QLineEdit(self.config['group_link'])
        group_link_layout.addWidget(self.group_link_input)
        self.save_group_link_cb = QCheckBox("Save")
        self.save_group_link_cb.setChecked(bool(self.config['group_link']))
        group_link_layout.addWidget(self.save_group_link_cb)
        layout.addLayout(group_link_layout)

        limits_layout = QHBoxLayout()

        limits_layout.addWidget(QLabel("Giới hạn tin nhắn:"))
        self.messages_limit_input = QSpinBox()
        self.messages_limit_input.setRange(1, 10000)
        self.messages_limit_input.setValue(self.config['messages_limit'])
        limits_layout.addWidget(self.messages_limit_input)

        limits_layout.addWidget(QLabel("Giới hạn thành viên:"))
        self.member_limit_input = QSpinBox()
        self.member_limit_input.setRange(1, 10000)
        self.member_limit_input.setValue(self.config['member_limit'])
        limits_layout.addWidget(self.member_limit_input)

        layout.addLayout(limits_layout)

        day_target_layout = QHBoxLayout()
        day_target_layout.addWidget(QLabel("Lọc trong bao nhiêu ngày (0 là hôm nay):"))
        self.day_target_combo = QComboBox()
        for i in range(31):
            self.day_target_combo.addItem(str(i))
        self.day_target_combo.setCurrentIndex(self.config['day_target'])
        day_target_layout.addWidget(self.day_target_combo)
        layout.addLayout(day_target_layout)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def create_filters_group(self, parent_layout):
        group_box = QGroupBox("Kiểu lọc")
        layout = QVBoxLayout()

        self.locmess_cb = QCheckBox("Lọc theo tin nhắn")
        self.locmess_cb.setChecked(self.config['locmess'])
        layout.addWidget(self.locmess_cb)

        self.locmember_cb = QCheckBox("Lọc theo thành viên")
        self.locmember_cb.setChecked(self.config['locmember'])
        layout.addWidget(self.locmember_cb)

        self.locavatar_cb = QCheckBox("Chỉ lọc thành viên có avatar")
        self.locavatar_cb.setChecked(self.config['locavatar'])
        layout.addWidget(self.locavatar_cb)

        self.locphonenum_cb = QCheckBox("Chỉ lọc thành viên có số điện thoại")
        self.locphonenum_cb.setChecked(self.config['locphonenum'])
        layout.addWidget(self.locphonenum_cb)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def create_console_group(self, parent_layout):
        group_box = QGroupBox()
        layout = QVBoxLayout()

        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMaximumHeight(150)
        layout.addWidget(self.console_output)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    for key in saved_config:
                        if key in self.config:
                            self.config[key] = saved_config[key]
        except Exception:
            print(f"Lỗi khi load cấu hình")

    def save_config(self):
        config_to_save = {}

        if self.save_bot_token_cb.isChecked():
            config_to_save['bot_token'] = self.bot_token_input.text()

        if self.save_api_hash_cb.isChecked():
            config_to_save['api_hash'] = self.api_hash_input.text()

        if self.save_api_id_cb.isChecked():
            config_to_save['api_id'] = self.api_id_input.text()

        if self.save_chat_id_cb.isChecked():
            config_to_save['chat_id'] = self.chat_id_input.text()

        if self.save_phone_cb.isChecked():
            config_to_save['phone_number'] = self.phone_input.text()

        if self.save_group_link_cb.isChecked():
            config_to_save['group_link'] = self.group_link_input.text()

        config_to_save['messages_limit'] = self.messages_limit_input.value()
        config_to_save['member_limit'] = self.member_limit_input.value()
        config_to_save['day_target'] = self.day_target_combo.currentIndex()
        config_to_save['locmess'] = self.locmess_cb.isChecked()
        config_to_save['locmember'] = self.locmember_cb.isChecked()
        config_to_save['locavatar'] = self.locavatar_cb.isChecked()
        config_to_save['locphonenum'] = self.locphonenum_cb.isChecked()

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            QMessageBox.information(self, "Hoàn thành", "Đã lưu cấu hình.")
        except Exception:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu cấu hình")

    def get_current_config(self):
        current_config = {
            'bot_token': self.bot_token_input.text(),
            'api_hash': self.api_hash_input.text(),
            'api_id': self.api_id_input.text(),
            'chat_id': self.chat_id_input.text(),
            'phone_number': self.phone_input.text(),
            'group_link': self.group_link_input.text(),
            'messages_limit': self.messages_limit_input.value(),
            'member_limit': self.member_limit_input.value(),
            'day_target': self.day_target_combo.currentIndex(),
            'locmess': 'y' if self.locmess_cb.isChecked() else 'n',
            'locmember': 'y' if self.locmember_cb.isChecked() else 'n',
            'locavatar': 'y' if self.locavatar_cb.isChecked() else 'n',
            'locphonenum': 'y' if self.locphonenum_cb.isChecked() else 'n'
        }
        return current_config

    def validate_inputs(self):
        required_fields = {
            'Bot Token': self.bot_token_input.text(),
            'API Hash': self.api_hash_input.text(),
            'API ID': self.api_id_input.text(),
            'Chat ID': self.chat_id_input.text(),
            'Group Link': self.group_link_input.text()
        }

        missing_fields = []
        for field_name, value in required_fields.items():
            if not value.strip():
                missing_fields.append(field_name)

        if not (self.locmess_cb.isChecked() or self.locmember_cb.isChecked()):
            QMessageBox.warning(self, "Lỗi",
                                "Bạn phải chọn ít nhất 1 kiểu lọc (tin nhắn hoặc thành viên).")
            return False

        if required_fields['API ID'].strip() and not required_fields['API ID'].strip().isdigit():
            QMessageBox.warning(self, "Lỗi", "API ID phải là số")
            return False

        api_hash = required_fields['API Hash'].strip()
        if api_hash and (len(api_hash) != 32 or not all(c in '0123456789abcdef' for c in api_hash.lower())):
            QMessageBox.warning(self, "Lỗi", "API Hash không đúng định dạng (cần 32 ký tự hex)")
            return False

        if missing_fields:
            QMessageBox.warning(self, "Lỗi",
                                f"Vui lòng nhập thông tin: {', '.join(missing_fields)}")
            return False

        return True

    @pyqtSlot(str)
    def append_to_console(self, text):
        self.console_output.appendPlainText(text.rstrip())

    def handle_auth_data(self, phone, code):
        import start

        if code:
            start.auth_code = code
            start.auth_code_ready.set()
        else:
            start.auth_phone = phone
            start.auth_ready.set()

    @pyqtSlot(bool)
    def handle_worker_finished(self, success):
        if success:
            QMessageBox.information(self, "Hoàn thành", "Quá trình lọc đã hoàn thành!")
        else:
            QMessageBox.warning(self, "Lỗi", "Có lỗi xảy ra trong quá trình lọc!")

        if self.auth_dialog and self.auth_dialog.isVisible():
            self.auth_dialog.close()

            sys.stdout = sys.__stdout__

    def run_scraper(self):
        if not self.validate_inputs():
            return

        current_config = self.get_current_config()

        self.create_temp_config_file(current_config)

        import start
        start.auth_phone = None
        start.auth_code = None
        start.auth_ready.clear()
        start.auth_code_ready.clear()

        self.auth_dialog = AuthDialog(self)
        self.auth_dialog.auth_data.connect(self.handle_auth_data)
        self.auth_dialog.show()

        self.worker_thread = TelegramWorker()
        self.worker_thread.finished.connect(self.handle_worker_finished)
        self.worker_thread.start()

    def create_temp_config_file(self, config):
        with open('config.py', 'w', encoding='utf-8') as f:
            f.write(f"bot_token = '{config['bot_token']}'\n\n")
            f.write(f"api_hash = '{config['api_hash']}'\n")
            f.write(f"api_id = '{config['api_id']}'\n\n")
            f.write(f"chat_id = '{config['chat_id']}'\n\n")
            f.write(f"group_link = '{config['group_link']}'\n")
            f.write(f"phone_number = '{config['phone_number']}'\n")
            f.write(f"messages_limit = {config['messages_limit']}\n")
            f.write(f"member_limit = {config['member_limit']}\n")
            f.write(f"day_target = {config['day_target']}\n\n")
            f.write(f"locmess = '{config['locmess']}'\n")
            f.write(f"locmember = '{config['locmember']}'\n")
            f.write(f"locavatar = '{config['locavatar']}'\n")
            f.write(f"locphonenum = '{config['locphonenum']}'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelegramScraperUI()
    window.show()
    sys.exit(app.exec_())
