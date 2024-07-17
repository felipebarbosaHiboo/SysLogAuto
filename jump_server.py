# jump_server.py

import paramiko
import time
from config import JUMP_HOST, JUMP_PORT, LOCAL_PORT

def setup_jump_connection(username, password):
    try:
        # Connect to the jump server
        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_client.connect(JUMP_HOST, port=JUMP_PORT, username=username, password=password)

        # Get the underlying transport
        transport = jump_client.get_transport()

        # Request local port forwarding
        transport.request_port_forward('', LOCAL_PORT)

        # Wait briefly to ensure the tunnel is established
        time.sleep(2)

        return jump_client, transport
    except Exception as e:
        print(f"Failed to connect to jump server: {e}")
        return None, None
