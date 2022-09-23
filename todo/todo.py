import sys
from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from settings import DB_NAME, DB_USER, DB_PASSWORD

database_path="postgresql://postgres:postgres@localhost:5432/todo"
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=database_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db=SQLAlchemy(app)
CORS(app)

# migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'{self.id} {self.description} {self.created_at}'

db.create_all()

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

#  get todos
@app.route('/')
def index():
  data = Todo.query.all()
  return render_template('index.html', data=data)













if __name__ == "__main__":
  app.run(host='0.0.0.0')