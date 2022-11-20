from flask import Flask, request, Response
import json
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from functools import wraps
import sqlite3
import collections
from datetime import datetime

DB_PATH = 'todo.db'
NOTSTARTED = 'Not Started'
INPROGRESS = 'In Progress'
FINISHED = 'Finished'

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

authorizations = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API', authorizations=authorizations
)

def read_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message' : 'Token is missing.'}, 401

        if token != 'sam' and token != 'aravind':
            return {'message' : 'Your token is wrong, wrong, wrong!!!'}, 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated

def write_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message' : 'Token is missing.'}, 401

        if token != 'aravind':
            return {'message' : 'Your token is wrong, wrong, wrong!!!'}, 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due' : fields.Date(required=True, description='The task due date'),
    'status' : fields.String(required=True, description='The task status')
})




#id_counter = 0

class TodoDAO(object):
    def __init__(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('select max(id) from tasks')
        row = c.fetchone()
        conn.close()
        self.counter = row[0]

    def add_to_list(self, data):
        try:
            todo = data
            global id_counter
            todo['id'] = self.counter = self.counter + 1

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute('insert into tasks(id, task, due, status) values(?,?,?,?)', (todo['id'], todo['task'], todo['due'], todo['status']))

            conn.commit()
            conn.close()
            return todo

        except Exception as e:
            print('Error: ', e)
            return None

    # data = add_to_list({'task':'do laundry', 'due' : '2021-05-20', 'status' : 'Not Started'})
    # data = add_to_list({'task':'do dishes', 'due' : '2021-05-20', 'status' : 'In Progress'})
    # data = add_to_list({'task':'assignment', 'due' : '2021-05-18', 'status' : 'Finished'})
    # data = add_to_list({'task':'workout', 'due' : '2021-05-18', 'status' : 'In Progress'})
    # data = add_to_list({'task':'clean', 'due' : '2021-05-18', 'status' : 'Not Started'})


    def get_all_items(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory=sqlite3.Row
            c = conn.cursor()
            c.execute('select * from tasks')
            rows = c.fetchall()
            conn.close()
            return rows

            # objects_list = []
            # for row in rows:
            #     d = collections.OrderedDict()
            #     d['id'] = row[0]
            #     d['task'] = row[1]
            #     d['due'] = row[2]
            #     d['status'] = row[3]
            #     objects_list.append(d)
            # return objects_list

        except Exception as e:
            print('Error: ', e)
            return None

    def get_item(self, id):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory=sqlite3.Row
            c = conn.cursor()
            c.execute("select * from tasks where id='%d'" % (id))
            res = c.fetchone()
            conn.close()
            return res

        except Exception as e:
            print('Error: ', e)
            return None

    def delete_item(self, id):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory=sqlite3.Row
            c = conn.cursor()
            res = self.get_item(id)
            c.execute("delete from tasks where id='%d'" %(id))
            conn.commit()
            conn.close()

            return list(res)

        except Exception as e:
            print('Error: ', e)
            return None

    def update(self, id, data):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('update tasks set task=?, due=?, status=? where id=?', (data['task'], data['due'], data['status'], id))
            conn.commit()
            conn.close()
            todo = self.get_item(id)
            return todo

        except Exception as e:
            print('Error: ', e)
            return None

    def get_due(self, due):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory=sqlite3.Row
            c = conn.cursor()
            c.execute("select * from tasks where due='%s'" % (str(due)))
            res = c.fetchall()
            conn.close()
            return res

        except Exception as e:
            print('Error: ', e)
            return None

    def get_finished(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory=sqlite3.Row
            c = conn.cursor()
            c.execute("select * from tasks where status='Finished'")
            res = c.fetchall()
            conn.close()
            return res

        except Exception as e:
            print('Error: ', e)
            return None

    def get_overdue(self):
        try:
            today = datetime.today()

            conn = sqlite3.connect(DB_PATH)
            # conn.row_factory=sqlite3.Row
            c = conn.cursor()
            c.execute("select * from tasks")
            rows = c.fetchall()

            objects_list = []
            for row in rows:
                due = row[2]
                status = row[3]
                due = datetime.strptime(due, '%Y-%m-%d')
                if(due<today and status!='Finished'):
                    d = collections.OrderedDict()
                    d['id'] = row[0]
                    d['task'] = row[1]
                    d['due'] = row[2]
                    d['status'] = row[3]
                    objects_list.append(d)
            conn.close()
            return objects_list

        except Exception as e:
            print('Error: ', e)
            return None

    def update_status(self, id):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            todo = self.get_item(id)
            status=todo[3]
            if(status == NOTSTARTED):
                status = INPROGRESS
            elif(status == INPROGRESS):
                status = FINISHED
            else:
                return []

            c.execute('update tasks set status=? where id=?', (status, id))
            conn.commit()
            conn.close()
            todo = self.get_item(id)
            return todo

        except Exception as e:
            print('Error: ', e)
            return None

DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    @ns.doc(security='apikey')
    @read_token_required
    def get(self):
        '''List all tasks'''
        return DAO.get_all_items()


    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    @ns.doc(security='apikey')
    @write_token_required
    def post(self):
        '''Create a new task'''
        return DAO.add_to_list(api.payload), 201

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    @ns.doc(security='apikey')
    @read_token_required
    def get(self, id):
        '''Fetch a given resource'''
        res = DAO.get_item(id)
        if res==None:
            api.abort(404, "Todo {} doesn't exist".format(id))
        return res

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    @ns.doc(security='apikey')
    @write_token_required
    def delete(self, id):
        '''Delete a task given its identifier'''
        res = DAO.delete_item(id)
        if res==None:
            api.abort(404, "Todo {} doesn't exist".format(id))
        return res

    @ns.expect(todo)
    @ns.marshal_with(todo)
    @ns.doc(security='apikey')
    @write_token_required
    def put(self, id):
        '''Update a task given its identifier'''
        res = DAO.update(id, api.payload)
        if res==None:
            api.abort(404, "Todo {} doesn't exist".format(id))
        return res

@ns.route('/due/<due>')
@ns.response(404, 'Todo not found')
@ns.param('due', 'The task due date')
class Todoget(Resource):
    '''Gets tasks based on due, overdue and status'''
    @ns.doc('get_todos_due')
    @ns.marshal_list_with(todo)
    @ns.doc(security='apikey')
    @read_token_required
    def get(self, due):
        '''Fetch tasks due on given due date'''
        res = DAO.get_due(due)
        if res==[]:
            api.abort(404, "No tasks due on {}".format(due))
        return res

@ns.route('/overdue')
@ns.response(404, 'No tasks')
class Overdue(Resource):
    @ns.doc('get_todos_overdue')
    @ns.marshal_list_with(todo)
    @ns.doc(security='apikey')
    @read_token_required
    def get(self):
        '''Fetch overdue tasks'''
        res = DAO.get_overdue()
        if res==[]:
            api.abort(404, "No overdue tasks")
        return res

@ns.route('/finished')
@ns.response(404, 'No tasks')
class Finished(Resource):
    @ns.doc('get_todos_finished')
    @ns.marshal_list_with(todo)
    @ns.doc(security='apikey')
    @read_token_required
    def get(self):
        '''Fetch finished tasks'''
        res = DAO.get_finished()
        if res==[]:
            api.abort(404, "No finished tasks")
        return res

@ns.route('/status/<int:id>')
@ns.response(404, 'Todo not found')
@ns.response(400, 'Todo finished')
@ns.param('id', 'The task identifier')
class Status(Resource):
    @ns.marshal_with(todo)
    @ns.doc(security='apikey')
    @write_token_required
    def put(self, id):
        '''Upgrade status of task'''
        res = DAO.update_status(id)
        if res==None:
            api.abort(404, "Todo {} doesn't exist".format(id))
        elif res==[]:
            api.abort(400, "Task finished. Cannot update status")
        return res

if __name__ == '__main__':
    app.run(debug=True)
