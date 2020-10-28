# -*- coding: utf-8 -*-
from io import open as _open
from json import loads
from os import path as _path, remove as _remove

str_types = (str,)

def read(path):
    with _open(path, encoding='utf-8', mode='rt') as fp:
        return loads(fp.read())

def exist(path):
    return _path.isfile(path)

def rm(path):
    if exist(path):
        _remove(path)

def update(path):
    rm(path)

def load(path):
    if not exist(path):
        update(path)

    return read(path)