"""Automatically generated REST API services from SQLAlchemy
ORM models or a database introspection."""

# Third-party imports
from flask import request, make_response, current_app
import flask
import json
from flask.views import MethodView

# Application imports
from sandman2.exception import NotFoundException, BadRequestException
from sandman2.model import db
from sandman2.decorators import etag, validate_fields
from flask_httpauth import HTTPBasicAuth

import request as Request

try:
    import Auth
except ImportError:
    import auth as Auth
    pass

from Stats import Stats

auth = HTTPBasicAuth()

def add_link_headers(response, links):
    """Return *response* with the proper link headers set, based on the contents
    of *links*.

    :param response: :class:`flask.Response` response object for links to be
                     added
    :param dict links: Dictionary of links to be added
    :rtype :class:`flask.Response` :
    """
    link_string = '<{}>; rel=self'.format(links['self'])
    for link in links.values():
        link_string += ', <{}>; rel=related'.format(link)
    response.headers['Link'] = link_string
    return response


def jsonify(resource):
    """Return a Flask ``Response`` object containing a
    JSON representation of *resource*.

    :param resource: The resource to act as the basis of the response
    """
    response = flask.jsonify(resource.to_dict() if type(resource) is not type(list()) else [r for r in resource])
    if type(resource) is not type(list()):
        response = add_link_headers(response, resource.links())
    return response


def is_valid_method(model, resource=None):
    """Return the error message to be sent to the client if the current
    request passes fails any user-defined validation."""
    validation_function_name = 'is_valid_{}'.format(
        request.method.lower())
    if hasattr(model, validation_function_name):
        return getattr(model, validation_function_name)(request, resource)

class Service(MethodView):

    """The *Service* class is a generic extension of Flask's *MethodView*,
    providing default RESTful functionality for a given ORM resource.

    Each service has an associated *__model__* attribute which represents the
    ORM resource it exposes. Services are JSON-only. HTML-based representation
    is available through the admin interface.
    """

    @auth.verify_password
    def verify_pw(username, password):
        a = Auth.Auth()
        return a.password_verify(username, password)


    #: The sandman2.model.Model-derived class to expose
    __model__ = None


    #: The string used to describe the elements when a collection is
    #: returned.
    __json_collection_name__ = 'resources'

    @auth.login_required
    def delete(self, resource_id):
        """Return an HTTP response object resulting from a HTTP DELETE call.

        :param resource_id: The value of the resource's primary key
        """
        resource = self._resource(resource_id)
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        db.session().delete(resource)
        db.session().commit()
        return self._no_content_response()

    @auth.login_required
    @etag
    def get(self, resource_id=None):
        """Return an HTTP response object resulting from an HTTP GET call.

        If *resource_id* is provided, return just the single resource.
        Otherwise, return the full collection.

        :param resource_id: The value of the resource's primary key
        """
        stats = Stats()
        if request.path.endswith('meta'):
            return self._meta()

        if request.path.endswith('/max'):
            resource_id = self._get_max()
        elif request.path.endswith('/min'):
            resource_id = self._get_min()

        if resource_id is None:
            error_message = is_valid_method(self.__model__)
            if error_message:
                raise BadRequestException(error_message)

            if 'export' in request.args:
                return self._export(self._all_resources())

            resp = flask.jsonify({
                self.__json_collection_name__: self._all_resources()
                })
        else:
            resource = self._resource(resource_id)
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            resp = jsonify(resource)
        stats.setresponse(resp)
        stats.log()
        return resp

    @auth.login_required
    def patch(self, resource_id):
        """Return an HTTP response object resulting from an HTTP PATCH call.

        :returns: ``HTTP 200`` if the resource already exists
        :returns: ``HTTP 400`` if the request is malformed
        :returns: ``HTTP 404`` if the resource is not found
        :param resource_id: The value of the resource's primary key
        """
        stats = Stats()
        req = Request.Request(current_app, request)

        resource = self._resource(resource_id)
        error_message = is_valid_method(self.__model__, resource)
        if error_message:
            raise BadRequestException(error_message)
        if not req.json:
            raise BadRequestException('No JSON data received')
        resource.update(req.json)
        db.session().merge(resource)
        db.session().flush()
        db.session().refresh( resource )
        ret = self._created_response(resource)
        db.session().commit()
        stats.setresponse(ret)
        stats.log()
        return ret #jsonify(resource)

    # aadel - 2017-09-18 - complete overhaul to handle multiples via the collection name tag, or a single one
    @auth.login_required
    @validate_fields
    def post(self):
        """Return the JSON representation of a new resource created through
        an HTTP POST call.

        :returns: ``HTTP 201`` if a resource is properly created
        :returns: ``HTTP 204`` if the resource already exists
        :returns: ``HTTP 400`` if the request is malformed or missing data
        """
        stats = Stats()
        req = Request.Request(current_app, request)
        ret = '{}'
        resources = req.json[self.__json_collection_name__] if self.__json_collection_name__ in req.json else self.__model__(**req.json)
        if self.__json_collection_name__ in req.json:
            l = []
            for i in resources:
                resource = self.__model__(**i)
                l.append( resource )
                error_message = is_valid_method(self.__model__, resource)
                if error_message:
                    raise BadRequestException(error_message)
                db.session().add(resource)
            db.session().flush()
            resources = l
            for resource in l:
                db.session().refresh( resource )

            ret = flask.jsonify({
                self.__json_collection_name__: [ r.to_dict() for r in resources ]
            })

        else:
            error_message = is_valid_method(self.__model__, resources)
            if error_message:
                raise BadRequestException(error_message)
            db.session().add(resources)
            db.session().flush()
            db.session().refresh( resources )
            ret = self._created_response(resources)

        db.session().commit()
        stats.setresponse(ret)
        stats.log()
        return ret

    @auth.login_required
    @validate_fields
    def put(self, resource_id=None):
        """Return the JSON representation of a new resource created or updated
        through an HTTP PUT call.

        If resource_id is not provided, it is assumed the primary key field is
        included and a totally new resource is created. Otherwise, the existing
        resource referred to by *resource_id* is updated with the provided JSON
        data. This method is idempotent.

        :returns: ``HTTP 201`` if a new resource is created
        :returns: ``HTTP 200`` if a resource is updated
        :returns: ``HTTP 400`` if the request is malformed or missing data
        """
        stats = Stats()
        req = Request.Request(current_app, request)
        if resource_id:
            resource = self.__model__.query.get(resource_id)
            if resource:
                error_message = is_valid_method(self.__model__, resource)
                if error_message:
                    raise BadRequestException(error_message)
                resource.update(req.json)
                db.session().merge(resource)
                db.session().commit()
                ret = jsonify(resource)
                stats.setresponse(ret)
                stats.log()
                return ret

            resource = self.__model__(**req.json)  # pylint: disable=not-callable
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            db.session().add(resource)
            db.session().commit()
            ret = self._created_response(resource)
            stats.setresponse(ret)
            stats.log()
            return ret
        else:
            ret = '{}'
            resources = req.json[self.__json_collection_name__] if self.__json_collection_name__ in req.json else self.__model__(**req.json)
            if self.__json_collection_name__ in req.json:
                l = []
                for i in resources:
                    resource = self.__model__(**i)
                    error_message = is_valid_method(self.__model__, resource)
                    if error_message:
                        raise BadRequestException(error_message)
                    resource = self._upsert(resource, db)
                    l.append( resource )
#                 db.session().flush()
                resources = l
#                 for resource in l:
#                     db.session().refresh( resource )

                ret = flask.jsonify({
                    self.__json_collection_name__: [ r.to_dict() for r in resources ]
                })

            else:
                error_message = is_valid_method(self.__model__, resources)
                if error_message:
                    raise BadRequestException(error_message)
                resources = self._upsert(resources,db)
#             db.session().add(resources)
#                 db.session().flush()
#                 db.session().refresh( resources )
                ret = self._created_response(resources)

            db.session().commit()
            stats.setresponse(ret)
            stats.log()
            return ret

    def _upsert(self, resource, db):
        """Checks the resources against it's models primary and unique key(s)
        to see if it already exists. If it does, it does an update, merge
        if it does not, it does an add
        """

        filters = []
        for key in self.__model__.unique_columns():
            if hasattr(self.__model__, key) and hasattr(resource, key):
                filters.append(getattr(self.__model__, key) == getattr(resource, key))
            else:
                raise BadRequestException('Invalid field [{}]'.format(key))

        filters2 = []
        key = self.__model__.primary_key_column().name
        if hasattr(self.__model__, key) and hasattr(resource, key):
            filters2.append(getattr(self.__model__, key) == getattr(resource, key))
        else:
            raise BadRequestException('Invalid field [{}]'.format(key))


        resource_collision = self.__model__.query.filter(*filters).first()
        resource_collision2 = self.__model__.query.filter(*filters2).first()
        if resource_collision:
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            resource_collision.update(resource.to_dict())
            db.session().merge(resource_collision)
            db.session().flush()
            db.session().refresh( resource_collision )
            return resource_collision
        elif resource_collision2:
            error_message = is_valid_method(self.__model__, resource)
            if error_message:
                raise BadRequestException(error_message)
            resource_collision2.update(resource.to_dict())
            db.session().merge(resource_collision2)
            db.session().flush()
            db.session().refresh( resource_collision2 )
            return resource_collision2

        else:
            db.session().add(resource)
            db.session().flush()
            db.session.refresh( resource )

            return resource

    @auth.login_required
    def _meta(self):
        """Return a description of this resource as reported by the
        database."""
        return flask.jsonify(self.__model__.description())

    def _get_max(self):
        """Return the max primary key in the model

        :rtype: :Integer
        """
        return db.session.query(db.func.max(self.__model__.primary_key_column())).one()

    def _get_min(self):
        """Return the min primary key in the model

        :rtype: :Integer
        """
        return db.session.query(db.func.min(self.__model__.primary_key_column())).one()

    def _resource(self, resource_id):
        """Return the ``sandman2.model.Model`` instance with the given
        *resource_id*.

        :rtype: :class:`sandman2.model.Model`
        """
        # addition - aadel - 2017-07-27 - defining max and min id methods
        resource = self.__model__.query.get(resource_id)
        if not resource:
            raise NotFoundException()
        return resource

    def _q(self, query, filters=[], page=0, page_size=None, order=[]):
        """ from https://stackoverflow.com/questions/13258934/applying-limit-and-offset-to-all-queries-in-sqlalchemy/25943188#25943188
        Do the sorting, limiting, filtering and paging in the database instead of on the web server, helper method for that

        :rtype: :class:`sandman2.model.Model`
        """
        if len(filters):
            query = query.filter(*filters)
        if len(order):
            query = query.order_by(*order)
        if page_size is not None and page_size > 0:
            query = query.limit(page_size)
        if page > 0 and page_size is not None and page_size > 0:
            query = query.offset(page*page_size)
        return query


    def _all_resources(self):
        """Return the complete collection of resources as a list of
        dictionaries.

        :rtype: :class:`sandman2.model.Model`
        """
        args = {k: v for (k, v) in request.args.items() if k not in ('page', 'export')}
        filters = []
        order = []
        limit = 0
        if len(args.items()) > 0:
            for key, value in args.items():
                gte = False
                lte = False
                ne = False
                if key[-1:] == '>' or key[-1:] == '<' or key[-1:] == '!':
                    if key[-1:] == '>':
                        gte = True
                    elif key[-1:] == '<':
                        lte = True
                    elif key[-1:] == '!':
                        ne = True
                    key = key[:-1]

                if key.startswith('%'):
                    key = key[1:]
                    filters.append(getattr(self.__model__, key).like(str(value), escape='/'))
                elif key == 'sort':
                    # modification - aadel - 2017-07-27 - allow the use of -value for desc order by and ? wildcards, etc
                    order.append(db.text(value))
                elif key == 'limit':
                    limit = value
                elif hasattr(self.__model__, key):
                    if not gte and not lte and not ne:
                        filters.append(getattr(self.__model__, key) == value)
                    elif gte:
                        filters.append(getattr(self.__model__, key) >= value)
                    elif lte:
                        filters.append(getattr(self.__model__, key) <= value)
                    elif ne:
                        filters.append(getattr(self.__model__, key) != value)

                else:
                    raise BadRequestException('Invalid field [{}]'.format(key))


        queryset = self._q(self.__model__.query,
                filters,
                int(request.args['page']) if 'page' in request.args else 0,
                int(limit) if 'limit' in request.args and int(limit) > 0  else 50000,
                order
            )

        resources = queryset.all()
#         for r in resources:
#             print r.object_as_dict()
        return [r.to_dict() for r in resources]

    def _export(self, collection):
        """Return a CSV of the resources in *collection*.

        :param list collection: A list of resources represented by dicts
        """
        fieldnames = collection[0].keys()
        faux_csv = ','.join(fieldnames) + '\r\n'
        for resource in collection:
            faux_csv += ','.join((str(x) for x in resource.values())) + '\r\n'
        response = make_response(faux_csv)
        response.mimetype = 'text/csv'
        return response


    @staticmethod
    def _no_content_response():
        """Return an HTTP 204 "No Content" response.

        :returns: HTTP Response
        """
        response = make_response()
        response.status_code = 204
        return response

    @staticmethod
    def _created_response(resource):
        """Return an HTTP 201 "Created" response.

        :returns: HTTP Response
        """

#         if type(resource) == type(list()):
#             response = jsonify(resource)
#             response.status_code = 201
#         else:
#             response = jsonify(resource)
#             response.status_code = 201
#             return response
#         else:
#             l = []
#             for r in resource:
#                 l.append(jsonify(r))
#             response = json.dumps( l )
        response = jsonify( resource )
#             response = add_link_headers(response, resource.links())
        response.status_code = 201
        return response
