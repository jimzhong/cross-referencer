import subprocess
import os
import pygments
from pygments.token import Token
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_for_filename

def parse_defs(path):

    output = subprocess.check_output(['ctags', '-x', path]).decode()
    for line in output.splitlines():
        # ident, type, lineNo
        yield line.split(maxsplit=3)[:3]

def tokenize(path, min_length=4):

    with open(path, "r", errors='ignore') as f:
        code = f.read()

    filename = os.path.split(path)[-1]
    try:
        lexer = get_lexer_for_filename(filename)
    except ClassNotFound:
        # TODO: log it
        return
    tokens = pygments.lex(code, lexer)
    lineno = 1
    for tokentype, value in tokens:
        if tokentype in Token.Name and len(value) >= min_length:
            # only care about func/var names for now
            yield (value, tokentype, lineno)
        lineno += value.count('\n')

if __name__ == "__main__":

    import pprint
    import sys
    pprint.pprint(list(tokenize(sys.argv[1])))
