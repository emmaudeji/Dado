from crypt import methods
import sys
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from settings import DB_NAME, DB_USER, DB_PASSWORD

database_path="postgresql://postgres:postgres@localhost:5432/todo"
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db=SQLAlchemy(app)
CORS(app)

migrate = Migrate(app, db)

# Model
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    set_completed = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    
    def __repr__(self):
        return f'{self.set_completed} {self.description} {self.created_at}'

class TodoList(db.Model):
  __tablename__= 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  todos = db.relationship('Todo', backref='list', lazy=True)

  def __repr__(self):
    return f'{self.name} {self.todos}'


# db.create_all()

#  create todos
@app.route('/todo/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    if not description:
      return "no description"
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    body = jsonify({
      "id": todo.id,
      "description": todo.description, 
      "created_at": todo.created_at
    }) 
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    return body

#  update todo checkbox.
@app.route('/todos/<todo_id>/set_completed', methods=['POST'])
def check_checkbox(todo_id):
  try:
    completed = request.get_json()['completed']
    print(completed)
    todo = Todo.query.get(todo_id)
    todo.set_completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

# delete todo item
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  error=False
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    error=True
    print(sys.exc_info(error))
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))


#  get todos
@app.route('/lists/<list_id>')
def get_todo_list(list_id):
  lists = TodoList.query.order_by('id').all()
  active_list = TodoList.query.get(list_id)
  todos = Todo.query.filter_by(list_id=list_id).order_by('id').all()
  return render_template('index.html', todos=todos, lists=lists, active_list=active_list)

#  get todos
@app.route('/')
def index():
  return redirect(url_for('get_todo_list', list_id=1))



if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)