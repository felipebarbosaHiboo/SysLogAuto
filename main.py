import paramiko
import socks
import socket
import threading
import select
import time

# Define the jump server details
jump_host = 'jump.hiboonetworks.com'
jump_port = 4422
jump_user = 'felipebarbosa'
jump_password = 'dota-1LUNA-mouse'

# Define the syslog server details
syslog_host = 'sftp.int.hiboonetworks.com'
syslog_user = 'hiboo-readonly'
syslog_password = 'syslogtesting'

# Local port for SOCKS5 proxy
local_port = 9999

def forward_tunnel(local_port, remote_host, remote_port, transport):
    """
    Sets up a forward tunnel (SOCKS5 proxy).
    """
    transport.request_port_forward('', local_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remote_host, remote_port))
        thr.setDaemon(True)
        thr.start()

def handler(chan, host, port):
    """
    Handles the incoming requests and forwards them to the destination.
    """
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f'Forwarding request to {host}:{port} failed: {e}')
        return

    while True:
        r, w, x = select.select([chan, sock], [], [])
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)

    chan.close()
    sock.close()

# Connect to the jump server
jump_client = paramiko.SSHClient()
jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
jump_client.connect(jump_host, port=jump_port, username=jump_user, password=jump_password)

# Get the underlying transport
transport = jump_client.get_transport()

# Set up dynamic port forwarding (SOCKS5 proxy) on local port 9999
threading.Thread(target=forward_tunnel, args=(local_port, syslog_host, 22, transport)).start()
print(f"SOCKS5 proxy running on local port {local_port}")

# Allow some time for the tunnel to be established
time.sleep(2)

# Set up a SOCKS5 proxy with the local port
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", local_port)
socket.socket = socks.socksocket

# Connect to the syslog server through the SOCKS5 proxy
syslog_client = paramiko.SSHClient()
syslog_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
syslog_client.connect(syslog_host, username=syslog_user, password=syslog_password)

print("Connected to syslog server")

# Execute the 'ls -l' command in the /var/log/remote/ directory
stdin, stdout, stderr = syslog_client.exec_command('ls -l /var/log/remote/')
print("Output of 'ls -l /var/log/remote/' command:")
print(stdout.read().decode())
print(stderr.read().decode())

# Close the connections
syslog_client.close()
jump_client.close()
print("Connection to syslog server closed")
