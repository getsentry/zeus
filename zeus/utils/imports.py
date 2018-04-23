import pkgutil


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


def import_submodules(context: dict, root_module: str, path: str):
    """
    Import all submodules and register them in the ``context`` namespace.

    >>> import_submodules(locals(), __name__, __path__)
    """
    modules = {}
    for loader, module_name, is_pkg in pkgutil.walk_packages(path, root_module + "."):
        # this causes a Runtime error with model conflicts
        # module = loader.find_module(module_name).load_module(module_name)
        module = __import__(module_name, globals(), locals(), ["__name__"])
        keys = getattr(module, "__all__", None)
        if keys is None:
            keys = [k for k in vars(module).keys() if not k.startswith("_")]

        for k in keys:
            context[k] = getattr(module, k, None)
        modules[module_name] = module

    # maintain existing module namespace import with priority
    for k, v in modules.items():
        context[k] = v
