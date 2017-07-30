from flask import current_app
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import md5
from sandman2.model import db, Model, AutomapModel
# from sqlalchemy.dialects import mysql

class Auth:
    db = SQLAlchemy()

    def password_verify(self, username, password):
        user_cls = None
        for cls in AutomapModel.classes:
            if cls.__table__.name == 'phlj_users':
                user_cls = cls
        query = user_cls.query
        filters = []
        if hasattr(user_cls, 'username'):
            filters.append(getattr(user_cls, 'username') == username)
        if len(filters) > 0:
            query = query.filter(*filters)
#             print query.compile(dialect=mysql.dialect())
#             print str(query)

            recs = query.all()
            rec = {} if len(recs) <= 0 else recs[0].to_dict()
            if rec == {}:
                return False
            hashed = rec['password'].encode('utf-8')
            if hashed[0] == '$':
                # do bcrypt compute
                if bcrypt.hashpw(password, hashed) == hashed:
                    return True
                else:
                    return False
            else:
                # do md5 + salt compute
                parts = hashed.split(':')
                crypted = parts[0]
                salt = parts[1]
                m = md5.new(password + salt)
                if m.hexdigest() == crypted:
                    return True
                else:
                    return False
        else:
            return False

