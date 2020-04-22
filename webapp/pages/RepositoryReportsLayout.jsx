import React from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from '@rebass/grid/emotion';

import AsyncPage from '../components/AsyncPage';
import ListLink from '../components/ListLink';

export default class RepositoryReportsLayout extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    let {repo} = this.context;
    return (
      <Flex>
        <Box flex="0 0 10em">
          <ul>
            <ListLink to={`/${repo.full_name}/reports`}>Overview</ListLink>
            <ListLink to={`/${repo.full_name}/reports/coverage`}>Code Coverage</ListLink>
            <ListLink to={`/${repo.full_name}/reports/tests`}>Tests</ListLink>
          </ul>
        </Box>
        <Box flex="1">{this.props.children}</Box>
      </Flex>
    );
  }
}
