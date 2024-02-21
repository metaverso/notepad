import os

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///text.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret!')
db = SQLAlchemy(app)
socketio = SocketIO(app)


class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Text {self.path}>'


def setup_database(app):
    with app.app_context():
        db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>')
def secret_url(path):
    text_entry = Text.query.filter_by(path=path).first()
    text = text_entry.content if text_entry else ""
    return render_template('secret_url.html', text=text, path=path)

# Socket.IO events aqui

@socketio.on('join', namespace='/chat')
def on_join(data):
    room = data['room']
    join_room(room)
    text_entry = Text.query.filter_by(path=room).first()
    text = text_entry.content if text_entry else ""
    emit('text', {'text': text}, room=room)


@socketio.on('text change', namespace='/chat')
def on_text_change(data):
    room = data['room']
    text = data['text']
    text_entry = Text.query.filter_by(path=room).first()
    if text_entry:
        text_entry.content = text
    else:
        text_entry = Text(path=room, content=text)
        db.session.add(text_entry)
    db.session.commit()
    emit('update', {'text': text}, room=room)


@socketio.on('leave', namespace='/chat')
def on_leave(data):
    room = data['room']
    leave_room(room)


if __name__ == '__main__':
    setup_database(app)
    socketio.run(app, debug=True)
