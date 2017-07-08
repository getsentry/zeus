from .controller import Controller
from . import resources as r

app = Controller('api', __name__)
app.add_resource('/', r.IndexResource)
app.add_resource('/auth', r.AuthIndexResource)
app.add_resource('/builds', r.BuildIndexResource)
app.add_resource('/builds/<build_id>', r.BuildDetailsResource)
app.add_resource('/builds/<build_id>/jobs', r.BuildJobsResource)
app.add_resource('/builds/<build_id>/tests', r.BuildTestsResource)
app.add_resource('/jobs/<job_id>', r.JobDetailsResource)
app.add_resource('/jobs/<job_id>/artifacts', r.JobArtifactsResource)
app.add_resource('/repos', r.RepositoryIndexResource)
app.add_resource('/repos/<repository_id>/builds', r.RepositoryBuildsResource)
app.add_resource('/<path:path>', r.CatchallResource)
