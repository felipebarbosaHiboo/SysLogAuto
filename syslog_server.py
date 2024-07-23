# syslog_server.py

import paramiko
from config import SYSLOG_HOST, SYSLOG_USER, SYSLOG_PASSWORD, LOCAL_PORT
from jump_server import setup_jump_connection

KEYWORDS = ["error", "warning", "critical", "fail", "failed", "down", "unreachable",
            "timeout", "denied", "dropped", "authentication", "interface", "link",
            "overrun", "underrun", "congestion", "chassis", "memory", "cpu", "pfe", "nat"]

def connect_to_syslog_server(transport):
    try:
        # Connect to the syslog server through the jump server's transdef execute_cat_command(username, password, file_name, tail, filter_keywords):
        #     try:
        #         jump_client, transport = setup_jump_connection(username, password)
        #         if jump_client is None or transport is None:
        #             return "Failed to establish jump server connection."
        #
        #         syslog_client = connect_to_syslog_server(transport)
        #         if syslog_client is None:
        #             return "Failed to connect to syslog server."
        #
        #         if file_name == "all_logs":
        #             # Get the list of all files
        #             stdin, stdout, stderr = syslog_client.exec_command('ls /var/log/remote/*.log')
        #             files = stdout.read().decode(errors='replace').strip().split()
        #             logs_output = ""
        #             for file in files:
        #                 command = f'tail -n {tail} {file}'
        #                 stdin, stdout, stderr = syslog_client.exec_command(command)
        #                 log_output = stdout.read().decode(errors='replace')
        #                 log_error = stderr.read().decode(errors='replace')
        #                 if log_error:
        #                     log_output = f"Error: {log_error}"
        #                 device_name = file.split('/')[-1]
        #                 filtered_log_output = filter_logs(log_output, filter_keywords)
        #                 logs_output += f"<h2><b>{device_name}</b></h2><pre>{filtered_log_output}</pre><br>"
        #
        #         else:
        #             # Execute the 'cat' command with the specified number of lines (tail)
        #             command = f'tail -n {tail} /var/log/remote/{file_name}'
        #             stdin, stdout, stderr = syslog_client.exec_command(command)
        #             logs_output = stdout.read().decode(errors='replace')
        #             logs_error = stderr.read().decode(errors='replace')
        #
        #             if logs_error:
        #                 logs_output = f"Error: {logs_error}"
        #             else:
        #                 logs_output = f"<pre>{filter_logs(logs_output, filter_keywords)}</pre>"
        #
        #         # Close the connections
        #         syslog_client.close()
        #         jump_client.close()
        #         print("Connection to syslog server closed")
        #
        #         return logs_output
        #
        #     except Exception as e:
        #         return str(e)
        #
        # def filter_logs(logs, filter_keywords):
        #     filtered_logs = ""
        #     for line in logs.split('\n'):
        #         if any(keyword.strip().lower() in line.lower() for keyword in filter_keywords if keyword.strip()):
        #             filtered_logs += line + "\n"
        #     return filtered_logsport
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
        ls_output = stdout.read().decode(errors='replace')
        ls_error = stderr.read().decode(errors='replace')

        # Close the connections
        syslog_client.close()
        jump_client.close()
        print("Connection to syslog server closed")

        if ls_error:
            return f"Error: {ls_error}"

        return ls_output

    except Exception as e:
        return str(e)

def filter_logs(logs):
    filtered_logs = ""
    for line in logs.split('\n'):
        if any(keyword in line.lower() for keyword in KEYWORDS):
            filtered_logs += line + "\n"
    return filtered_logs

def execute_cat_command(username, password, file_name, tail, filter_keywords):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        syslog_client = connect_to_syslog_server(transport)
        if syslog_client is None:
            return "Failed to connect to syslog server."

        if file_name == "all_logs":
            # Get the list of all files
            stdin, stdout, stderr = syslog_client.exec_command('ls /var/log/remote/*.log')
            files = stdout.read().decode(errors='replace').strip().split()
            logs_output = ""
            for file in files:
                command = f'tail -n {tail} {file}'
                stdin, stdout, stderr = syslog_client.exec_command(command)
                log_output = stdout.read().decode(errors='replace')
                log_error = stderr.read().decode(errors='replace')
                if log_error:
                    log_output = f"Error: {log_error}"
                device_name = file.split('/')[-1]
                filtered_log_output = filter_logs(log_output, filter_keywords)
                logs_output += f"<h2><b>{device_name}</b></h2><pre>{filtered_log_output}</pre><br>"

        else:
            # Execute the 'cat' command with the specified number of lines (tail)
            command = f'tail -n {tail} /var/log/remote/{file_name}'
            stdin, stdout, stderr = syslog_client.exec_command(command)
            logs_output = stdout.read().decode(errors='replace')
            logs_error = stderr.read().decode(errors='replace')

            if logs_error:
                logs_output = f"Error: {logs_error}"
            else:
                logs_output = f"<pre>{filter_logs(logs_output, filter_keywords)}</pre>"

        # Close the connections
        syslog_client.close()
        jump_client.close()
        print("Connection to syslog server closed")

        return logs_output

    except Exception as e:
        return str(e)

def filter_logs(logs, filter_keywords):
    if not filter_keywords or all(not keyword.strip() for keyword in filter_keywords):
        # If no keywords are provided, return the original logs
        return logs
    filtered_logs = ""
    for line in logs.split('\n'):
        if any(keyword.strip().lower() in line.lower() for keyword in filter_keywords if keyword.strip()):
            filtered_logs += line + "\n"
    return filtered_logs


