from .controller import Controller
from . import resources as r

app = Controller('api', __name__)
app.add_resource('/', r.IndexResource)
app.add_resource('/auth', r.AuthIndexResource)
app.add_resource('/builds', r.BuildIndexResource)
app.add_resource('/organizations', r.OrganizationIndexResource)
app.add_resource('/projects', r.ProjectIndexResource)
app.add_resource('/organizations/<org_name>/projects', r.OrganizationProjectsResource)
app.add_resource('/organizations/<org_name>/repos', r.OrganizationRepositoriesResource)
app.add_resource('/projects/<org_name>/<project_name>/builds', r.ProjectBuildsResource)
app.add_resource('/projects/<org_name>/<project_name>/tests', r.ProjectTestsResource)
app.add_resource('/projects/<org_name>/<project_name>/test-tree', r.ProjectTestTreeResource)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>', r.BuildDetailsResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/file-coverage',
    r.BuildFileCoverageResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/jobs', r.BuildJobsResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/source', r.BuildSourceResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/tests', r.BuildTestsResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/tests/<test_name>',
    r.TestDetailsResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/jobs/<job_number>',
    r.JobDetailsResource
)
app.add_resource(
    '/projects/<org_name>/<project_name>/builds/<build_number>/jobs/<job_number>/artifacts',
    r.JobArtifactsResource
)
app.add_resource('/users/<user_id>/builds', r.UserBuildsResource)
app.add_resource('/<path:path>', r.CatchallResource)
