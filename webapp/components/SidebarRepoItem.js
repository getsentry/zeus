import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled, {css} from 'styled-components';

export default class SidebarRepoItem extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired
  };

  render() {
    const {name, status} = {...this.props.repo};
    return (
      <SidebarRepoItemLink to={`/repos/${name}`}>
        <SidebarRepoItemName>
          {name}
        </SidebarRepoItemName>
        <SidebarRepoItemStatus status={status} />
      </SidebarRepoItemLink>
    );
  }
}

const SidebarRepoItemLink = styled(Link)`
  display: flex;
  align-items: center;
  height: 30px;
  color: #B9B6CE;
  position: relative;

  &:hover {
    color: #fff;
  }

  &.${props => props.activeClassName} {
    color: #fff;

    &:before {
      background: #7B6BE6;
      display: block;
      content: "";
      position: absolute;
      top: 0;
      left: -20px;
      right: -20px;
      bottom: 0;
      z-index: -1;
    }
  }
`;

SidebarRepoItemLink.defaultProps = {
  activeClassName: 'active'
};

const SidebarRepoItemName = styled.div`
  flex: 1;
  font-size: 14px;
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
