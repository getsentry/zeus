import re


from sqlalchemy.sql import func
from sqlalchemy.types import String, TypeDecorator

# https://bitbucket.org/zzzeek/sqlalchemy/issues/3729/using-array_agg-around-row-function-does


class ArrayOfRecord(TypeDecorator):
    _array_regexp = re.compile(r"^\{(\".+?\")*\}$")
    _chunk_regexp = re.compile(r'"(.*?)",?')
    _param_regexp = re.compile(r"[^\(\),]+")

    impl = String

    def process_result_value(self, value, dialect):
        elems = self._array_regexp.match(value).group(1)
        elems = [e for e in self._chunk_regexp.split(elems) if e]
        return [tuple(self._param_regexp.findall(e)) for e in elems]


def array_agg_row(*arg):
    return func.array_agg(func.row(*arg), type_=ArrayOfRecord)
