import re

from typing import List
from unidecode import unidecode

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text: str, delim: str = "-") -> str:
    """
    Generates an ASCII-only slug.
    """
    result: List[str] = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return str(delim.join(result))
