import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

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
                  <ObjectResult data={job} />
                  #{build.number}.{job.number}
                  {job.url &&
                    <span>
                      {' '}&mdash; <a href={job.url}>{job.url}</a>
                    </span>}
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
