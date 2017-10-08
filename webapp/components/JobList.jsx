import React, {Component} from 'react';
import idx from 'idx';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import Badge from './Badge';
import ObjectDuration from './ObjectDuration';
import ObjectResult from './ObjectResult';
import Panel from './Panel';
import ResultGridHeader from './ResultGridHeader';
import ResultGridRow from './ResultGridRow';

export default class JobList extends Component {
  static propTypes = {
    jobList: PropTypes.arrayOf(PropTypes.object).isRequired,
    build: PropTypes.object.isRequired
  };

  render() {
    let {build} = this.props;
    return (
      <Panel>
        <ResultGridHeader>
          <Flex align="center">
            <Box flex="1" width={10 / 12} pr={15}>
              Job
            </Box>
            <Box width={1 / 12} style={{textAlign: 'center'}}>
              Tests
            </Box>
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              Duration
            </Box>
          </Flex>
        </ResultGridHeader>
        {this.props.jobList.map(job => {
          return (
            <ResultGridRow key={job.id}>
              <Flex align="center">
                <Box flex="1" width={10 / 12} pr={15}>
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
                        {job.allow_failure &&
                          <Badge type="warning">allowed to fail</Badge>}
                      </small>
                    </div>
                  </div>
                </Box>
                <Box width={1 / 12} style={{textAlign: 'center'}}>
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
                </Box>
                <Box width={1 / 12} style={{textAlign: 'right'}}>
                  <ObjectDuration data={job} short={true} />
                </Box>
              </Flex>
            </ResultGridRow>
          );
        })}
      </Panel>
    );
  }
}
