# -*- coding: utf-8 -*-
import random
from pathlib import Path
from threading import Lock
from os import path as _path

from lib.fake_headers.errors import FakeUserAgentError
from lib.fake_headers.utils import load, str_types

class FakeUserAgent(object):
    def __init__(self):
        self.replacements = {' ': '', '_': ''}
        self.path = _path.join(
            Path('faka_useragent.json').parent.absolute(),
            'lib/fake_headers/fake_useragent.json'
        )
        self.data = {}
        self.data_randomize = []
        self.data_browsers = {}

        self.load()

    def load(self):
        try:
            with self.load.lock:
                self.data = load(self.path)
                self.data_randomize = list(self.data['randomize'].values())
                self.data_browsers = self.data['browsers']

        except FakeUserAgentError:
            raise Exception(FakeUserAgentError)

    load.lock = Lock()

    def random(self):
        try:
            browser = random.choice(self.data_randomize)

            return random.choice(self.data_browsers[browser])

        except (KeyError, IndexError):
            raise FakeUserAgentError('Error occurred during getting browser')


# alias
UserAgent = FakeUserAgent