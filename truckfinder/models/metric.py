# -*- coding: utf-8 -*-
import datetime

from truckfinder.models import db


class Metrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    vehicle_count = db.Column(db.Integer)
    engine_27L_count = db.Column(db.Integer)
    engine_35L_count = db.Column(db.Integer)
    avg_msrp = db.Column(db.Integer)
    avg_allx = db.Column(db.Integer)
    avg_az = db.Column(db.Integer)
    error_count = db.Column(db.Integer)

    def __init__(self, metric_dict):
        self.date = datetime.date.today()
        self.vehicle_count = metric_dict['v_count']
        self.engine_27L_count = metric_dict['e_27L_count']
        self.engine_35L_count = metric_dict['e_35L_count']
        self.avg_msrp = metric_dict['sum_msrp'] / metric_dict['v_count']
        self.avg_allx = metric_dict['sum_allx'] / metric_dict['v_count']
        self.avg_az = metric_dict['sum_az'] / metric_dict['v_count']
        self.error_count = metric_dict['error_count']

    def __repr__(self):
        return '<Metrics(date={})>'.format(self.date)


def create_daily_metrics(metric_dict):
    new_metrics = Metrics(metric_dict)
    db.session.add(new_metrics)
    db.session.commit()
    return new_metrics
