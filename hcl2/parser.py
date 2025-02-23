"""A parser for HCL2 implemented using the Lark parser"""
import os
from os.path import exists, dirname

from lark import Lark
from lark.grammar import Rule
from lark.lexer import TerminalDef

from hcl2.transformer import DictTransformer

PARSER_FILE = os.path.join(dirname(__file__), 'lark_parser.py')

PARSER_FILE_TEMPLATE = """
from lark import Lark

DATA = (%s)
MEMO = (%s)

def Lark_StandAlone(**kwargs):
  return Lark._load_from_dict(DATA, MEMO, **kwargs)
"""


def create_parser_file():
    """
    Parsing the Lark grammar takes about 0.5 seconds. In order to improve performance we can cache the parser
    file. The below code caches the entire python file which is generated by Lark's standalone parser feature
    See: https://github.com/lark-parser/lark/blob/master/lark/tools/standalone.py

    Lark also supports serializing the parser config but the deserialize function did not work for me.
    The lark state contains dicts with numbers as keys which is not supported by json so the serialized
    state can't be written to a json file. Exporting to other file types would have required
    adding additional dependencies or writing a lot more code. Lark's standalone parser
    feature works great but it expects to be run as a separate shell command
    The below code copies some of the standalone parser generator code in a way that we can use
    """
    lark_file = os.path.join(dirname(__file__), 'hcl2.lark')
    with open(lark_file, 'r', encoding="utf-8") as lark_file,\
         open(PARSER_FILE, 'w', encoding="utf-8") as parser_file:
        lark_inst = Lark(lark_file.read(), parser="lalr", lexer="standard")

        data, memo = lark_inst.memo_serialize([TerminalDef, Rule])

        print(PARSER_FILE_TEMPLATE % (data, memo), file=parser_file)


if not exists(PARSER_FILE):
    create_parser_file()

# pylint: disable=wrong-import-position
# Lark_StandAlone needs to be imported after the above block of code because lark_parser.py might not exist
from hcl2.lark_parser import Lark_StandAlone

hcl2 = Lark_StandAlone(transformer=DictTransformer())
