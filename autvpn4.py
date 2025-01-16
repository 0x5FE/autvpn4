import os
import subprocess
import requests
import base64
import tempfile
import sys
import shutil
import platform
import logging
import configparser
import threading
from cryptography.fernet import Fernet
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config

Config.set('graphics', 'resizable', False)
Window.size = (600, 400)

logging.basicConfig(
    filename='autovpn4.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

config = configparser.ConfigParser()
config.read('config.ini')

VPN_GATE_API_URL = config.get('DEFAULT', 'VPN_GATE_API_URL', fallback="https://www.vpngate.net/api/iphone/")
TEMP_DIR = tempfile.mkdtemp()

KEY = Fernet.generate_key()
cipher_suite = Fernet(KEY)

LANGUAGES = {
    "en": {
        "title": "AutoVPN4",
        "country_label": "Enter desired country code (e.g., US):",
        "password_label": "Enter VPN password (min 8 characters):",
        "connect_button": "Connect",
        "status_connected": "Connected",
        "status_disconnected": "Disconnected",
        "error_invalid_country": "Invalid country code. Use a 2-letter code (e.g., US).",
        "error_short_password": "Password must be at least 8 characters long.",
        "settings_button": "Settings",
        "back_button": "Back to Main",
        "language_label": "Language:",
        "ssl_cert_label": "SSL Certificate (optional):",
        "update_button": "Check for Updates",
    },
    "pt": {
        "title": "AutoVPN4",
        "country_label": "Digite o código do país desejado (ex., BR):",
        "password_label": "Digite a senha da VPN (mínimo 8 caracteres):",
        "connect_button": "Conectar",
        "status_connected": "Conectado",
        "status_disconnected": "Desconectado",
        "error_invalid_country": "Código do país inválido. Use um código de 2 letras (ex., BR).",
        "error_short_password": "A senha deve ter pelo menos 8 caracteres.",
        "settings_button": "Configurações",
        "back_button": "Voltar ao Principal",
        "language_label": "Idioma:",
        "ssl_cert_label": "Certificado SSL (opcional):",
        "update_button": "Verificar Atualizações",
    },
}

class AutoVpn4:
    def __init__(self, country="US"):
        self.country = country.upper()
        self.servers = []
        self.password = None
        self.config_file_path = None
        self.get_server_list()

    def save_config_file(self, server_index):
        logging.info("Writing config file")
        try:
            server_data = base64.b64decode(self.servers[server_index + 8]).decode("utf-8")
            config_file_path = os.path.join(TEMP_DIR, "config.ovpn")
            with open(config_file_path, "w") as config_file:
                config_file.write(server_data)
            self.config_file_path = config_file_path
        except Exception as e:
            logging.error(f"Failed to create config file: {e}")
            raise

    def get_server_list(self):
        if not self.country or len(self.country) != 2:
            raise ValueError("Invalid country code. Use a 2-letter code (e.g., US).")

        logging.info(f"Looking for servers in {self.country}")
        try:
            response = requests.get(VPN_GATE_API_URL, verify=True)  
            server_list = response.text.split(",")
            self.servers.extend([x for x in server_list if len(x) > 15])
            try:
                server_index = self.servers.index(self.country)
            except ValueError:
                raise ValueError(f"Country code {self.country} not in server list")
            else:
                self.save_config_file(server_index)
        except Exception as e:
            logging.error(f"Error fetching server list: {e}")
            raise

    def openvpn(self):
        if not self.config_file_path:
            raise FileNotFoundError("No config file found. Unable to connect.")
        try:
            with open(os.devnull, "w") as fnull:
                openvpn_cmd = self.get_openvpn_command()
                subprocess.run(
                    openvpn_cmd + ["--config", self.config_file_path, "--auth-user-pass", "password.txt"],
                    stderr=fnull,
                    input=f"{self.password}\n".encode()
                )
        except Exception as e:
            logging.error(f"Error connecting to VPN: {e}")
            raise

    @staticmethod
    def clean_up():
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            logging.info("Temporary files cleaned up.")

    @staticmethod
    def get_openvpn_command():
        system_platform = platform.system()
        if system_platform == "Windows":
            return ["openvpn.exe"]
        elif system_platform in ["Linux", "Darwin"]:
            return ["openvpn"]
        else:
            raise Exception("Unsupported platform")

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = LANGUAGES["en"]  # Idioma padrão
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        self.country_label = Label(text=self.language['country_label'])
        layout.add_widget(self.country_label)

        self.country_input = TextInput(multiline=False)
        layout.add_widget(self.country_input)

        self.password_label = Label(text=self.language['password_label'])
        layout.add_widget(self.password_label)

        self.password_input = TextInput(multiline=False, password=True)
        layout.add_widget(self.password_input)

        self.connect_button = Button(text=self.language['connect_button'])
        self.connect_button.bind(on_press=self.connect_vpn)
        layout.add_widget(self.connect_button)

        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        self.progress_bar.opacity = 0  # Inicialmente invisível
        layout.add_widget(self.progress_bar)

        self.settings_button = Button(text=self.language['settings_button'])
        self.settings_button.bind(on_press=self.go_to_settings)
        layout.add_widget(self.settings_button)

        self.add_widget(layout)

    def go_to_settings(self, instance):
        self.manager.current = 'settings'

    def update_ui(self):
        self.country_label.text = self.language['country_label']
        self.password_label.text = self.language['password_label']
        self.connect_button.text = self.language['connect_button']
        self.settings_button.text = self.language['settings_button']

    def connect_vpn(self, instance):
        country_code = self.country_input.text.strip()
        password = self.password_input.text.strip()

        if not country_code or len(country_code) != 2:
            self.show_error_popup(self.language["error_invalid_country"])
            return

        if len(password) < 8:
            self.show_error_popup(self.language["error_short_password"])
            return

        self.progress_bar.opacity = 1  
        self.connect_button.disabled = True  

        try:
            vpn = AutoVpn4(country_code)
            vpn.password = password
            threading.Thread(target=self.run_vpn, args=(vpn,)).start()  
        except Exception as e:
            self.show_error_popup(str(e))
            self.reset_ui()

    def run_vpn(self, vpn):
        try:
            vpn.openvpn()
            self.show_success_popup(self.language["status_connected"])
        except Exception as e:
            self.show_error_popup(str(e))
        finally:
            vpn.clean_up()
            self.reset_ui()

    def reset_ui(self):
        self.progress_bar.opacity = 0
        self.connect_button.disabled = False

    def show_error_popup(self, message):
        popup = Popup(title='Error', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def show_success_popup(self, message):
        popup = Popup(title='Success', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)

        self.language_label = Label(text=LANGUAGES["en"]['language_label'])
        layout.add_widget(self.language_label)

        self.language_spinner = Spinner(text="English", values=["English", "Português"])
        self.language_spinner.bind(text=self.change_language)
        layout.add_widget(self.language_spinner)

        self.ssl_cert_label = Label(text=LANGUAGES["en"]['ssl_cert_label'])
        layout.add_widget(self.ssl_cert_label)

        self.ssl_cert_input = TextInput(multiline=False, hint_text="Path to SSL certificate")
        layout.add_widget(self.ssl_cert_input)

        self.update_button = Button(text=LANGUAGES["en"]['update_button'])
        self.update_button.bind(on_press=self.check_for_updates)
        layout.add_widget(self.update_button)

        self.back_button = Button(text=LANGUAGES["en"]['back_button'])
        self.back_button.bind(on_press=self.go_to_main)
        layout.add_widget(self.back_button)

        self.add_widget(layout)

    def change_language(self, spinner, text):
        main_screen = self.manager.get_screen('main')
        if text == "English":
            main_screen.language = LANGUAGES["en"]
        elif text == "Português":
            main_screen.language = LANGUAGES["pt"]
        main_screen.update_ui()

    def check_for_updates(self, instance):
        try:
            response = requests.get("https://api.github.com/repos/mrfelpa/autovpn4/releases/latest")
            latest_version = response.json()["tag_name"]
            current_version = "1.0.0"  
            if latest_version != current_version:
                self.show_update_popup(f"New version {latest_version} available!")
            else:
                self.show_update_popup("You are using the latest version.")
        except Exception as e:
            self.show_update_popup(f"Error checking for updates: {e}")

    def show_update_popup(self, message):
        popup = Popup(title='Update', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def go_to_main(self, instance):
        self.manager.current = 'main'

class AutoVpn4App(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

def main():
    if not os.environ.get('USERPROFILE') and platform.system() == "Windows":
        sys.exit("[!] Please run the script from a user account, not a system account.")

    AutoVpn4App().run()

if __name__ == "__main__":
    main()
