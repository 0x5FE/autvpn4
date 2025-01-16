- AutoVPN4 is a Python script for automating VPN connections using OpenVPN and [VPN Gate servers](https://www.vpngate.net). 
- An idea similar to to [autovpn2](https://github.com/ruped24/autovpn2) With some improvements.

![tela_01](https://github.com/user-attachments/assets/c418b2d2-ce6f-4049-bc92-9599819b27ca)
![tela_02](https://github.com/user-attachments/assets/1d34b93a-626b-4e74-834f-f42abbf699a0)


# Main Features:

- Automatically selects and connects to a VPN server based on the country code provided.

- the interface is intuitive and supports multiple languages ​​(English and Portuguese).

- Allows for language customization and the inclusion of optional SSL certificates.

- Checks for the availability of new versions of the application.

- Uses Fernet encryption to protect passwords and sensitive data.

# Installation

    git clone https://github.com/mrfelpa/autovpn4.git

Navigate to the project directory:

        cd autvpn4

# Install Dependencies

    pip install -r requirements.txt
    
# Setting up OpenVPN:

- On Windows, download and install OpenVPN from the official website.

- On Linux, install via package manager:

        sudo apt-get install openvpn

# Additional Settings:

- The ***config.ini*** file allows you to customize the VPN Gate API URL and other default settings.
- To add support for new languages, edit the LANGUAGES dictionary in the source code.
