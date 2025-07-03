# server.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

clients = {}  # sid: name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html', clients=clients)

@socketio.on('connect', namespace='/client')
def client_connect():
    sid = request.sid
    print(f"🟢 Client connected: {sid}")
    clients[sid] = f"Employee-{len(clients)+1}"
    socketio.emit('clients_update', clients, namespace='/admin')
@socketio.on('disconnect_client', namespace='/viewer')
def disconnect_client(data):
    sid = data.get('sid')
    print(f"🔌 Forcing stop_stream to {sid}")
    socketio.emit('stop_stream', {}, to=sid, namespace='/client')
@socketio.on('disconnect', namespace='/client')
def client_disconnect():
    sid = request.sid
    print(f"🔴 Client disconnected: {sid}")
    clients.pop(sid, None)
    socketio.emit('clients_update', clients, namespace='/admin')

@socketio.on('frame', namespace='/client')
def handle_frame(data):
    sid = request.sid
    emit('frame', {'sid': sid, 'image': data['image']}, broadcast=True, namespace='/viewer')

@socketio.on('connect', namespace='/viewer')
def viewer_connect():
    print("🖥️ Viewer connected")

@socketio.on('connect', namespace='/admin')
def admin_connect():
    print("🛠️ Admin connected")
    emit('clients_update', clients)

@socketio.on('trigger_stream', namespace='/admin')
def trigger_stream(data):
    sid = data['sid']
    print(f"📤 Triggering stream for {sid}")
    socketio.emit('start_stream', {}, to=sid, namespace='/client')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5005)
