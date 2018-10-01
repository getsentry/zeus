import os
import sys

from .base import cli


@cli.command()
def shell():
    import IPython
    from zeus.app import app
    from zeus.config import db

    banner = "Python %s on %s\nIPython: %s\nApp: %s%s\nInstance: %s\n" % (
        sys.version,
        sys.platform,
        IPython.__version__,
        app.import_name,
        app.debug and " [debug]" or "",
        app.instance_path,
    )

    ctx = app.make_shell_context()
    ctx["app"].test_request_context().push()
    ctx["db"] = db
    # Import all models into the shell context
    ctx.update(db.Model._decl_class_registry)

    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup, "rb") as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    IPython.embed(banner1=banner, user_ns=ctx)
