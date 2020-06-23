from flask import flash, render_template, url_for, request, json, jsonify, make_response, redirect
from flask_login import login_user, logout_user, current_user, login_required
from game import app, db, bcrypt
from game.forms import RegistrationForm, LoginForm, NewGameForm
from game.game import GameOfLife, GameSettings, GameState
from game.models import User, Game
from time import sleep
import random

@app.route("/")
@app.route("/home")
def main():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {form.username.data}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('lobby'))
        else:
            flash(f'Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route("/lobby")
@login_required
def lobby():
    open_games = Game.query.filter(Game.status!=-1)
    own_games = Game.query.filter(((Game.first_player_id==current_user.id)|(Game.second_player_id==current_user.id))&(Game.status!=-1))
    return render_template('lobby.html', open_games=open_games, own_games=own_games)

@app.route("/new", methods=['GET','POST'])
@login_required
def new():
    form = NewGameForm()
    if request.method == 'POST' and form.validate_on_submit():
        game_settings = GameSettings(generations_per_round=form.generations_per_round.data,
                                     rounds_number=form.rounds_number.data,
                                     new_cells_per_round=form.new_cells_per_round.data)
        game = GameOfLife(settings=game_settings)
        game_db = Game(first_player_id=current_user.id,
                        settings=game_settings.ToJSON(),
                        state=game._GameOfLife__state.ToJSON())
        db.session.add(game_db)
        db.session.commit()
        return redirect('/game/%d' % game_db.id)
    return render_template('new_game.html', form=form)

@app.route("/game/<id>", methods=['GET','POST'])
@login_required
def game(id):
    game_db = Game.query.filter_by(id=id).first()
    if game_db == None:
        flash(f'This game does not exist', 'danger')
        return redirect(url_for('lobby'))
    
    game = getGameFromEntry(game_db)
    if current_user.id == game_db.first_player_id:
        player_num = 1
    elif current_user.id == game_db.second_player_id:
        player_num = 2
    else:
        player_num = 0

    if request.method == 'GET':
        player_1 = User.query.filter_by(id=game_db.first_player_id).first().username
        if player_num == 0 and game_db.second_player_id is None:
            game_db.second_player_id = current_user.id
            game_db.status = 1
            db.session.commit()
            player_2 = current_user.username
        elif game_db.second_player_id == None:
            player_2 = 'None'
        else:
            player_2 = User.query.filter_by(id=game_db.second_player_id).first()
            player_2 = player_2.username if player_2 else 'None'
        gameboard_class = '_mod-addcell' if game.GetNextAction(player_num) == 'add_cell' else ''
        return render_template('game.html',
                                player_1=player_1,
                                player_2=player_2,
                                grid=json.loads(game_db.state)['grid'],
                                status=game.Status,
                                gameboard_class=gameboard_class)
    
    req = request.get_json()
    if player_num == 0:
        req['action'] = 'get_state'
    response = {}

    if req['action'] == 'check_p2':
        if game_db.second_player_id != None:
            response['p2_ingame'] = True
            response['p2_name'] = User.query.filter_by(id=game_db.second_player_id).first().username
        else:
            response['p2_ingame'] = False
    elif req['action'] == 'add_cell':
        if current_user.id != game_db.first_player_id and current_user.id != game_db.second_player_id:
            return make_response(jsonify({'error': True, 'message': 'Not a player, you are'}), 200)
        if not ('cell_x' in req and 'cell_y' in req):
            return make_response(jsonify({'error': True, 'message': 'Not provided, cell coordinates are'}), 200)
        
        if game.AddCell(req['cell_x'], req['cell_y'], player_num):
            game_db.state = game._GameOfLife__state.ToJSON()
            db.session.commit()
            response['cell_class'] = 'cell-p{}'.format(player_num)
            response['counts_class'] = '_p{}_counts'.format(player_num)
            response['next_action'] = game.GetNextAction(player_num)
            response['status'] = game.Status
            if game._GameOfLife__state.phase == 1:
                response['send_gen_move'] = True
        else:
            response['error'] = True
            response['message'] = game.error_message or 'Cell there, cannot you add'
    elif req['action'] == 'get_status':
        response['next_action'] = game.GetNextAction(player_num)
        alive_cells_counts = game.counts
        response['p1_cells'] = alive_cells_counts[1]
        response['p2_cells'] = alive_cells_counts[2]
        response['status'] = game.Status
        if response['next_action'] == 'add_cell':
            need_grid_in_response = True
            gameboard_class = '_mod-addcell'
        else:
            gameboard_class = ''
            need_grid_in_response = not 'gameboard' in req or not game.GridIsActual(json.loads(req['gameboard']))
        if need_grid_in_response:
            response['gameboard'] = render_template('gameboard.html',
                                                    grid=game._GameOfLife__state.grid,
                                                    gameboard_class=gameboard_class)
    elif req['action'] == 'gen_move':
        while game._GameOfLife__state.phase == 1:
            game.Move()
            game_db.state = game._GameOfLife__state.ToJSON()
            if game._GameOfLife__state.phase == -1:
                game_db.status = 2
            db.session.commit()
            sleep(0.3)
        response['success'] = True
    else:
        response['error'] = True
        response['message'] = 'Not the action you looking for, this one is'
    
    return make_response(jsonify(response), 200)


def getGameFromEntry(game_entry: Game) -> GameOfLife:
    if not isinstance(game_entry, Game):
        return None
    
    game_settings = json.loads(game_entry.settings)
    game_settings = GameSettings(generations_per_round=game_settings['generations_per_round'],
                                 rounds_number=game_settings['rounds_number'],
                                 new_cells_per_round=game_settings['new_cells_per_round'])
    
    game_state_params = json.loads(game_entry.state)
    game_state = GameState()
    for param in game_state_params:
        game_state.__setattr__(param, game_state_params[param])
    
    return GameOfLife(settings=game_settings, state=game_state)