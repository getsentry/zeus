import toronado
import lxml


def inline_css(value):
    tree = lxml.html.document_fromstring(value)
    toronado.inline(tree)
    # CSS media query support is inconistent when the DOCTYPE declaration is
    # missing, so we force it to HTML5 here.
    return lxml.html.tostring(tree, doctype="<!DOCTYPE html>").decode("utf-8")
