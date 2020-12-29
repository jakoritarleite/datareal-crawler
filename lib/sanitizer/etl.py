from re import findall
from lxml import etree
from io import StringIO

class Sanitizer:
    def __init__(self, content: dict, encoding: str = 'UTF-8'):
        self.encoding = encoding
        
        assert isinstance(content, dict), \
            f'Content must be a Dictionary and not {type(content)}'

        self.content = content

    def clean(self):
        pass

