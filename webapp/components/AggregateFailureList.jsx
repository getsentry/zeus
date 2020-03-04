import React, {Component} from 'react';
import PropTypes from 'prop-types';

const failureReasonToDescription = function(reason) {
  switch (reason) {
    case 'failing_tests':
      return 'There were test failures.';
    case 'missing_tests':
      return 'No test results were found.';
    case 'no_jobs':
      return 'No jobs were found.';
    case 'unresolvable_ref':
      return 'Unable to resolve commit ref';
    default:
      return `Unrecognized reason: '${reason}'.`;
  }
};

export default class AggregateFailureList extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired,
    failureList: PropTypes.arrayOf(
      PropTypes.shape({
        reason: PropTypes.string.isRequired,
        runs: PropTypes.arrayOf(
          PropTypes.shape({
            id: PropTypes.string.isRequired,
            job_id: PropTypes.string
          })
        )
      })
    ).isRequired
  };

  render() {
    return (
      <ul>
        {this.props.failureList.map(failure => {
          return (
            <li key={failure.reason}>{failureReasonToDescription(failure.reason)}</li>
          );
        })}
      </ul>
    );
  }
}
