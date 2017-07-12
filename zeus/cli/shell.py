import os
import sys

from .base import cli


@cli.command()
def shell():
    import IPython
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app
    banner = 'Python %s on %s\nIPython: %s\nApp: %s%s\nInstance: %s\n' % (
        sys.version, sys.platform, IPython.__version__, app.import_name,
        app.debug and ' [debug]' or '', app.instance_path,
    )

    ctx = {}

    startup = os.environ.get('PYTHONSTARTUP')
    if startup and os.path.isfile(startup):
        with open(startup, 'rb') as f:
            eval(compile(f.read(), startup, 'exec'), ctx)

    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)
