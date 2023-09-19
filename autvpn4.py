import os
import subprocess
import requests
import base64
import tempfile
import random
import sys
import urllib3
import shutil
import platform
from getpass import getpass
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox


VPN_GATE_API_URL = "https://www.vpngate.net/api/iphone/"
TEMP_DIR = tempfile.mkdtemp()

class AutoVpn4:
    def __init__(self, country="US"):
        self.country = country.upper()
        self.servers = []
        self.password = None
        self.config_file_path = None
        self.get_server_list()

    def save_config_file(self, server_index):
        print("[autovpn4] Writing config file")
        try:
            server_data = base64.b64decode(self.servers[server_index + 8]).decode("utf-8")
            config_file_path = os.path.join(TEMP_DIR, "config.ovpn")
            with open(config_file_path, "w") as config_file:
                config_file.write(server_data)
            self.config_file_path = config_file_path
        except Exception as e:
            print("[autovpn4] Failed to create config file:", e)

    def get_server_list(self):
        if not self.country:
            self.country = "US"
        print("[autovpn4] Looking for", self.country)

        try:
            urllib3.disable_warnings()
            response = requests.get(VPN_GATE_API_URL, verify=False)
            server_list = response.text.split(",")
            self.servers.extend([x for x in server_list if len(x) > 15])
            try:
                server_index = self.servers.index(self.country)
            except ValueError:
                sys.exit(f"[!] Country code {self.country} not in server list")
            else:
                self.save_config_file(server_index)
        except Exception as e:
            sys.exit("[!] Error: " + str(e))

    def openvpn(self):
        if not self.config_file_path:
            sys.exit("[!] No config file found. Unable to connect.")
        with open(os.devnull, "w") as fnull:
            openvpn_cmd = self.get_openvpn_command()
            subprocess.run(openvpn_cmd + ["--config", self.config_file_path, "--auth-user-pass", "password.txt"], stderr=fnull, input=f"{self.password}\n")

    @staticmethod
    def clean_up():
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)

    @staticmethod
    def get_openvpn_command():
        system_platform = platform.system()
        if system_platform == "Windows":
            return ["openvpn.exe"]
        elif system_platform in ["Linux", "Darwin"]:
            return ["openvpn"]
        else:
            raise Exception("Unsupported platform")

class AutoVpn4GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Welcome to AutoVPN4")
        self.setGeometry(100, 100, 400, 200)

        self.country_label = QLabel("Enter desired country code:", self)
        self.country_label.move(20, 20)

        self.country_input = QLineEdit(self)
        self.country_input.move(200, 20)

        self.password_label = QLabel("Enter VPN password:", self)
        self.password_label.move(20, 60)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.move(200, 60)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.move(150, 120)
        self.connect_button.clicked.connect(self.connect_vpn)

    def connect_vpn(self):
        country_code = self.country_input.text()
        password = self.password_input.text()
        vpn = AutoVpn4(country_code)
        vpn.password = password
        try:
            vpn.openvpn()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

def main():
    if not os.environ.get('USERPROFILE') and platform.system() == "Windows":
        sys.exit("[!] Please run the script from a user account, not a system account.")

    app = QApplication(sys.argv)
    window = AutoVpn4GUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
