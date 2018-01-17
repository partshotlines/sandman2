import time
from flask import request as request

class Stats:

    def __init__(self):
        self.response = None
        self.request = request

        self.full_path = self.request.full_path
        self.method = self.request.method
        self.auth = '-' if 'Authorization' not in self.request.headers else self.request.headers['Authorization']
        self.data = self.request.data
        self.remote_ip = self.request.environ['REMOTE_ADDR']
        self.start_time = time.time()
        self.user_agent = '-' if 'User-Agent' not in self.request.headers else self.request.headers['User-Agent']
        self.enc = '-' if 'Accept-Encoding' not in self.request.headers else self.request.headers['Accept-Encoding']

    def setresponse(self, response):
        self.response = response
        self.response_len = 0 if response.response is None or len(response.response) == 0 else len(response.response[0])
        self.response_code = response.status_code
        self.end_time = time.time()

    def log(self, log_data=False):
        if self.response is not None:
            s = (
                    self.remote_ip,
                    self.auth,
                    self.method,
                    self.full_path,
                    str(self.response_code),
                    str(self.response_len),
                    self.user_agent,
                    str(self.end_time - self.start_time),
                    self.data.decode('utf8') if log_data else '-'

            )
            print("%s %s \"%s %s\" %s %s %s %s seconds [%s]" % s)
