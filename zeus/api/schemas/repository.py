from marshmallow import Schema, fields, post_load, pre_dump
from sqlalchemy.orm import joinedload, subqueryload_all
from typing import List

from zeus.config import db
from zeus.constants import Permission, Result, Status
from zeus.models import Build, Repository, RepositoryAccess, RepositoryBackend

from .fields import EnumField


class PermissionSchema(Schema):
    read = fields.Bool()
    write = fields.Bool()
    admin = fields.Bool()


class RepositorySchema(Schema):
    id = fields.UUID(dump_only=True)
    owner_name = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    provider = fields.Str(dump_only=True)
    backend = EnumField(RepositoryBackend, dump_only=True)
    created_at = fields.DateTime(attribute="date_created", dump_only=True)
    full_name = fields.Method("get_full_name", dump_only=True)
    latest_build = fields.Nested("BuildSchema", exclude=("repository",), dump_only=True)
    public = fields.Bool()
    permissions = fields.Nested(PermissionSchema, allow_none=True, dump_only=True)

    @pre_dump(pass_many=True)
    def process_permission(self, data, many, **kwargs):
        user = self.context.get("user")
        if not user:
            return data

        if not many:
            items = [data]
        else:
            items = data

        access = dict(
            db.session.query(
                RepositoryAccess.repository_id, RepositoryAccess.permission
            ).filter(
                RepositoryAccess.user_id == user.id,
                RepositoryAccess.repository_id.in_([i.id for i in items]),
            )
        )
        for item in items:
            permission = access.get(item.id) or Permission.none
            item.permissions = {
                "read": Permission.read in permission,
                "write": Permission.write in permission,
                "admin": Permission.admin in permission,
            }
        return data

    @pre_dump(pass_many=True)
    def process_latest_build(self, data, many, **kwargs):
        if "latest_build" not in self.exclude:
            if many:
                latest_builds = get_latest_builds(data, Result.passed)
                for repo in data:
                    repo.latest_build = latest_builds.get(repo.id)
            else:
                latest_builds = get_latest_builds([data], Result.passed)
                data.latest_build = latest_builds.get(data.id)
        return data

    @post_load
    def make_instance(self, data, **kwargs):
        if self.context.get("repository"):
            obj = self.context["repository"]
            for key, value in data.items():
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
        else:
            obj = Repository(**data)
        return obj

    def get_full_name(self, obj):
        return "{}/{}/{}".format(obj.provider, obj.owner_name, obj.name)


def get_latest_builds(repo_list: List[Repository], result: Result):
    # TODO(dcramer): this should find the 'last build in [default branch]'
    if not repo_list:
        return {}

    build_query = (
        db.session.query(Build.id)
        .filter(Build.status == Status.finished, Build.result == result)
        .order_by(Build.date_created.desc())
    )

    build_map = dict(
        db.session.query(
            Repository.id,
            build_query.filter(Build.repository_id == Repository.id)
            .limit(1)
            .as_scalar(),
        ).filter(Repository.id.in_(r.id for r in repo_list))
    )

    if not build_map:
        return {}

    return {
        b.repository_id: b
        for b in Build.query.unrestricted_unsafe()
        .filter(Build.id.in_(build_map.values()))
        .options(
            joinedload("author"), joinedload("revision"), subqueryload_all("stats")
        )
    }
