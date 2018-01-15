from flask import current_app
import json

from zeus.constants import Result
from zeus.utils.testresult import TestResult, TestResultManager

from .base import ArtifactHandler


class GoTestHandler(ArtifactHandler):
    supported_types = frozenset(['application/x-gotest+json'])

    def process(self, fp):
        test_list = self.get_tests(fp)

        manager = TestResultManager(self.job)
        manager.clear()
        manager.save(test_list)

        return test_list

    def get_tests(self, fp):
        job = self.job

        results = []

        actionToResult = {
            'pass': Result.passed,
            'fail': Result.failed,
        }
        last_output = {}
        for lineno, line in enumerate(fp.readlines()):
            # Format at https://tip.golang.org/cmd/test2json/
            try:
                event = json.loads(line)
            except Exception:
                current_app.logger.exception(
                    'Failed to parse JSON on line %d', lineno + 1)
                return []

            if 'Test' not in event:
                continue

            key = (event.get('Package'), event['Test'])
            output = event.get('Output') or last_output.get(key)
            if output:
                last_output[key] = output

            result = actionToResult.get(event['Action'])
            if result is None:
                continue
            results.append(TestResult(
                job=job,
                name=event['Test'],
                message=output if result == Result.failed else None,
                package=event.get('Package'),
                result=result,
                duration=int(event['Elapsed'] * 1000),
            ))

        return results
