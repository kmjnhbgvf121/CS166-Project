from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://vagrant:@127.0.0.1:9998/vagrant_DB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hard'

db = SQLAlchemy(app)

# migrate=Migrate(app,db)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/new_customer', methods=['GET', 'POST'])
def add_new_customer():
    from models import customer
    if request.method == 'POST':
        if not request.form['fname'] or not request.form['lname'] or not request.form['phone'] \
                or not request.form['address']:
            flash('Please enter all the information')
        elif (customer.query.filter_by(fname=request.form['fname']).all() != [] and
              customer.query.filter_by(lname=request.form['lname']).all() != []):

            flash('Customer exists!')
            return redirect(url_for('add_new_customer'))
        else:
            id = db.session.query(db.func.max(customer.id)).scalar() + 1
            phone = "(" + request.form['phone'][0:3] + ")" + request.form['phone'][3:6] + "-" + request.form['phone'][
                                                                                                6:10]
            new_customer = customer(id=id, fname=request.form['fname'], lname=request.form['lname'],
                                    phone=phone,
                                    address=request.form['address'])
            db.session.add(new_customer)
            db.session.commit()
            flash('New customer added successful!')
            return redirect(url_for('index'))

    return render_template('new_customer.html')


@app.route('/new_mechanic', methods=['GET', 'POST'])
def add_new_mechanic():
    from models import mechanic
    if request.method == 'POST':
        if not request.form['fname'] or not request.form['lname'] \
                or not request.form['experience']:
            flash('Please enter all the information', 'error')
        elif (mechanic.query.filter_by(fname=request.form['fname']).all() != [] and
              mechanic.query.filter_by(lname=request.form['lname']).all() != []):

            flash('Mechanic exists!')
            return redirect(url_for('add_new_mechanic'))
        else:
            id = db.session.query(db.func.max(mechanic.id)).scalar() + 1
            new_mechanic = mechanic(id=id, fname=request.form['fname'], lname=request.form['lname'],
                                    experience=request.form['experience'])
            db.session.add(new_mechanic)
            db.session.commit()
            flash('New mechanic added successful!')
            return redirect(url_for('index'))

    return render_template('new_mechanic.html')


@app.route('/new_car', methods=['GET', 'POST'])
def add_new_car():
    from models import car
    if request.method == 'POST':
        if not request.form['vin'] or not request.form['make'] \
                or not request.form['model'] or not request.form['year']:
            flash('Please enter all the information')
        elif car.query.filter_by(vin=request.form['vin']).all():

            flash('VIN exists!')
            return redirect(url_for('add_new_car'))
        elif len(str(request.form['vin'])) != 16:
            flash('Invalid VIN!')
        else:
            new_car = car(vin=request.form['vin'], make=request.form['make'],
                          model=request.form['model'], year=request.form['year'])
            db.session.add(new_car)
            db.session.commit()
            flash('New car added successful!')
            return redirect(url_for('index'))

    return render_template('new_car.html')


@app.route('/init_service', methods=['GET', 'POST'])
def init_service():
    from models import customer, owns, service_request, car
    global cid
    if request.method == 'POST' and request.form.get('car_vin') is None:
        c = customer.query.filter_by(lname=request.form['lname']).first()
        if c is None:
            flash('Invalid Name!')
            return render_template('new_customer.html')
        cid = c.id
        cars = owns.query.filter_by(customer_id=cid).subquery()

        car_list = car.query.join((cars, cars.c.car_vin == car.vin)).all()

        return render_template('init_service.html', cars=car_list)

    elif request.method == 'POST' and request.form.get('car_vin') != 'good':
        rid = db.session.query(db.func.max(service_request.rid)).scalar() + 1
        car_vin = request.form['vin']
        date = request.form['date']
        odometer = request.form['odometer']
        complain = request.form['complain']
        new_service = service_request(rid=rid, customer_id=cid, car_vin=car_vin,
                                      date=date, odometer=odometer, complain=complain)
        db.session.add(new_service)
        db.session.commit()
        flash('Initiate service request successful!')

        return redirect(url_for('index'))

    elif request.method == 'POST' and request.form.get('car_vin') == 'good':
        car_vin = request.form['vin']
        car_make = request.form['car_make']
        car_model = request.form['car_model']
        car_year = request.form['car_year']

        if car.query.filter_by(vin=car_vin).all():
            flash('VIN exists!')
            return render_template('init_service.html')

        new_car = car(vin=car_vin, make=car_make, model=car_model, year=car_year)
        oid = db.session.query(db.func.max(owns.ownership_id)).scalar() + 1
        new_own_car = owns(ownership_id=oid, customer_id=cid, car_vin=car_vin)

        rid = db.session.query(db.func.max(service_request.rid)).scalar() + 1
        date = request.form['date']
        odometer = request.form['odometer']
        complain = request.form['complain']
        new_service = service_request(rid=rid, customer_id=cid, car_vin=car_vin,
                                      date=date, odometer=odometer, complain=complain)

        db.session.add(new_car)
        db.session.commit()
        db.session.add(new_own_car)
        db.session.commit()
        db.session.add(new_service)
        db.session.commit()

        flash('Add new car and initiate service request successful!')

        return redirect(url_for('index'))

    return render_template('init_service.html')


@app.route('/close_service', methods=['GET', 'POST'])
def close_service():
    from models import service_request, mechanic, closed_request
    from datetime import date
    if request.method == 'POST':
        if closed_request.query.filter_by(rid=request.form['rid']).first() is not None:
            flash('Already closed!')
        elif service_request.query.filter_by(rid=request.form['rid']).first() \
                and mechanic.query.filter_by(id=request.form['mid']).first():
            service_date = service_request.query.filter_by(rid=request.form['rid']).first().date
            cdate = request.form['cdate']
            cdate = date(int(cdate[:4]), int(cdate[5:7]), int(cdate[8:]))

            if cdate > service_date:
                wid = db.session.query(db.func.max(closed_request.wid)).scalar() + 1
                new_close_request = closed_request(wid=wid, rid=request.form['rid'], mid=request.form['mid'],
                                                   date=cdate, comment=request.form['comment'],
                                                   bill=request.form['bill'])
                db.session.add(new_close_request)
                db.session.commit()
                flash('Close service request successful!')

                return redirect(url_for('index'))
            else:
                flash('Invalid date!')

        elif service_request.query.filter_by(rid=request.form['rid']).first() is None:
            flash('Invalid service request number!')
        elif mechanic.query.filter_by(id=request.form['mid']).first() is None:
            flash('Invalid Employee ID')

    return render_template('close_service.html')


@app.route('/list_bill/<int:page>', methods=['GET'])
def list_bill(page=None):
    from models import closed_request
    if not page:
        page = 1

    bills = db.session.query(closed_request).filter(closed_request.bill < 100)
    pagination = bills.paginate(page, 50)

    return render_template('list_bill.html', result=pagination)


@app.route('/list_customers/<int:page>')
def list_customers(page=None):
    from models import owns, customer
    if not page:
        page = 1

    customers = db.session.query(owns.customer_id) \
        .group_by(owns.customer_id).having(db.func.count(owns.customer_id) > 20).subquery()
    cname = db.session.query(customer).join((customers, customer.id == customers.c.customer_id))
    pagination = cname.paginate(page, 50)

    return render_template('list_customers.html', result=pagination)


@app.route('/list_cars/<int:page>')
def list_cars(page=None):
    from models import service_request, car
    if not page:
        page = 1

    lessCar = service_request.query.filter(service_request.odometer < 50000).subquery()
    oldCar = car.query.join((lessCar, car.vin == lessCar.c.car_vin)).filter(car.year < 1995).distinct()

    pagination = oldCar.paginate(page, 50)

    return render_template('list_cars.html', result=pagination)


@app.route('/list_services/<int:page>', methods=['GET', 'POST'])
def list_services(page=None):
    global k
    from models import service_request, car
    if not page:
        page = 1

    if request.method == 'POST':
        k = request.form['k']
        page = 1
    elif request.method == 'GET' and page == 1:
        k = 100

    service = db.session.query(service_request.car_vin,
                               db.func.count(service_request.car_vin).label('service_count')).group_by(
        service_request.car_vin).order_by(db.func.count(service_request.car_vin).desc()).limit(k).subquery()

    pagination = db.session.query(car.make, car.model, service.c.service_count). \
        join((service, service.c.car_vin == car.vin)).paginate(page, 50)

    return render_template('list_services.html', result=pagination)


@app.route('/list_total_bill/<int:page>')
def list_total_bill(page=None):
    from models import customer, closed_request, service_request
    if not page:
        page = 1

    tb = db.session.query(service_request.customer_id, db.func.sum(closed_request.bill).label('tbill')). \
        join((closed_request, closed_request.rid == service_request.rid)). \
        group_by(service_request.customer_id).order_by(db.func.sum(closed_request.bill).desc()).subquery()

    name_bill = db.session.query(customer.fname, customer.lname, tb.c.tbill). \
        join((tb, tb.c.customer_id == customer.id)).order_by(tb.c.tbill.desc())

    pagination = name_bill.paginate(page, 50)

    return render_template('list_total_bill.html', result=pagination)
