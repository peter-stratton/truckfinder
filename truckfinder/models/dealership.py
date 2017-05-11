# -*- coding: utf-8 -*-

from truckfinder.models import db


class Dealership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    code = db.Column(db.String(16), unique=True)
    distance = db.Column(db.String(16))
    phone = db.Column(db.String(16))
    street = db.Column(db.String(128))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    zipcode = db.Column(db.String(12))

    def __init__(self, dealer):
        self.name = dealer.name
        self.code = dealer.code
        self.distance = dealer.distance
        self.phone = dealer.phone
        self.street = dealer.street
        self.city = dealer.city
        self.state = dealer.state
        self.zipcode = dealer.zip

    def __repr__(self):
        return '<Dealership(name={})>'.format(self.name)


def get_or_create_dealership(dealer):
    dealership = Dealership.query.filter_by(code=dealer.code).first()
    if not dealership:
        dealership = Dealership(dealer)
        db.session.add(dealership)
        db.session.commit()
    return dealership
