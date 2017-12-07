from marshmallow import Schema, fields, pre_dump
from sqlalchemy.orm import joinedload, subqueryload_all
from typing import List

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Build, Repository, RepositoryBackend, Source

from .fields import EnumField


class RepositorySchema(Schema):
    id = fields.UUID(dump_only=True)
    owner_name = fields.Str()
    name = fields.Str()
    url = fields.Str()
    provider = fields.Str()
    backend = EnumField(RepositoryBackend)
    created_at = fields.DateTime(
        attribute='date_created',
        dump_only=True,
    )
    full_name = fields.Method('get_full_name')
    latest_build = fields.Nested('BuildSchema', exclude=('repository',))

    @pre_dump(pass_many=True)
    def process_latest_build(self, data, many):
        if many:
            latest_builds = get_latest_builds(data, Result.passed)
            for repo in data:
                repo.latest_build = latest_builds.get(repo.id)
        else:
            latest_builds = get_latest_builds([data], Result.passed)
            data.latest_build = latest_builds.get(data.id)
        return data

    def get_full_name(self, obj):
        return '{}/{}/{}'.format(obj.provider, obj.owner_name, obj.name)


def get_latest_builds(repo_list: List[Repository], result: Result):
    # TODO(dcramer): this should find the 'last build in [default branch]'
    if not repo_list:
        return {}

    build_query = db.session.query(
        Build.id,
    ).join(
        Source, Build.source_id == Source.id,
    ).filter(
        Source.patch_id == None,  # NOQA
        Build.status == Status.finished,
        Build.result == result,
    ).order_by(
        Build.date_created.desc(),
    )

    build_map = dict(db.session.query(
        Repository.id,
        build_query.filter(
            Build.repository_id == Repository.id,
        ).limit(1).as_scalar(),
    ).filter(
        Repository.id.in_(r.id for r in repo_list),
    ))

    if not build_map:
        return {}

    return {
        b.repository_id: b for b in Build.query.unrestricted_unsafe().filter(
            Build.id.in_(build_map.values()),
        ).options(
            joinedload('source'),
            joinedload('source').joinedload('author'),
            joinedload('source').joinedload('revision'),
            joinedload('source').joinedload('patch'),
            subqueryload_all('stats'),
        )
    }
