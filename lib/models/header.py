from lib.fake_headers import UserAgent

class Header(object):
    def __init__(self, header):
        self.headers = header
        
    def __get_header__(self):
        if self.headers is None:
            self.headers = UserAgent().random()

        return {'user-agent': self.headers}