from flask import Flask, render_template, request, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, desc
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db.init_app(app)

class ToDo(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.now())

with app.app_context():
    db.create_all()

@app.route('/todos')
def todos():
    todos = db.session.execute(db.select(ToDo).order_by(desc(ToDo.id))).scalars()
    return render_template('index.html', todos=todos)   

@app.route('/todos/get-one/<id>')
def get_one(id):
    todo = db.session.execute(db.select(ToDo).filter_by(id=id)).scalar_one()
    return render_template('get-one.html', todo=todo)

@app.route('/todos/post', methods=['GET', 'POST'])
def post():
    id = ''
    if request.method == 'POST':
        todo = ToDo(
            title=request.form.get('title'),
            description=request.form.get('description'),
        )
        db.session.add(todo)
        db.session.flush()
        id = todo.id
        db.session.commit()
    return render_template('post.html', id=id)
    
@app.route('/todos/put/<id>', methods=['GET', 'PUT'])
def put(id):
    todo = db.session.execute(db.select(ToDo).filter_by(id=id)).scalar_one()
    if request.method == 'PUT' and todo:
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        todo.completed = request.form.get('completed') == 'True'
        db.session.flush()
        db.session.commit()
        return render_template('get-one.html', todo=todo)
    if request.method == 'GET' and todo:
        return render_template('put.html', todo=todo)
        
@app.route('/todos/delete/<id>', methods=['DELETE'])
def delete(id):
    if request.method == 'DELETE':
        todo = db.session.execute(db.select(ToDo).filter_by(id=id)).scalar_one()
        db.session.delete(todo)
        db.session.commit()
        return ''