import pkgutil


def import_string(path):
    """
    Path must be module.path.ClassName

    >>> cls = import_string('sentry.models.Group')
    """
    if '.' not in key:
        return __import__(key)

    module_name, class_name = key.rsplit('.', 1)

    module = __import__(module_name, {}, {}, [class_name], -1)
    try:
        handler = getattr(module, class_name)
    except AttributeError as exc:
        raise ImportError from exc

    return handle


def import_submodules(context, root_module, path):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_submodules(locals(), __name__, __path__)
    """
    for loader, module_name, is_pkg in pkgutil.walk_packages(path, root_module + '.'):
        # this causes a Runtime error with model conflicts
        # module = loader.find_module(module_name).load_module(module_name)
        module = __import__(module_name, globals(), locals(), ['__name__'])
        for k, v in vars(module).items():
            if not k.startswith('_'):
                context[k] = v
        context[module_name] = module
