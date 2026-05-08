from flask import Flask, render_template, request, redirect, session, url_for
import os
import requests

app = Flask(__name__)
# This secret key allows Flask to store "cookies" so it remembers who is logged in
app.secret_key = 'cloud_computing_lab_secret'

API_BASE = "http://34.58.84.64:5001/api/items"
API_LOGIN = "http://34.58.84.64:5001/api/login"
BACKEND_IP = os.getenv('BACKEND_IP', '34.58.84.64')


@app.route("/")
def show_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get status from the browser URL (e.g., /?status=Completed)
    status = request.args.get('status', 'All')
    user = session['username']

    # Pass the status to the VM API
    response = requests.get(
        f"http://{BACKEND_IP}:5001/api/items/{user}?status={status}")
    todolist = response.json()

    return render_template("index.html", todolist=todolist, current_status=status)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # Get password from the new HTML field
        password = request.form['password']

        # Prepare the data to send to the Backend API
        login_payload = {
            "username": username,
            "password": password
        }

        try:
            # Ask the Backend VM if these credentials are correct
            resp = requests.post(API_LOGIN, json=login_payload)

            if resp.status_code == 200:
                # Success! Save username in session and go to the list
                session['username'] = username
                return redirect(url_for('show_list'))
            else:
                # Unauthorized (401) or other error
                error_msg = "Invalid username or password."
                return render_template('login.html', error=error_msg)

        except Exception as e:
            return f"Frontend could not connect to Backend: {e}", 500

    return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/add", methods=['POST'])
def add_entry():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Collect data from the form
    new_task = {
        "user_id": session['username'],
        "what_to_do": request.form.get('name'),
        "description": request.form.get('description'),
        "category": request.form.get('category'),
        "due_date": request.form.get('date'),
        "time": request.form.get('time'),
        "priority": request.form.get('priority'),
        "fulfillment": 0,
        "status": "In Progress"
    }

    # Send it to the VM Backend to save in SQLite
    try:
        requests.post(f"http://{BACKEND_IP}:5001/api/add", json=new_task)
    except Exception as e:
        print(f"Error saving: {e}")

    return redirect(url_for('show_list'))


# Add these to your frontend_app.py in VS Code

@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    # Calls your backend DELETE route
    requests.delete(f"http://{BACKEND_IP}:5001/api/delete/{item_id}")
    return redirect(url_for('show_list'))


@app.route("/complete/<int:item_id>")
def complete_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    # Calls your backend POST route to update status
    requests.post(f"http://{BACKEND_IP}:5001/api/complete/{item_id}")
    return redirect(url_for('show_list'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
