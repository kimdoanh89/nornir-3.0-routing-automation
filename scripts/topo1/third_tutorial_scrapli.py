from scrapli.driver.core import IOSXEDriver


switch = {
    "host": "192.168.65.137",
    "auth_username": "admin",
    "auth_password": "admin",
    "auth_strict_key": False
}

cli = IOSXEDriver(**switch)
cli.open()
sh_int = cli.send_command("show interface")
print(sh_int.output)
