from flask import Flask, current_app, jsonify
from sandman2.model import db, Model

from sqlalchemy import orm, MetaData, Table
from sqlalchemy.ext.automap import automap_base
from flask_sqlalchemy import SQLAlchemy
# https://docs.pylonsproject.org/projects/pylons-webframework/en/latest/advanced_models.html
# https://parijatmishra.wordpress.com/2009/01/18/sqlalchemy-one-classes-two-tables/
# http://sandman2.readthedocs.io/en/latest/extending.html
# http://flask.pocoo.org/snippets/22/
# defined to prevent error


db = SQLAlchemy()


class HTestExt(db.Model, Model):
    __tablename__ = 'htest'
#
    id = db.Column(db.Integer, primary_key=True)
    val = db.Column(db.String)

class RTestExt(db.Model, Model):
    __tablename__ = 'rtest'
    rid = db.Column(db.Integer, primary_key=True)
    hid = db.Column(db.Integer, db.ForeignKey('htest.id'))
    val2 = db.Column(db.String)
    htest = db.relationship(HTestExt, primaryjoin=(HTestExt.id == hid), lazy='joined')


