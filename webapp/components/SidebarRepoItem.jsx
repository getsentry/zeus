import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import SidebarLink from './SidebarLink';

export default class SidebarRepoItem extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired
  };

  render() {
    let {repo} = this.props;
    return (
      <SidebarLink to={`/${repo.owner_name}/${repo.name}`}>
        <SidebarRepoItemWrapper>
          <SidebarRepoItemName>
            {repo.owner_name}/{repo.name}
          </SidebarRepoItemName>
          <SidebarRepoItemStatus result={repo.result} />
        </SidebarRepoItemWrapper>
      </SidebarLink>
    );
  }
}

const SidebarRepoItemWrapper = styled.div`
  display: flex;
  align-items: center;
  height: 30px;
  position: relative;
`;

const SidebarRepoItemName = styled.div`
  flex: 1;
  padding-right: 5px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

const SidebarRepoItemStatus = styled.div`
  width: 10px;
  height: 10px;
  border-radius: 10px;

  ${props => {
    switch (props.result) {
      case 'passed':
        return css`
          background-color: #76D392;
        `;
      case 'failed':
        return css`
          background-color: #F06E5B;
        `;
      default:
        return css``;
    }
  }};
`;
