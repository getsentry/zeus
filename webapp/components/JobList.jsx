import React, {Component} from 'react';
import idx from 'idx';
import PropTypes from 'prop-types';

import Badge from './Badge';
import ObjectDuration from './ObjectDuration';
import ObjectResult from './ObjectResult';
import {ResultGrid, Column, Header, Row} from './ResultGrid';

export default class JobList extends Component {
  static propTypes = {
    jobList: PropTypes.arrayOf(PropTypes.object).isRequired,
    build: PropTypes.object.isRequired
  };

  render() {
    let {build} = this.props;
    return (
      <ResultGrid>
        <Header>
          <Column>Job</Column>
          <Column width={80} textAlign="center">
            Tests
          </Column>
          <Column width={80} textAlign="right">
            Duration
          </Column>
        </Header>
        {this.props.jobList.map(job => {
          return (
            <Row key={job.id}>
              <Column>
                <div style={{position: 'absolute'}}>
                  <ObjectResult data={job} />
                </div>
                <div style={{display: 'inline-block', marginLeft: 25}}>
                  <div>
                    #{build.number}.{job.number}
                    {job.label && ` - ${job.label}`}
                  </div>
                  <div>
                    <small>
                      {job.url &&
                        <a href={job.url}>
                          {job.url}
                        </a>}
                      {job.allow_failure && <Badge type="warning">allowed to fail</Badge>}
                    </small>
                  </div>
                </div>
              </Column>
              <Column width={80} textAlign="center">
                {idx(job.stats, _ => _.tests.count) > 0
                  ? <div>
                      {job.stats.tests.count.toLocaleString()}
                    </div>
                  : null}
                {idx(job.stats, _ => _.tests.failures) > 0
                  ? <small>
                      {job.stats.tests.failures.toLocaleString()} failed
                    </small>
                  : null}
              </Column>
              <Column width={80} textAlign="right">
                <ObjectDuration data={job} short={true} />
              </Column>
            </Row>
          );
        })}
      </ResultGrid>
    );
  }
}
