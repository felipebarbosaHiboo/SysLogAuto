# syslog_server.py

import paramiko
from config import SYSLOG_HOST, SYSLOG_USER, SYSLOG_PASSWORD, LOCAL_PORT
from jump_server import setup_jump_connection

def connect_to_syslog_server(transport):
    try:
        # Connect to the syslog server through the jump server's transport
        syslog_client = paramiko.SSHClient()
        syslog_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        syslog_client.connect(
            SYSLOG_HOST,
            username=SYSLOG_USER,
            password=SYSLOG_PASSWORD,
            sock=transport.open_channel('direct-tcpip', (SYSLOG_HOST, 22), ('127.0.0.1', LOCAL_PORT))
        )
        print("Connected to syslog server")
        return syslog_client
    except Exception as e:
        print(f"Failed to connect to syslog server: {e}")
        return None

def execute_ls_command(username, password):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        syslog_client = connect_to_syslog_server(transport)
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

        syslog_client = connect_to_syslog_server(transport)
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
