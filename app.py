from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import render_template




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vagrant:@127.0.0.1:9998/vagrant_DB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

migrate=Migrate(app,db)


@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1>'

@app.route('/car')
def view_car():
    from models import car
    cars=car.query.all()
    return render_template('base.html',
                           cars=cars)