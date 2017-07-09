from flask import current_app, request

from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Build, Repository, TestCase, Job, Source
from zeus.utils.trees import build_tree

from .base import Resource


class RepositoryTestTreeResource(Resource):
    def get(self, repository_name: str):
        """
        Return a tree of testcases for the given repository.
        """
        repo = Repository.query.filter(Repository.name == repository_name).first()
        if not repo:
            return self.not_found()

        parent = request.args.get('parent')

        latest_build = Build.query.join(
            Source,
            Source.id == Build.source_id,
        ).filter(
            Source.patch_id == None,  # NOQA
            Build.repository_id == repo.id,
            Build.result == Result.passed,
            Build.status == Status.finished,
        ).order_by(
            Build.date_created.desc(),
        ).first()

        if not latest_build:
            current_app.logger.info('no successful builds found for repository')
            return self.respond({})

        job_list = db.session.query(Job.id).filter(
            Job.build_id == latest_build.id,
        )

        # use the most completed build to fetch test results
        test_list = db.session.query(TestCase.name, TestCase.duration).filter(
            TestCase.job_id.in_(job_list),
        )
        if parent:
            test_list = test_list.filter(
                TestCase.name.startswith(parent),
            )
        test_list = list(test_list)

        if test_list:
            sep = TestCase(name=test_list[0][0]).sep

            groups = build_tree(
                [t[0] for t in test_list],
                sep=sep,
                min_children=2,
                parent=parent,
            )

            results = []
            for group in groups:
                num_tests = 0
                total_duration = 0
                for name, duration in test_list:
                    if name == group or name.startswith(group + sep):
                        num_tests += 1
                        total_duration += duration

                if parent:
                    name = group[len(parent) + len(sep):]
                else:
                    name = group
                data = {
                    'name': name,
                    'path': group,
                    'totalDuration': total_duration,
                    'numTests': num_tests,
                }
                results.append(data)
            results.sort(key=lambda x: x['totalDuration'], reverse=True)

            trail = []
            context = []
            if parent:
                for chunk in parent.split(sep):
                    context.append(chunk)
                    trail.append({
                        'path': sep.join(context),
                        'name': chunk,
                    })
        else:
            results = []
            trail = []

        return {
            'groups': results,
            'trail': trail,
        }
