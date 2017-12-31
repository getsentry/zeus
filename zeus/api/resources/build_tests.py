import re

from flask import request
from sqlalchemy.sql import func
from sqlalchemy.types import String, TypeDecorator
from sqlalchemy.dialects.postgresql import array_agg

from zeus.config import db
from zeus.constants import Result
from zeus.models import Job, Build, TestCase

from .base_build import BaseBuildResource
from ..schemas import AggregateTestCaseSummarySchema

testcases_schema = AggregateTestCaseSummarySchema(many=True, strict=True)


# https://bitbucket.org/zzzeek/sqlalchemy/issues/3729/using-array_agg-around-row-function-does
class ArrayOfRecord(TypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        elems = re.match(r"^\{(\".+?\")*\}$", value).group(1)
        elems = [e for e in re.split(r'"(.*?)",?', elems) if e]
        return [tuple(
            re.findall(r'[^\(\),]+', e)
        ) for e in elems]


def array_agg_row(*arg):
    return func.array_agg(func.row(*arg), type_=ArrayOfRecord)


class BuildTestsResource(BaseBuildResource):
    def get(self, build: Build):
        """
        Return a list of test cases for a given build.
        """
        job_ids = db.session.query(Job.id).filter(
            Job.build_id == build.id,
        ).subquery()

        query = db.session.query(
            TestCase.hash,
            TestCase.name,
            array_agg_row(TestCase.id, TestCase.job_id, TestCase.duration,
                          TestCase.result).label('runs'),
        ).filter(
            TestCase.job_id.in_(job_ids),
        ).group_by(TestCase.hash, TestCase.name)

        result = request.args.get('result')
        if result:
            try:
                query = query.filter(
                    TestCase.result == getattr(Result, result))
            except AttributeError:
                raise NotImplementedError

        query = query.order_by(
            (array_agg(TestCase.result).label('results').contains([Result.failed])).desc(), TestCase.name.asc())

        return self.paginate_with_schema(testcases_schema, query)
