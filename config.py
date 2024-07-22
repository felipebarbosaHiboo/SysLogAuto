# config.py

# Define the jump server details
JUMP_HOST = 'jump.hiboonetworks.com'
JUMP_PORT = 4422

# Define the syslog server details
SYSLOG_HOST = 'sftp.int.hiboonetworks.com'
SYSLOG_USER = 'hiboo-readonly'
SYSLOG_PASSWORD = 'syslogtesting'

# Local port for SOCKS5 proxy
LOCAL_PORT = 9999

# List of devices
DEVICES = [
    {'name': 'hib-dc01-rtr-core-01-mx304', 'ip': '10.11.0.11'},
    {'name': 'hib-dc01-rtr-edge-01-acx5448', 'ip': '10.11.0.21'},
    {'name': 'Device3', 'ip': '192.168.1.3'}
]
