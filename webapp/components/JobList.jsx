import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import Badge from './Badge';
import ObjectDuration from './ObjectDuration';
import ObjectResult from './ObjectResult';
import Panel from './Panel';
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
        {this.props.jobList.map(job => {
          return (
            <ResultGridRow key={job.id}>
              <Flex align="center">
                <Box flex="1" width={11 / 12} pr={15}>
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
