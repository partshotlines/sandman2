import gzip
import io
import binascii
import json
import functools
from flask_sqlalchemy import SQLAlchemy

class Request:

    request = None
    data = None
    json = None

    def __init__(self, app, request):
        self.request = request
        self.gunzip_payload(request.data)

    def is_gzipped(self, data):
        ba = bytearray(data)
        gzip_header = b"\x1f\x8b\x08"
        return ba[:len(gzip_header)] == gzip_header

    @functools.lru_cache()
    def gunzip_payload(self, payload):
        data = ''
        if self.is_gzipped(payload):
            data = gzip.decompress(payload).decode('utf8')
        else:
            data = payload.decode('utf8')
        try:
            self.data = data
            self.json = json.loads(data)
        except:
            pass

    def before_request_hook(self, app, request):
        """
        This is a hook that extends anything before any request

        :param app: The application instance
        :param request: The request instance
        """
        path = request.__dict__['environ']['PATH_INFO']
        if '/utc/' in path:
            with app.app_context():
                db = SQLAlchemy()
                db.engine.execute('update utc set utc_ts = NOW()')

