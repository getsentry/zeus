from aiohttp.web import Response, json_response
from functools import wraps
from flask import current_app
from uuid import UUID

import sentry_sdk

from zeus import auth
from zeus.exceptions import InvalidPublicKey, UnknownRevision
from zeus.utils.sentry import span

from .utils import get_vcs


def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def tmp():
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                current_app.logger.exception(str(e))
                raise

        return tmp()

    return wrapper


def api_request(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        @log_errors
        async def tmp():
            repo_id = request.query.get("repo_id")
            if not repo_id:
                return json_response({"error": "missing_arg"}, status=403)

            repo_id = UUID(repo_id)

            tenant = auth.get_tenant_from_headers(request.headers)
            if not tenant:
                return json_response({"error": "access_denied"}, status=401)

            if getattr(tenant, "user_id", None):
                with sentry_sdk.configure_scope() as scope:
                    scope.user = {"id": str(tenant.user_id)}

            if not tenant.has_permission(repo_id):
                current_app.logger.debug(
                    "vcs-server.invalid-request command=%s tenant=%s reason=invalid-repo",
                    func.__name__,
                    tenant,
                )
                return json_response({"error": "access_denied"}, status=401)

            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("repository_id", str(repo_id))

            current_app.logger.debug(
                "vcs-server.request repo_id=%s command=%s tenant=%s",
                repo_id,
                func.__name__,
                tenant,
            )

            async with request.app["db_pool"].acquire() as conn:
                vcs = await get_vcs(conn, repo_id)

            try:
                return await func(request, vcs, repo_id, *args, **kwargs)
            except InvalidPublicKey:
                current_app.logger.exception(
                    "vcs-server.invalid-pubkey repo_id=%s", repo_id
                )
                return json_response({"error": "invalid_pubkey"}, status=400)
            except UnknownRevision as exc:
                current_app.logger.info(
                    "vcs-server.invalid-revision repo_id=%s ref=%s",
                    repo_id,
                    exc.ref,
                    exc_info=True,
                )
                return json_response(
                    {"error": "invalid_ref", "ref": exc.ref}, status=400
                )
            except Exception:
                current_app.logger.exception(
                    "vcs-server.unhandled-error repo_id=%s", repo_id
                )
                return json_response({"error": "unknown_error"}, status=500)

        return tmp()

    return wrapper


@span("health_check")
@log_errors
async def health_check(request):
    return Response(text='{"ok": true}')


@span("stmt.log")
@api_request
@log_errors
async def stmt_log(request, vcs, repo_id):
    queue = request.app["queue"]

    parent = request.query.get("parent")
    branch = request.query.get("branch")
    offset = int(request.query.get("offset") or 0)
    limit = int(request.query.get("limit") or 100)

    try:
        log_results = list(
            vcs.log(parent=parent, branch=branch, offset=offset, limit=limit)
        )
    except UnknownRevision:
        # we're running a lazy update here if it didnt already exist
        log_results = vcs.log(
            parent=parent,
            branch=branch,
            offset=offset,
            limit=limit,
            update_if_exists=True,
        )

    results = []
    for revision in log_results:
        results.append(
            {
                "sha": revision.sha,
                "message": revision.message,
                "authors": revision.get_authors(),
                "author_date": revision.author_date.isoformat(),
                "committer": revision.get_committer(),
                "committer_date": (
                    revision.committer_date or revision.author_date
                ).isoformat(),
                "parents": revision.parents,
            }
        )
        # XXX(dcramer): we could wait until the revisions are confirmed to exist in the db
        await queue.put(["revision", {"repo_id": repo_id, "revision": revision}])

    return json_response({"log": results})


@span("stmt.export")
@api_request
@log_errors
async def stmt_export(request, vcs, repo_id):
    sha = request.query.get("sha")
    if not sha:
        return json_response({"error": "missing_arg"}, status=403)

    return json_response({"export": vcs.export(sha)})


@span("stmt.show")
@api_request
@log_errors
async def stmt_show(request, vcs, repo_id):
    sha = request.query.get("sha")
    if not sha:
        return json_response({"error": "missing_arg"}, status=403)
    filename = request.query.get("filename")
    if not filename:
        return json_response({"error": "missing_arg"}, status=403)

    return json_response({"show": vcs.show(sha, filename)})


@span("stmt.branches")
@api_request
@log_errors
async def stmt_branches(request, vcs, repo_id):
    return json_response({"branches": vcs.get_known_branches()})


def register_api_routes(app):
    app.router.add_route("GET", "/stmt/branches", stmt_branches)
    app.router.add_route("GET", "/stmt/export", stmt_export)
    app.router.add_route("GET", "/stmt/log", stmt_log)
    app.router.add_route("GET", "/stmt/show", stmt_show)
    app.router.add_route("GET", "/healthz", health_check)
