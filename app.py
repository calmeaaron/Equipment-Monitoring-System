import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
socketio = SocketIO(app, cors_allowed_origins="*")

master_inventory = {}
activity_logs = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    if not data:
        return {"status": "error", "message": "No data"}, 400

    if 'status' in data:
        master_inventory[data['id']] = data
        socketio.emit('status_change', data)

    if 'msg' in data:
        activity_logs.insert(0, data)
        socketio.emit('log_event', data)

    return {"status": "success"}, 200


@app.route('/clear')
def clear():
    global master_inventory, activity_logs
    master_inventory = {}
    activity_logs = []
    socketio.emit('clear_all', {})
    return "<h1>System Cleared</h1><a href='/'>Go Back</a>"


@socketio.on('connect')
def handle_connect():
    for item in master_inventory.values():
        emit('status_change', item)
    for log in reversed(activity_logs):
        emit('log_event', log)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)