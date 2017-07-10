import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import SidebarLink from './SidebarLink';

export default class SidebarRepoItem extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired
  };

  render() {
    const {name, status} = {...this.props.repo};
    return (
      <SidebarLink to={`/repos/${name}`}>
        <SidebarRepoItemWrapper>
          <SidebarRepoItemName>
            {name}
          </SidebarRepoItemName>
          <SidebarRepoItemStatus status={status} />
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
    switch (props.status) {
      case 'pass':
        return css`
          background-color: #76D392;
        `;
      case 'fail':
        return css`
          background-color: #F06E5B;
        `;
      default:
        return css``;
    }
  }};
`;
