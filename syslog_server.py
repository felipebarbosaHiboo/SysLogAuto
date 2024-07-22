# syslog_server.py

import paramiko
from config import SYSLOG_HOST, SYSLOG_USER, SYSLOG_PASSWORD, LOCAL_PORT, DEVICES
from jump_server import setup_jump_connection

def connect_to_server(host, username, password, transport):
    try:
        # Connect to the specified server through the jump server's transport
        server_client = paramiko.SSHClient()
        server_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        server_client.connect(
            host,
            username=username,
            password=password,
            sock=transport.open_channel('direct-tcpip', (host, 22), ('127.0.0.1', LOCAL_PORT))
        )
        print(f"Connected to {host}")
        return server_client
    except Exception as e:
        print(f"Failed to connect to {host}: {e}")
        return None

def execute_ls_command(username, password):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        syslog_client = connect_to_server(SYSLOG_HOST, SYSLOG_USER, SYSLOG_PASSWORD, transport)
        if syslog_client is None:
            return "Failed to connect to syslog server."

        # Execute the 'ls -l' command in the /var/log/remote/ directory
        stdin, stdout, stderr = syslog_client.exec_command('ls -l /var/log/remote/')
        ls_output = stdout.read().decode()
        ls_error = stderr.read().decode()

        # Close the connections
        syslog_client.close()
        jump_client.close()
        print("Connection to syslog server closed")

        if ls_error:
            return f"Error: {ls_error}"

        return ls_output

    except Exception as e:
        return str(e)

def execute_cat_command(username, password, file_name):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        syslog_client = connect_to_server(SYSLOG_HOST, SYSLOG_USER, SYSLOG_PASSWORD, transport)
        if syslog_client is None:
            return "Failed to connect to syslog server."

        # Execute the 'cat' command with tail 100 on the specified log file
        command = f'tail -n 100 /var/log/remote/{file_name}'
        stdin, stdout, stderr = syslog_client.exec_command(command)
        cat_output = stdout.read().decode()
        cat_error = stderr.read().decode()

        # Close the connections
        syslog_client.close()
        jump_client.close()
        print("Connection to syslog server closed")

        if cat_error:
            return f"Error: {cat_error}"

        return cat_output

    except Exception as e:
        return str(e)

def execute_show_interfaces_terse(username, password, device_ip):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        device_client = connect_to_server(device_ip, username, password, transport)
        if device_client is None:
            return "Failed to connect to device."

        # Execute the 'show interfaces terse' command on the specified device
        stdin, stdout, stderr = device_client.exec_command('show system users')
        stdin, stdout, stderr = device_client.exec_command('show interfaces terse')
        terse_output = stdout.read().decode()
        terse_error = stderr.read().decode()

        # Close the connections
        device_client.close()
        jump_client.close()
        print("Connection to device closed")

        if terse_error:
            return f"Error: {terse_error}"

        return terse_output

    except Exception as e:
        return str(e)
