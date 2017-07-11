from flask import jsonify, request
from marshmallow import fields, Schema

from zeus.api.schemas import BuildSchema, JobSchema
from zeus.config import db
from zeus.models import Build, HookToken, Job
from zeus.tasks import aggregate_build_stats_for_job


class BuildExternalSchema(BuildSchema):
    external_id = fields.Str(required=True)


class JobExternalSchema(JobSchema):
    external_id = fields.Str(required=True)


class JobHookSchema(Schema):
    provider = fields.Str(required=True)
    build = fields.Nested(BuildExternalSchema, required=True)
    job = fields.Nested(JobExternalSchema, required=True)


schema = JobHookSchema(strict=True)


def job_hook(token_id, signature):
    if request.method != 'POST':
        return '', 405

    hook_token = HookToken.query.unrestricted_unsafe().get(token_id)
    if not hook_token.is_valid_signature(signature):
        return '', 403

    # we allow a partial load, but might need to enforce behavior later
    result = schema.load(request.get_json() or {}, partial=True)
    if result.errors:
        return jsonify(result.errors), 403

    data = result.data

    build = Build.query.filter(
        Build.repository_id == hook_token.repository_id,
        Build.provider == data['provider'],
        Build.external_id == data['build']['external_id'],
    ).first()
    if not build:
        build = Build(
            repository_id=hook_token.repository_id,
            provider=data['provider'],
            **data['build'],
        )
    else:
        for key, value in data['build'].items():
            if getattr(build, key) != value:
                setattr(build, key, value)
        if db.session.is_modified(build):
            db.session.add(build)
            db.session.flush()

    job = Job.query.filter(
        Job.repository_id == hook_token.repository_id,
        # the constraint isnt on Build.id, so its possible for this to
        # fail hard
        Job.build_id == build.id,
        Job.provider == data['provider'],
        Job.external_id == data['job']['external_id'],
    ).first()
    if not job:
        job = Job(
            repository_id=hook_token.repository_id,
            build_id=build.id,
            provider=data['provider'],
            **data['job']
        )
    else:
        for key, value in data['job'].items():
            if getattr(job, key) != value:
                setattr(job, key, value)
        if db.session.is_modified(job):
            db.session.add(job)
            db.session.commit()

            aggregate_build_stats_for_job.delay(job_id=job.id)

    db.session.commit()

    return jsonify(schema.dumps(job))
