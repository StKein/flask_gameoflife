from datetime import datetime
from game import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    first_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    second_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, nullable=False, default=0)
    settings = db.Column(db.String(1000))
    state = db.Column(db.String(1000))

    def __repr__(self):
        status = ['open', 'active', 'finished'][self.status]
        player_1 = load_user(self.first_player_id).username
        player_2 = User.query.filter_by(id=self.second_player_id).first()
        if player_2:
            return f"{player_1} vs {player_2.username}, {status} ({self.date_created}))"
        else:
            return f"{player_1}, {status} ({self.date_created}))"