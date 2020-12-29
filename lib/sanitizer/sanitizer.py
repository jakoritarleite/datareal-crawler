from re import findall
from lxml import etree
from io import StringIO

class Sanitizer:
    def __init__(content: str, encoding: str = 'UTF-8'):
        self.content = content
        self.encoding = encoding

    def clean(self):
        print(self.content)