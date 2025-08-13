import json
import socket
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import random
import threading
import time
import led_controller



app = Flask(__name__)
app.config['SECRET_KEY'] = 'simon_game_secret'

# Initialization SocketIO
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# level,light_duration_per_color,off_duration_between_colors
level_duration_list = [
    (1, 1, 0.5),
    (2, 1, 0.49),
    (3, 0.9, 0.48),
    (4, 0.9, 0.47),
    (5, 0.8, 0.46),
    (6, 0.8, 0.45),
    (7, 0.7, 0.44),
    (8, 0.7, 0.43),
    (9, 0.6, 0.42),
    (10, 0.6, 0.41),
    (11, 0.5, 0.40)
]

# ------------------ Multiplayer mode -------------------------
user_sessions = {}
rooms = {}
user_sids = {}  # { username: sid }


# Room structure example:
# rooms = {
#     "room1": {
#         "host": "player1",
#         "players": {
#             "player1": {"ready": False, "score": 0},
#             "player2": {"ready": False, "score": 0}
#         },
#         "game_active": False,
#         "current_level": 1,
#         "target_sequence": [],
#         "answers_received": {},  # { player: [sequence] }
#         "all_answered": False
#     }
# }
@socketio.on('connect')
def handle_connect():
    print("socket[connect]without data, Client connected", request.sid)


@socketio.on('register_user')
def handle_register_user(data):
    print("socket[register_user]with data:", data)
    username = data.get('username')
    if username:
        user_sids[username] = request.sid
        print(f"SID 注册成功: {username} -> {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print("socket[disconnect]without data,Client disconnected:", request.sid)
    # Search for the username corresponding to this sid
    for username, sid in user_sids.items():
        if sid == request.sid:
            print(f"将要删除用户 {username}")
            for room in list(rooms.keys()):
                if username in rooms[room]['players']:
                    del rooms[room]['players'][username]
                    # If it is the homeowner, update the homeowner or delete the empty room
                    if rooms[room]['host'] == username:
                        remaining = list(rooms[room]['players'].keys())
                        if remaining:
                            rooms[room]['host'] = remaining[0]
                        else:
                            del rooms[room]
                            print(f"已删除空房间: {room}")
                            break
                socketio.emit('update_players', {
                    'players': rooms[room]['players'],
                    'host': rooms[room]['host']
                })

            print(f"User {username} 已从所有房间中移除")
            user_sids.pop(username, None)
            break

# Join the room
@socketio.on('join_room')
def join_room(data):
    print("socket[join_room]with data:", data)
    username = data.get('username')
    room = data.get('room', 'default_room')

    print(f"{username} 加入 {room}")

    if room in rooms and rooms[room]['game_active']:
        # The game has started. Joining is not allowed
        socketio.emit('join_denied', {
            'message': '游戏已经开始，无法加入'
        }, to=request.sid)
        return

    if room not in rooms:
        rooms[room] = {
            'host': username,
            'players': {},
            'game_active': False,
            'current_level': 1,
            'target_sequence': [],
            'answers_received': {},
            'all_answered': False
        }

    rooms[room]['players'][username] = {'ready': False, 'score': 0}

    # Update room information
    socketio.emit('update_players', {
        'players': rooms[room]['players'],
        'host': rooms[room]['host']
    })

@socketio.on('set_ready')
def handle_set_ready(data):
    print("socket[set_ready]with data:", data)
    username = data['username']
    room = data['room']
    if room in rooms:
        room_data = rooms[room]
        if username in room_data['players']:
            room_data['players'][username]['ready'] = True

            socketio.emit('update_players', {
                'players': rooms[room]['players'],
                'host': rooms[room]['host']
            })


@socketio.on('start_game')
def handle_start_game(data):
    print("socket[start_game]with data:", data)
    time.sleep(1)
    room = data['room']
    if room in rooms:
        room_data = rooms[room]
        if room_data['host'] == data['username']:
            room_data['game_active'] = True
            room_data['current_level'] = 1
            room_data['target_sequence'] = game_state.generate_sequence(1)

            threading.Thread(target=simulate_raspberry_processing_multi, args=(room,room_data['current_level'], room_data['target_sequence'],)).start()

            socketio.emit('game_started', {
                'level': room_data['current_level'],
                'sequence': room_data['target_sequence']
            })


def update_user_score(room, username, score_change):
    """
    Update the score of the specified user and broadcast it to everyone in the room
    :param room: 
    :param username: 
    :param score_change: 
    """
    if room in rooms and username in rooms[room]['players']:
        rooms[room]['players'][username]['score'] += score_change
        socketio.emit('update_score', {
            'username': username,
            'score': rooms[room]['players'][username]['score']
        })


@socketio.on('submit_answer')
def handle_submit_answer(data):
    print("socket[submit_answer]with data:", data)
    username = data['username']
    room = data['room']
    answer = data['answer']

    if room in rooms:
        room_data = rooms[room]
        room_data['answers_received'][username] = answer

        if len(room_data['answers_received']) == len(room_data['players']):
            socketio.emit('write_messageBox', {
                'message': 'Observe the light!'
            })
            evaluate_all_answers(room)
        else:
            socketio.emit('write_messageBox', {
                'message': 'Waiting for other players...'
            }, to=request.sid)

def evaluate_all_answers(room):
    room_data = rooms[room]
    correct_sequence = room_data['target_sequence']

    for user, ans in room_data['answers_received'].items():
        if ans == correct_sequence:
            room_data['players'][user]['score'] += 10 + (room_data['current_level'] * 10)
            update_user_score(room, user, room_data['players'][user]['score'])
        else:
            pass

    room_data['current_level'] += 1
    room_data['answers_received'] = {}

    if room_data['current_level'] > 5:
        end_game(room)
    else:
        time.sleep(1)
        print("[evaluate_all_answers]进入第{0}关".format(room_data['current_level']))
        next_seq = game_state.generate_sequence(room_data['current_level'])
        room_data['target_sequence'] = next_seq
        threading.Thread(target=simulate_raspberry_processing_multi, args=(room,room_data['current_level'], next_seq,)).start()


def end_game(room):
    print("[end_game]游戏结束")
    room_data = rooms[room]
    socketio.emit('game_over', {
        'scores': {u: p['score'] for u, p in room_data['players'].items()}
    })

    if room in rooms:
        del rooms[room]




# Raspberry PI processing simulation
def simulate_raspberry_processing_multi(room, level, sequence):
    # Playback sequence
    led_controller.play_sequence(sequence, light_duration_per_color=level_duration_list[level-1][1], off_duration_between_colors=level_duration_list[level-1][2])

    # led_controller.play_sequence(sequence, light_duration_per_color=0.8, off_duration_between_colors=0.2)
    print(f"树莓派序列处理完成: {sequence}")
    if room not in rooms:
        print("[simulate_raspberry_processing_multi]房间不存在")
        return
    room_data = rooms[room]

    # Notify the front end: The Raspberry PI has completed the sequence display and can now start inputting
    notify_frontend({
        'status': 'ready_for_input',
        'level': room_data['current_level'],
        'sequence': sequence
    })



# -------------------------- Home Page --------------------------
@app.route('/mode_selection')
def mode_selection():
    return render_template('mode_selection.html')


@app.route('/api/save_username', methods=['POST'])
def save_username():
    data = request.json
    username = data.get('username')

    if not username or len(username.strip()) == 0:
        return jsonify({'error': '用户名不能为空'}), 400

    session['username'] = username
    user_sessions[username] = {'score': 0, 'level': 1}

    return jsonify({
        'status': 'success',
        'username': username
    })


@app.route('/api/select_mode', methods=['POST'])
def select_mode():
    data = request.json
    mode = data.get('mode')  # 'single' or 'multi'
    username = session.get('username', 'tourist')

    if not username or mode not in ['single', 'multi']:
        return jsonify({'error': 'Invalid input'}), 400

    session['player_name'] = username
    session['game_mode'] = mode

    return jsonify({
        'redirect': '/single' if mode == 'single' else '/multi',
        'username': username,
        'mode': mode
    })


@app.route('/single')
def single_player():
    username = session.get('username', 'tourist')
    return render_template('single.html', player_name=username, game_mode='single')


@app.route('/multi')
def multi_player():
    username = session.get('username', 'tourist')
    return render_template('multi.html', player_name=username, game_mode='multi')
    # return f"欢迎 {username} 进入【多人模式】页面！"

@app.route('/')
def index():
    return render_template('mode_selection.html')

# ---------------------------- Single-player mode ---------------------------------

class GameState:
    def __init__(self):
        self.current_level = 1
        self.target_sequence = []
        self.player_sequence = []
        self.player_score = 0
        self.game_active = False

    def generate_sequence(self, level=None):
        """Generate a new color sequence"""
        level = level or self.current_level
        colors = ['red', 'blue', 'green', 'yellow']
        seq_length = min(2 + level, 10) 
        self.target_sequence = random.choices(colors, k=seq_length)
        print("生成新序列:", self.target_sequence)
        self.player_sequence = []
        return self.target_sequence

    def reset_game(self):
        """Reset the game status"""
        self.current_level = 1
        self.player_score = 0   
        self.game_active = False
        self.target_sequence = []
        self.player_sequence = []

    def check_sequence(self, player_sequence):
        """Verify the player sequence and update the score"""
        print("对比玩家输入序列:", player_sequence)
        print("目标序列:", self.target_sequence)
        if player_sequence == self.target_sequence:
            # Calculate the score: base score + level bonus
            self.player_score += 10 + (self.current_level * 10)
            self.current_level += 1
            return True
        self.game_active = False
        return False

game_state = GameState()


# API endpoint implementation
@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game"""
    game_state.reset_game()
    game_state.game_active = True
    sequence = game_state.generate_sequence()

    time.sleep(1)

    # Simulate the processing thread of Raspberry PI
    threading.Thread(target=simulate_raspberry_processing, args=(game_state.current_level, sequence,)).start()

    return jsonify({
        'status': 'started',
        'level': game_state.current_level,
        'sequence': sequence,
        'score': game_state.player_score
    })


@app.route('/api/game/check', methods=['POST'])
def check_sequence():
    """Verify the sequence input by the player"""
    if not game_state.game_active:
        return jsonify({'error': 'Game not active'}), 400

    data = request.json
    player_sequence = data.get('playerSequence', [])

    if game_state.check_sequence(player_sequence):
        return jsonify({
            'result': 'correct',
            'score': game_state.player_score,
            'nextLevel': game_state.current_level
        })
    else:
        return jsonify({
            'result': 'incorrect',
            'final_score': game_state.player_score,
            'max_level': game_state.current_level - 1
        })


@app.route('/api/game/sequence', methods=['GET'])
def get_sequence():
    """Get the new sequence of the specified level"""
    time.sleep(1)

    level = request.args.get('level', type=int, default=game_state.current_level)
    sequence = game_state.generate_sequence(level)

    threading.Thread(target=simulate_raspberry_processing, args=(level, sequence,)).start()

    return jsonify({
        'sequence': sequence,
        'level': level
    })


@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    """Reset the game status"""
    game_state.reset_game()
    return jsonify({'status': 'reset', 'score': 0, 'level': 1})

def simulate_raspberry_processing(level, sequence):

    led_controller.play_sequence(sequence, light_duration_per_color=level_duration_list[level-1][1], off_duration_between_colors=level_duration_list[level-1][2])
    print(f"树莓派序列处理完成: {sequence}")

    notify_frontend({
        'status': 'ready_for_input',
        'level': game_state.current_level,
        'sequence': sequence
    })

def notify_frontend(message):
    """Send real-time notifications to the front end via WebSocket"""
    socketio.emit('game_update', message)
    print(f"已通过WebSocket发送通知到前端: {message}")


if __name__ == '__main__':
    # threading.Thread(target=start_socket_server, daemon=True).start()
    # app.run(host='0.0.0.0', port=5001, debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug = True, debug = True)
