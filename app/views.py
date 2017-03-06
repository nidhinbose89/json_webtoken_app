"""views.py."""
from sqlalchemy.exc import IntegrityError
from flask import request, jsonify, session
from functools import wraps
from flask_jwt_extended import JWTManager, jwt_required, \
    create_access_token, jwt_refresh_token_required, \
    create_refresh_token, get_jwt_identity
from flask.views import MethodView

from app import app, db
from models import User, Exercise, Day, Plan, Client

jwt = JWTManager(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"message": "Please login to continue", "next": request.path}), 401
        return f(*args, **kwargs)
    return decorated_function

DECORATORS = [login_required, jwt_required]


@app.route('/sign_up', methods=['POST'])
def sign_up():
    # TODO - better/generic exception handling
    data = request.get_json()
    if not data:
        return jsonify({"message": "Please input the username and password."})
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError as e:
        return jsonify({"message": "The username already in DB."}), 409
    except Exception as e:
        return jsonify({"message": e.message})
    return jsonify({"message": "User Created Successfully.", "username": data['username']})


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter(User.username == username).scalar()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    session['user_id'] = user.id
    session['logged_in'] = True
    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    ret = {
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    ret = {
        'message': 'Logged out successfully.'
    }
    return jsonify(ret), 200

# Refresh token endpoint. This will generate a new access token from
# the refresh token, but will mark that access token as non-fresh
# (so that it cannot access any endpoint protected via the
# fresh_jwt_required decorator)


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    ret = {'access_token': new_token}
    return jsonify(ret), 200


class ClientUserAPI(MethodView):
    decorators = DECORATORS

    def get(self, client_id):
        if client_id is None:
            # return a list of users
            clients = Client.query.all()
            data = []
            count = 0
            for each_client in clients:
                count += 1
                data.append(
                    {
                        'id': each_client.id,
                        'email': each_client.email,
                        'first_name': each_client.first_name,
                        'last_name': each_client.last_name,
                        'age': each_client.age,
                        'weight': each_client.weight,
                        'height': each_client.height,
                        'owner_id': each_client.owner_id,
                        'plan_id': each_client.plan_id
                    }
                )
            return jsonify({"data": data, "count": count}), 200
        else:
            # expose a single user
            client = Client.query.filter_by(id=client_id).first()
            if client:
                ret = {
                    'id': client.id,
                    'email': client.email,
                    'first_name': client.first_name,
                    'last_name': client.last_name,
                    'age': client.age,
                    'weight': client.weight,
                    'height': client.height,
                    'owner_id': client.owner_id,
                    'plan_id': client.plan_id
                }
                return jsonify(ret), 200
            ret = {
                'message': 'Client not found.',
            }
            return jsonify(ret), 404

    def post(self):
        # create a new user
        data = request.get_json()
        if not data:
            ret = {
                'message': 'Provide data.',
            }
            return jsonify(ret), 422
        if all(k in data for k in ("email", "first_name", "last_name")):
            client = Client(email=data.get('email'),
                            first_name=data.get('first_name'),
                            last_name=data.get('last_name'),
                            age=data.get('age'),
                            weight=data.get('weight'),
                            height=data.get('height'),
                            owner_id=session.get('user_id'))
            try:
                db.session.add(client)
                db.session.commit()
            except IntegrityError as e:
                return jsonify({'message': e.message}), 409
            except Exception as e:
                raise e
            db.session.refresh(client)
            ret = {
                'message': 'Client created successfully.',
                'id': client.id,
            }
            ret.update(data)
            return jsonify(ret), 200

        ret = {
            'message': 'Must provide email, first name and last name.',
        }
        return jsonify(ret), 422

    def delete(self, client_id):
        # delete a single user
        client = Client.query.filter_by(
            id=client_id, owner_id=session.get('user_id')).first()
        if not client:
            ret = {
                'message': 'Client not found.',
            }
            return jsonify(ret), 404
        db.session.delete(client)
        db.session.commit()
        ret = {
            'message': 'Client deleted successfully.',
            'client_id': client_id
        }
        return jsonify(ret), 200

    def put(self, client_id):
        # update a single user
        data = request.get_json()
        if data:
            client = Client.query.filter_by(id=client_id).first()
            if not client:
                ret = {
                    'message': 'Client not found.',
                }
                return jsonify(ret), 404
            if data.get('email'):
                client.email = data.get('email')
            if data.get('first_name'):
                client.first_name = data.get('first_name')
            if data.get('last_name'):
                client.last_name = data.get('last_name')
            if data.get('age'):
                client.age = data.get('age')
            if data.get('weight'):
                client.weight = data.get('weight')
            if data.get('height'):
                client.height = data.get('height')
            if data.get('plan_id'):
                client.plan_id = data.get('plan_id')
            try:
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                ret = {
                    'message': e.message,
                    'id': client.id
                }
                return jsonify(ret), 409
            except Exception as e:
                raise e
            ret = {
                'message': 'Client updated successfully.',
                'id': client.id
            }
            return jsonify(ret), 200
        ret = {
            'message': 'Provide data to update.',
        }
        return jsonify(ret), 422


class ExerciseAPI(MethodView):
    decorators = DECORATORS

    def get(self, exercise_id):
        if exercise_id is None:
            exercises = Exercise.query.all()
            data = []
            count = 0
            for each_exercise in exercises:
                count += 1
                data.append(
                    {
                        'id': each_exercise.id,
                        'name': each_exercise.name,
                        'activity': each_exercise.activity
                    }
                )
            return jsonify({"data": data, "count": count}), 200
        else:
            exercise = Exercise.query.filter_by(id=exercise_id).first()
            if exercise:
                ret = {
                    'id': exercise.id,
                    'name': exercise.name,
                    'activity': exercise.activity
                }
                return jsonify(ret), 200
            ret = {
                'message': 'Exercise not found.',
            }
            return jsonify(ret), 404

    def post(self):
        # create a new exercise
        data = request.get_json()
        if not data:
            ret = {
                'message': 'Provide data.',
            }
            return jsonify(ret), 422
        exercise = Exercise(name=data['name'], activity=data['activity'])
        db.session.add(exercise)
        db.session.commit()
        db.session.refresh(exercise)
        ret = {
            'message': 'Exercise created successfully.',
            'id': exercise.id,
            'name': data['name']
        }
        return jsonify(ret), 200

        pass

    def delete(self, exercise_id):
        # delete a single exercise
        exercise = Exercise.query.filter_by(id=exercise_id).first()
        if not exercise:
            ret = {
                'message': 'Exercise not found.',
            }
            return jsonify(ret), 404
        db.session.delete(exercise)
        db.session.commit()
        ret = {
            'message': 'Exercise deleted successfully.',
            'exercise_id': exercise_id
        }
        return jsonify(ret), 200

    def put(self, exercise_id):
        # update a single exercise
        data = request.get_json()
        if data:
            exercise = Exercise.query.filter_by(id=exercise_id).first()
            if not exercise:
                ret = {
                    'message': 'Exercise not found.',
                }
                return jsonify(ret), 404
            if data.get('name'):
                exercise.name = data.get('name')
            if data.get('activity'):
                exercise.activity = data.get('activity')
            db.session.commit()
            ret = {
                'message': 'Exercise updated successfully.',
                'id': exercise.id
            }
            return jsonify(ret), 200
        ret = {
            'message': 'Provide data to update.',
        }
        return jsonify(ret), 422


class DaysAPI(MethodView):
    decorators = DECORATORS

    def get(self, day_id):
        def _get_exercises_data(day):
            exercises = []
            for each_ex in day.exercises:
                temp_dat = {}
                temp_dat['id'] = each_ex.id
                temp_dat['name'] = each_ex.name
                temp_dat['activity'] = each_ex.activity
                exercises.append(temp_dat)
            return exercises

        if day_id is None:
            days = Day.query.all()
            data = []
            count = 0
            for each_day in days:
                count += 1
                data.append(
                    {
                        'id': each_day.id,
                        'name': each_day.name,
                        'exercises': _get_exercises_data(each_day)
                    }
                )
            return jsonify({"data": data, "count": count}), 200
        else:
            day = Day.query.filter_by(id=day_id).first()
            if day:
                ret = {
                    'id': day.id,
                    'name': day.name,
                    'exercises': _get_exercises_data(day)
                }
                return jsonify(ret), 200
            ret = {
                'message': 'Exercise not found.',
            }
            return jsonify(ret), 404

    def post(self):
        # create a new day
        data = request.get_json()
        if not data:
            ret = {
                'message': 'Provide data.',
            }
            return jsonify(ret), 422
        exercises = []
        if data.get('exercises'):
            exercises = [Exercise.get(each_exercise)
                         for each_exercise in data.get('exercises')]

        day = Day(name=data['name'], exercises=filter(None, exercises))
        db.session.add(day)
        db.session.commit()
        db.session.refresh(day)
        ret = {
            'message': 'Day created successfully.',
            'id': day.id,
            'name': data['name']
        }
        return jsonify(ret), 200

    def delete(self, day_id):
        # delete a single day
        day = Day.query.filter_by(id=day_id).first()
        if not day:
            ret = {
                'message': 'Day not found.',
            }
            return jsonify(ret), 404
        db.session.delete(day)
        db.session.commit()
        ret = {
            'message': 'Day deleted successfully.',
            'day_id': day_id
        }
        return jsonify(ret), 200

    def put(self, day_id):
        # update a single day
        day = Day.query.filter_by(id=day_id).first()
        if not day:
            ret = {
                'message': 'Day not found.',
            }
            return jsonify(ret), 404
        data = request.get_json()
        if data:
            if data.get('name'):
                day.name = data.get('name')
            # must provide all users to be present or None
            if data.get('exercises'):
                exercises = []
                for each_id in data['exercises']:
                    ex_obj = Exercise.query.get(each_id)
                    if ex_obj:
                        exercises.append(ex_obj)
                day.exercises = exercises
            db.session.commit()
            ret = {
                'message': 'Day updated successfully.',
                'id': day.id
            }
            return jsonify(ret), 200
        ret = {
            'message': 'Provide data to update.',
        }
        return jsonify(ret), 422


class PlanAPI(MethodView):
    decorators = DECORATORS

    def get(self, plan_id):
        def _get_plan_days(plan):
            out = []
            for each_day in plan.days:
                d_data = {}
                d_data['id'] = each_day.id
                d_data['name'] = each_day.name
                d_data['exercises'] = []
                for each_ex in each_day.exercises:
                    d_data['exercises'].append({'id': each_ex.id,
                                                'name': each_ex.name,
                                                'activity': each_ex.activity
                                                })
                out.append(d_data)
            return out

        def _get_plan_clients(plan):
            out = []
            for each_client in plan.clients:
                c_data = {}
                c_data['id'] = each_client.id
                c_data['email'] = each_client.email
                c_data['first_name'] = each_client.first_name
                c_data['last_name'] = each_client.last_name
                c_data['age'] = each_client.age
                c_data['weight'] = each_client.weight
                c_data['height'] = each_client.height
                out.append(c_data)
            return out

        if plan_id is None:
            # return a list of plan
            plans = Plan.query.all()
            data = []
            count = 0
            for each_plan in plans:
                count += 1
                data.append(
                    {
                        'id': each_plan.id,
                        'name': each_plan.name,
                        'days': _get_plan_days(each_plan),
                        'clients': _get_plan_clients(each_plan)
                    }
                )
            return jsonify({"data": data, "count": count}), 200
        else:
            # expose a single plan
            plan = Plan.query.filter_by(id=plan_id).first()
            if plan:
                ret = {
                    'id': plan.id,
                    'name': plan.name,
                    'days': _get_plan_days(plan),
                    'clients': _get_plan_clients(plan)
                }
                return jsonify(ret), 200
            ret = {
                'message': 'Exercise not found.',
            }
            return jsonify(ret), 404

    def post(self):
        # create a new plan
        data = request.get_json()
        if not data:
            ret = {
                'message': 'Provide data.',
            }
            return jsonify(ret), 422
        plan = Plan(name=data['name'])
        if data.get('clients'):
            clients = [Client.get(each_client)
                       for each_client in data.get('clients')]
            plan.clients = filter(None, clients)

        if data.get('days'):
            days = [Day.query.get(each_day) for each_day in data.get('days')]
            plan.days = filter(None, days)

        db.session.add(plan)
        db.session.commit()
        db.session.refresh(plan)
        ret = {
            'id': plan.id,
            'message': 'Plan created successfully.',
            'name': data['name']
        }
        return jsonify(ret), 200

    def delete(self, plan_id):
        # delete a single user
        plan = Plan.query.filter_by(id=plan_id).first()
        if not plan:
            ret = {
                'message': 'Plan not found.',
            }
            return jsonify(ret), 404
        db.session.delete(plan)
        db.session.commit()
        ret = {
            'message': 'Plan deleted successfully.',
            'plan_id': plan_id
        }
        return jsonify(ret), 200

    def put(self, plan_id):
        # update a single plan
        data = request.get_json()
        if data:
            plan = Plan.query.filter_by(id=plan_id).first()
            if not plan:
                ret = {
                    'message': 'Plan not found.',
                }
                return jsonify(ret), 404
            if data.get('name'):
                plan.name = data.get('name')

            if data.get('clients'):
                clients = [Client.query.get(each_client)
                           for each_client in data.get('clients')]
                plan.clients = filter(None, clients)

            if data.get('days'):
                days = [Day.query.get(each_day)
                        for each_day in data.get('days')]
                plan.days = filter(None, days)
            db.session.commit()
            ret = {
                'message': 'Plan updated successfully.',
                'id': plan.id
            }
            return jsonify(ret), 200
        ret = {
            'message': 'Provide data to update.',
        }
        return jsonify(ret), 422


def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s/<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

register_api(ClientUserAPI, 'client_user_api', '/clients', pk='client_id')
register_api(ExerciseAPI, 'exercises_api', '/exercises', pk='exercise_id')
register_api(DaysAPI, 'days_api', '/days', pk='day_id')
register_api(PlanAPI, 'plans_api', '/plans', pk='plan_id')
