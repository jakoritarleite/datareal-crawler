import importlib

from lib.sanitizer import settings

class Sanitizer:
    def __init__(self, content: dict, encoding: str = 'UTF-8'):
        assert isinstance(encoding, str), \
            f'Encoding must be a String and not {type(encoding)}'

        assert isinstance(content, dict), \
            f'Content must be a Dictionary and not {type(content)}'

        self.encoding = encoding
        self.content = content

    def clean(self):
        for item in self.content:
            if self.content[item] and item not in settings.IGNORE_ITEMS:
                function = getattr(importlib.import_module('lib.sanitizer.cleaners'), item)
                self.content[item] = function(self.content[item])

            else: pass

        return self.content