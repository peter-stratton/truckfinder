# -*- coding: utf-8 -*-
import datetime

from truckfinder.models import db


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.DateTime)
    vin = db.Column(db.String(32), unique=True)
    stage = db.Column(db.String(32))
    sticker_url = db.Column(db.String(2048))
    vehicle_url = db.Column(db.String(2048))
    f_box_size = db.Column(db.String(32))
    f_cab_style = db.Column(db.String(32))
    f_drivetrain = db.Column(db.String(8))
    f_engine = db.Column(db.String(64))
    f_mpg = db.Column(db.String(32))
    f_package = db.Column(db.String(32))
    f_transmission = db.Column(db.String(256))

    dealership_id = db.Column(db.Integer, db.ForeignKey('dealership.id'))
    dealership = db.relationship('Dealership', backref=db.backref('vehicles', lazy='dynamic'))

    def __init__(self, truck, dealership):
        self.date_added = datetime.date.today()
        self.vin = truck.vin
        self.stage = truck.stage
        self.sticker_url = truck.sticker_url
        self.vehicle_url = truck.vehicle_url
        self.f_box_size = truck.features['Box Size']
        self.f_cab_style = truck.features['Cab Style']
        self.f_drivetrain = truck.features['Drivetrain']
        self.f_engine = truck.features['Engine']
        self.f_mpg = truck.features['MPG']
        self.f_package = truck.features['Package']
        self.f_transmission = truck.features['Transmission']
        self.dealership = dealership

    def __repr__(self):
        return '<Vehicle(vin={})>'.format(self.vin)


def get_or_create_vehicle(truck, dealership):
    vehicle = Vehicle.query.filter_by(vin=truck.vin).first()
    if not vehicle:
        vehicle = Vehicle(truck, dealership)
        db.session.add(vehicle)
        db.session.commit()
    return vehicle
