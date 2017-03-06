"""models.py -- event listner also added."""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class User(BaseMixin, db.Model):
    __tablename__ = 'users'

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    clients = db.relationship('Client', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return "User(id={id}, username={username})".format(id=self.id, username=self.username)


class Client(BaseMixin, db.Model):
    __tablename__ = 'clients'

    def __init__(self, email, first_name, owner_id, last_name, age=0, weight=0, height=0):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.weight = weight
        self.height = height
        self.owner_id = owner_id

    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))

    def __str__(self):
        return "Client(id={id}, firstname={firstname})".format(id=self.id, username=self.firstname)


day_association_table = db.Table('day_association_table',
                                 db.Column('plan_id', db.Integer, db.ForeignKey('plans.id')),
                                 db.Column('day_id', db.Integer, db.ForeignKey('days.id'))
                                 )


class Plan(BaseMixin, db.Model):
    __tablename__ = 'plans'

    def __init__(self, name):
        self.name = name

    name = db.Column(db.String(120), unique=True, nullable=False)
    clients = db.relationship('Client', backref='plan', lazy='dynamic')
    days = db.relationship("Day", secondary=day_association_table,
                           backref=db.backref('plans', lazy='dynamic'))

    def __str__(self):
        return "Plan(id={id}, username={username})".format(id=self.id, username=self.username)


exercise_association_table = db.Table('exercise_association_table',
                                      db.Column('day_id', db.Integer, db.ForeignKey('days.id')),
                                      db.Column('exercise_id', db.Integer, db.ForeignKey('exercises.id'))
                                      )


class Day(BaseMixin, db.Model):
    __tablename__ = 'days'

    def __init__(self, name, exercises=None):
        self.name = name
        self.exercises = exercises

    name = db.Column(db.String(120), unique=True, nullable=False)
    exercises = db.relationship("Exercise", secondary=exercise_association_table,
                                backref=db.backref('days', lazy='dynamic'))

    def __str__(self):
        return "Day(id={id}, name={name})".format(id=self.id, name=self.name)


class Exercise(BaseMixin, db.Model):
    __tablename__ = 'exercises'

    def __init__(self, name, activity=None):
        self.name = name
        self.activity = activity

    name = db.Column(db.String(120), unique=True, nullable=False)
    activity = db.Column(db.String(200))

    def __str__(self):
        return "Exercise(id={id}, name={name})".format(id=self.id, name=self.name)


from sqlalchemy import event

# TODO - Implement mailing
# User some Queue to take care of mailing
# Whenever a user is assigned to a workout plan, he(she) should receive an email confirmation
@event.listens_for(Client.plan_id, 'set')
def receive_user_set_for_plan(target, value, oldvalue, initiator):
    # query the Plan from plan_id
    # send mail to the client.email
    receiver = target.email
    subject = "You are assigned to {}".format(target.plan.name)
    print receiver, subject
    # Use Flask-Mail to send email
    print "TODO -- Mail Sending"

# Whenever a plan is modified, the user(s) connected should be notified of the change by mail.*
@event.listens_for(Plan, 'before_update')
def receive_after_plan_update(mapper, connection, target):
    # get the client_ids of the plan updated
    # get the Client object, send mail to all their email
    print "TODO -- Send Plan ids to queue to get clients and mail them"
