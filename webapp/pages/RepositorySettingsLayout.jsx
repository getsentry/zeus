import React from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import AsyncPage from '../components/AsyncPage';
import ListLink from '../components/ListLink';

export default class RepositorySettingsLayout extends AsyncPage {
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
            <ListLink to={`/${repo.full_name}/settings`}>General</ListLink>
            <ListLink to={`/${repo.full_name}/settings/hooks`}>Hooks</ListLink>
          </ul>
        </Box>
        <Box flex="1">{this.props.children}</Box>
      </Flex>
    );
  }
}
