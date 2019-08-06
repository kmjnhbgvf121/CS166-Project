from app import db

class car(db.Model):
    __tablename__='car'
    vin=db.Column(db.VARCHAR(16),primary_key=True)
    make=db.Column(db.VARCHAR(32))
    model=db.Column(db.VARCHAR(32))
    year=db.Column(db.INTEGER)

    def __repr__(self):
        return '<car %r>' %self.vin