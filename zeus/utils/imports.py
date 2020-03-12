def import_string(path: str):
    """
    Path must be module.path.ClassName

    >>> cls = import_string('sentry.models.Group')
    """
    if "." not in path:
        return __import__(path)

    module_name, class_name = path.rsplit(".", 1)

    module = __import__(module_name, {}, {}, [class_name])
    try:
        return getattr(module, class_name)

    except AttributeError as exc:
        raise ImportError from exc
