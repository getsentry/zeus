from .controller import Controller
from . import resources as r

app = Controller('api', __name__)
app.add_resource('/', r.IndexResource)
app.add_resource('/auth/', r.AuthIndexResource)
