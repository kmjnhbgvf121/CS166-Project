from app import db


class car(db.Model):
    __tablename__='car'
    vin=db.Column(db.VARCHAR(16),primary_key=True)
    make=db.Column(db.VARCHAR(32))
    model=db.Column(db.VARCHAR(32))
    year=db.Column(db.INTEGER)

class customer(db.Model):
    __tablename__='customer'
    id=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.CHAR(32))
    lname=db.Column(db.CHAR(32))
    phone=db.Column(db.CHAR(13))
    address=db.Column(db.CHAR(256))


class mechanic(db.Model):
    __tablename__='mechanic'
    id=db.Column(db.INTEGER,primary_key=True)
    fname=db.Column(db.CHAR(32))
    lname=db.Column(db.CHAR(32))
    experience=db.Column(db.INTEGER)

class owns(db.Model):
    __tablename__='owns'
    ownership_id=db.Column(db.Integer,primary_key=True,nullable=False)
    customer_id=db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=False)
    car_vin=db.Column(db.VARCHAR(16),db.ForeignKey('car.vin'))

class service_request(db.Model):
    __tablename__='service_request'
    rid=db.Column(db.Integer,primary_key=True,nullable=False)
    customer_id=db.Column(db.Integer,db.ForeignKey('customer.id'))
    car_vin=db.Column(db.VARCHAR(16),db.ForeignKey('car.vin'))
    date=db.Column(db.DATE)
    odometer=db.Column(db.INTEGER)
    complain=db.Column(db.TEXT)

class closed_request(db.Model):
    __tablename__='closed_request'
    wid=db.Column(db.INTEGER,primary_key=True,nullable=False)
    rid=db.Column(db.INTEGER,db.ForeignKey('service_request.rid'))
    mid=db.Column(db.INTEGER,db.ForeignKey('mechanic.id'))
    date=db.Column(db.DATE)
    comment=db.Column(db.TEXT)
    bill=db.Column(db.INTEGER)
