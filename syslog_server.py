import paramiko, re
from config import SYSLOG_HOST, SYSLOG_USER, SYSLOG_PASSWORD, LOCAL_PORT
from jump_server import setup_jump_connection

KEYWORDS = ["error", "warning", "critical", "fail", "failed", "down", "unreachable",
            "timeout", "denied", "dropped", "authentication", "interface", "link",
            "overrun", "underrun", "congestion", "chassis", "memory", "cpu", "pfe", "nat"]

def connect_to_syslog_server(transport):
    try:
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

def execute_ls_command(username, password, path=''):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        syslog_client = connect_to_syslog_server(transport)
        if syslog_client is None:
            return "Failed to connect to syslog server."

        command = f'ls {path}'
        stdin, stdout, stderr = syslog_client.exec_command(command)
        ls_output = stdout.read().decode(errors='replace')
        ls_error = stderr.read().decode(errors='replace')

        syslog_client.close()
        jump_client.close()

        if ls_error:
            return f"Error: {ls_error}"

        return ls_output

    except Exception as e:
        return str(e)

def filter_logs(logs, filter_keywords):
    if not filter_keywords or all(not keyword.strip() for keyword in filter_keywords):
        return logs
    filtered_logs = ""
    for line in logs.split('\n'):
        if any(keyword.strip().lower() in line.lower() for keyword in filter_keywords if keyword.strip()):
            filtered_logs += line + "\n"
    return filtered_logs


def execute_cat_command(username, password, file_paths, filter_keywords, exclude_regex=None, chunk_size=4096):
    try:
        jump_client, transport = setup_jump_connection(username, password)
        if jump_client is None or transport is None:
            return "Failed to establish jump server connection."

        syslog_client = connect_to_syslog_server(transport)
        if syslog_client is None:
            return "Failed to connect to syslog server."

        logs_output = ""
        exclude_pattern = re.compile(exclude_regex) if exclude_regex else None

        for file_path in file_paths:
            command = f'cat {file_path}'
            stdin, stdout, stderr = syslog_client.exec_command(command)
            while True:
                chunk = stdout.read(chunk_size).decode(errors='replace')
                if not chunk:
                    break
                log_error = stderr.read().decode(errors='replace')
                if log_error:
                    return f"Error: {log_error}"

                # Apply exclusion regex
                if exclude_pattern:
                    chunk = "\n".join(line for line in chunk.splitlines() if not exclude_pattern.search(line))

                filtered_log_output = filter_logs(chunk, filter_keywords)
                logs_output += f"<h2><b>{file_path.split('/')[-1]}</b></h2><pre>{filtered_log_output}</pre><br>"

        syslog_client.close()
        jump_client.close()
        return logs_output

    except Exception as e:
        return str(e)



    except Exception as e:
        return str(e)
