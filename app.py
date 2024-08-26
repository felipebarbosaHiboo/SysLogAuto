from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from syslog_server import execute_ls_command, execute_cat_command

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a random secret key


@app.route('/get_dates', methods=['GET'])
def get_dates():
    directory = request.args.get('directory')
    username = session['username']
    password = session['password']

    dates = []
    if directory:
        dir_ls_output = execute_ls_command(username, password, f'/var/log/remote/{directory}')
        if not dir_ls_output.startswith("Error"):
            files = dir_ls_output.split()
            dates = [file.split('.')[0] for file in files if file.endswith('.log')]
            dates = sorted(dates)  # Sort the dates

    return jsonify(dates=dates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        session['username'] = username
        session['password'] = password
        ls_output = execute_ls_command(username, password)

        if "Failed" in ls_output:
            return render_template('login.html', error="Invalid credentials or connection issue.")

        return render_template('loading.html')
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('login'))

    username = session['username']
    password = session['password']

    directories = []
    ls_output = execute_ls_command(username, password, '/var/log/remote')
    if not ls_output.startswith("Error"):
        directories = ls_output.split()

    selected_files = []
    selected_file_content = ""

    if request.method == 'POST':
        selected_directory = request.form.get('directory')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        filter_keywords = request.form.get('filter', '').split(',')
        exclude_regex = request.form.get('exclude_regex')

        # Fetch files within the date range for the selected device
        file_paths = []
        dir_ls_output = execute_ls_command(username, password, f'/var/log/remote/{selected_directory}')
        if not dir_ls_output.startswith("Error"):
            files = dir_ls_output.split()
            available_dates = [file.split('.')[0] for file in files if file.endswith('.log')]

            # Filter files based on the selected date range
            file_paths = [f'/var/log/remote/{selected_directory}/{file}.log' for file in available_dates if start_date <= file <= end_date]

            # Fetch and filter the logs with exclude regex
            selected_file_content = execute_cat_command(username, password, file_paths, filter_keywords, exclude_regex)

    return render_template('index.html', directories=directories, selected_file_content=selected_file_content)


if __name__ == '__main__':
    app.run(debug=True)
