# -*- coding: utf-8 -*-
import datetime

from truckfinder.models import db


class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    msrp_adjusted = db.Column(db.Integer)
    allx_adjusted = db.Column(db.Integer)
    az_adjusted = db.Column(db.Integer)
    az_applicable = db.Column(db.Boolean)

    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    vehicle = db.relationship('Vehicle', backref=db.backref('prices', lazy='dynamic'))

    def __init__(self, price, vehicle):
        self.date = datetime.date.today()
        self.msrp_adjusted = price.msrp
        self.allx_adjusted = price.allx
        self.az_adjusted = price.az
        self.az_applicable = price.az_applicable
        self.vehicle = vehicle

    def __repr__(self):
        return '<Price(msrp={})>'.format(self.msrp_adjusted)


def create_price_for_vehicle(price, vehicle):
    newprice = Price(price, vehicle)
    db.session.add(newprice)
    db.session.commit()
    return newprice
