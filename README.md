AutoVPN4 is a Python script for automating VPN connections using OpenVPN and [VPN Gate servers](https://www.vpngate.net). 

An idea similar to to [autovpn2](https://github.com/ruped24/autovpn2) With some improvements.


# Prerequisites

Before you begin, ensure you have met the following requirements:

    Python 3.x is installed on your system.


You can directly download the script or Clone this repository to your local machine using the following command:

    git clone https://github.com/0x5FE/autvpn4.git


# Install Dependencies

Navigate to the project directory:

    cd autvpn4

    
Install the required dependencies using pip:

    pip install -r requirements.txt



# Basic Usage

To connect to a VPN server in the US (default) with a password prompt:

    python autvpn4.py

You will be prompted to enter the desired country code and VPN password.


# Advanced Usage

***AutoVPN4*** supports more advanced options. For example, you can specify a country code and provide the password directly:

    python autvpn4.py --country JP --password YourPassword123


# Options and Parameters

***AutoVPN4*** accepts the following command-line options and parameters:

    --country: Specify the desired country code (default is "US").
    --password: Provide the VPN password directly (useful for automation).

***AutoVPN4*** does not require additional configuration files. However, you may customize the script behavior by modifying the source code directly.


# You can customize this documentation further based on your specific project details and requirements.



![aut interface](https://github.com/0x5FE/autvpn4/assets/65371336/5a7f9069-086a-43e2-a800-ebc45f0122eb)


