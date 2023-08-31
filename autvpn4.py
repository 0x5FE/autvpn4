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

class AutoVpn4:
    def __init__(self, country="US"):
        self.country = country.upper()
        self.servers = []
        self.get_server_list()

    def save_config_file(self, server_index):
        print("[autovpn4] writing config file")
        try:
            server_data = base64.b64decode(self.servers[server_index + 8]).decode("utf-8")
            temp_dir = tempfile.mkdtemp()
            config_file_path = os.path.join(temp_dir, "config.ovpn")
            with open(config_file_path, "w") as config_file:
                config_file.write(server_data)
            return config_file_path
        except Exception as e:
            print("[autovpn4] failed to create config file:", e)
            return None

    def get_server_list(self):
        if not self.country:
            self.country = "US"
        print("[autovpn4] looking for", self.country)

        try:
            urllib3.disable_warnings()
            response = requests.get("https://www.vpngate.net/api/iphone/", verify=False)
            server_list = response.text.split(",")
            self.servers.extend([x for x in server_list if len(x) > 15])
            try:
                server_index = self.servers.index(self.country)
            except ValueError:
                exit(f"[!] Country code {self.country} not in server list")
            else:
                config_file_path = self.save_config_file(server_index)
                if config_file_path:
                    self.openvpn(config_file_path)
        except Exception as e:
            exit("[!] Error: " + str(e))

    def openvpn(self, config_file_path):
        with open(os.devnull, "w") as fnull:
            openvpn_cmd = self.get_openvpn_command()
            subprocess.run(openvpn_cmd + ["--config", config_file_path], stderr=fnull)

    @staticmethod
    def clean_up(temp_dir):
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @staticmethod
    def get_openvpn_command():
        system_platform = platform.system()
        if system_platform == "Windows":
            return ["openvpn.exe"]
        elif system_platform in ["Linux", "Darwin"]:
            return ["openvpn"]
        else:
            raise Exception("Unsupported platform")

def main():
    if not os.environ.get('USERPROFILE') and platform.system() == "Windows":
        sys.exit("[!] Please run the script from a user account, not a system account.")

    try:
        print("\033[96m\n[autovpn4] getting server list")
        print("[autovpn4] parsing response")
        country_code = input("Enter desired country code: ")
        AutoVpn4(country_code)
    except KeyboardInterrupt:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "C:\path\to\open\download\openvpn.exe"])
        else:
            subprocess.run(["pkill", "openvpn"])
            subprocess.run(["clear"])
        temp_dir = tempfile.mkdtemp()
        AutoVpn4.clean_up(temp_dir)
        retry = ("y", "yes")
        try:
            ans = input("\033[92m\n[autovpn4]\033[93m Try another VPN? (y/n)\033[0m \033[92m")
            if ans.lower() in retry:
                try:
                    servers = ("JP", "KR")
                    AutoVpn4(random.choice(servers))
                except:
                    AutoVpn4.clean_up(temp_dir)
        except:
            pass

if __name__ == "__main__":
    main()
