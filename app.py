# app.py

from flask import Flask, render_template, request, redirect, url_for, session
from syslog_server import execute_ls_command, execute_cat_command, execute_show_interfaces_terse
from config import DEVICES

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a random secret key


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate the credentials
        session['username'] = username
        session['password'] = password
        ls_output = execute_ls_command(username, password)

        if "Failed" in ls_output:
            return render_template('login.html', error="Invalid credentials or connection issue.")

        return render_template('loading.html')
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('login'))

    username = session['username']
    password = session['password']
    ls_output = execute_ls_command(username, password)
    files = []

    if not ls_output.startswith("Error"):
        # Parse the ls output to get a list of files
        lines = ls_output.split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) > 8:
                files.append(parts[8])

    selected_file_content = ""
    service_request_output = ""
    if request.method == 'POST':
        selected_file = request.form.get('file')
        if selected_file:
            selected_file_content = execute_cat_command(username, password, selected_file)

        if 'service_request' in request.form:
            device_ip = request.form['device_ip']
            service_request_output = execute_show_interfaces_terse(username, password, device_ip)

    return render_template('index.html', files=files, selected_file_content=selected_file_content,
                           service_request_output=service_request_output, devices=DEVICES)


if __name__ == '__main__':
    app.run(debug=True)
