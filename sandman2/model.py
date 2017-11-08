"""Module containing code related to *sandman2* ORM models."""

# Standard library imports
import datetime
from decimal import Decimal

# Third-party imports
from sqlalchemy.inspection import inspect
from flask_sqlalchemy import SQLAlchemy  # pylint: disable=import-error,no-name-in-module
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()

class Model(object):

    """The sandman2 Model class is the base class for all RESTful resources.
    There is a one-to-one mapping between a table in the database and a
    :class:`sandman2.model.Model`.
    """

    #: The relative URL this resource should live at.
    __url__ = None

    #: The API version of this resource (not yet used).
    __version__ = '1'

    #: The HTTP methods this resource supports (default=all).
    __methods__ = {
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'HEAD',
        'OPTIONS'
        }

    @classmethod
    def required(cls):
        """Return a list of all columns required by the database to create the
        resource.

        :param cls: The Model class to gather attributes from
        :rtype: list
        """
        columns = []
        for column in cls.__table__.columns:  # pylint: disable=no-member
            is_autoincrement = 'int' in str(column.type).lower() and column.autoincrement
            if ( ((not column.nullable and not column.primary_key) or (column.primary_key and not is_autoincrement)) and column.server_default is None):
                columns.append(column.name)
        return columns

    @classmethod
    def optional(cls):
        """Return a list of all nullable columns for the resource's table.

        :rtype: list
        """
        columns = []
        for column in cls.__table__.columns:  # pylint: disable=no-member
            if column.nullable or column.server_default is not None:
                columns.append(column.name)
        return columns

    @classmethod
    def primary_key(cls):
        """Return the key of the model's primary key field.

        :rtype: string
        """
        return list(
            cls.__table__.primary_key.columns)[  # pylint: disable=no-member
                0].key


    @classmethod
    def primary_key_column(cls):
        """Return the column of the model's primary key field.

        :rtype: column
        """
        return list(
            cls.__table__.primary_key.columns)[  # pylint: disable=no-member
                0]

    def to_dict(self):
        """Return the resource as a dictionary.

        :rtype: dict
        """
#         print self.__dict__
#         from sqlalchemy.inspection import inspect
#         for r in self.__mapper__.relationships:
#             print r

#         print self.__dict__
        result_dict = {}
#         for column in self.__table__.columns.keys():  # pylint: disable=no-member
        for column in self.__dict__:
            if column is not "_sa_instance_state":
#                 print column
                value = result_dict[column] = getattr(self, column, None)
                d = getattr(value, "__dict__", None)
                if isinstance(value, Decimal):
                    result_dict[column] = float(result_dict[column])
                elif isinstance(value, datetime.datetime):
                    result_dict[column] = value.isoformat()
                elif d is not None:
                    result_dict[column] = value.to_dict()
                else:
                    result_dict[column] = value
        return result_dict

    @classmethod
    def unique_columns(self):
        """Return a list column names with a unique key constraint
        """
        l = []
        for idx in self.__table__.__dict__['indexes']:
            if idx.unique:
                for col in idx.__dict__['_pending_colargs']:
                    if col.key not in l:
                        l.append(col.key)

        return l



#     # modiciation - aadel - 2017-09-05 - stopped use, check to see the new one is being used for nested objects/joins
#     def to_dict_old(self):
#         """Return the resource as a dictionary.
#
#         :rtype: dict
#         """
#         result_dict = {}
#         for column in self.__table__.columns.keys():  # pylint: disable=no-member
#             value = result_dict[column] = getattr(self, column, None)
#             if isinstance(value, Decimal):
#                 result_dict[column] = float(result_dict[column])
#             elif isinstance(value, datetime.datetime):
#                 result_dict[column] = value.isoformat()
#         return result_dict

    def links(self):
        """Return a dictionary of links to related resources that should be
        included in the *Link* header of an HTTP response.

        :rtype: dict

        """
        link_dict = {'self': self.resource_uri()}
        for relationship in inspect(  # pylint: disable=maybe-no-member
                self.__class__).relationships:
            if 'collection' not in relationship.key:
                instance = getattr(self, relationship.key)
                if instance:
                    link_dict[str(relationship.key)] = instance.resource_uri()
        return link_dict

    def resource_uri(self):
        """Return the URI to this specific resource.

        :rtype: str

        """
        return self.__url__ + '/' + str(getattr(self, self.primary_key()))

    def update(self, attributes):
        """Update the current instance based on attribute->value items in
        *attributes*.

        :param dict attributes: Dictionary of attributes to be updated
        :rtype: :class:`sandman2.model.Model`
        """
        for attribute in attributes:
            setattr(self, attribute, attributes[attribute])
        return self

    @classmethod
    def description(cls):
        """Return a field->data type dictionary describing this model
        as reported by the database.

        :rtype: dict
        """

        description = {}
        for column in cls.__table__.columns:  # pylint: disable=no-member
            column_description = str(column.type)
            if not column.nullable and column.server_default is None:
                column_description += ' (required)'
            description[column.name] = column_description
        return description

DeclarativeModel = declarative_base(cls=(db.Model, Model))
AutomapModel = automap_base(DeclarativeModel)
