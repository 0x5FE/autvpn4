*Similar idea to [autovpn2](https://github.com/ruped24/autovpn2) with some modifications like:*

> --script-security 2, --up up.bat, and --down down.bat. to perform additional actions, such as clearing DNS caches.

 > urllib3.disable_warnings() to suppress SSL warnings when making requests.

Although testing was done on Windows, you can test it on another operating system, platform specific behavior is managed using **platform method**

Remember to replace "openvpn.exe" with the actual OpenVPN executable path on your operating system.

Also remember to install built-in libraries such as the tempfile subprocess as they help ensure cross-platform compatibility.

Make sure dependencies like the requests library and the openvpn utility are installed in your environment for the script to work correctly.

***PS: You need to create up.bat and down.bat files in the same directory as your script. These files can contain commands to clear DNS caches or perform any other action***

![Sem título](https://github.com/0x5FE/autvpn4/assets/65371336/34063a8a-5f7d-4ab1-8087-f0c144a4b4af)
