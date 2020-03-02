import re

from sqlalchemy.sql import func
from sqlalchemy.types import String, TypeDecorator

# https://bitbucket.org/zzzeek/sqlalchemy/issues/3729/using-array_agg-around-row-function-does


class ArrayOfRecord(TypeDecorator):
    _array_regexp = re.compile(r"^\{(\".+?\")*\}$")
    _chunk_regexp = re.compile(r'"(.*?)",?')
    _param_regexp = re.compile(r"[^\(\),]+")

    impl = String

    def __init__(self, cols):
        self.cols = cols
        super().__init__()

    def process_result_value(self, value, dialect):
        # XXX(dcramer): if the trailing value(s?) fo t he returning array are NULL, postgres seems to
        # not return them, and thus our output array does not match the same length as our column
        # selection array
        #
        # For example if the input is:
        #   ARRAY_AGG_RESULT(col1, col2)
        # And the value of col2 is NULL
        # The resulting return value from this query will be:
        #   ({col1_value},)
        elems = self._array_regexp.match(value).group(1)
        elems = [e for e in self._chunk_regexp.split(elems) if e]
        padding = tuple((len(self.cols) - len(elems)) * (None,))
        return [tuple(self._param_regexp.findall(e)) + padding for e in elems]


def array_agg_row(*arg):
    return func.array_agg(func.row(*arg), type_=ArrayOfRecord(arg))
