import os
import json

def allread(filename:str, encoding:str='utf-8'):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding=encoding) as f:
                return f.read()
    except FileNotFoundError:
        return '파일이 없습니다. No files found.'
def replacefile(filename:str, old:str, new:str, encoding:str='utf-8'):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding=encoding) as f:
                a=f.read()
            a=a.replace(old, new)
            with open(filename, 'w', encoding=encoding) as f:
                f.write(a)
    except FileNotFoundError:
        pass

def read_json(filename:str, encoding:str='utf-8'):
    try:
        with open(filename, 'r', encoding=encoding) as f:
            a=json.load(f)
            return a
    except FileNotFoundError:
        raise '파일이 없습니다. No files found.'

def json_write(filename: str, data: dict, encoding: str = 'utf-8'):
    with open(filename, 'w', encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def listappend_file(filename:str, data:str, encoding:str='utf-8'):
    with open(filename, 'a', encoding=encoding) as f:
        f.write(f'{data}\n')

def listremove_file(filename:str, data:str, encoding:str='utf-8'):
    a=allread(filename)
    a.replace(f'{data}', '')
    with open(filename, 'w', encoding=encoding) as f:
        f.write(a)
