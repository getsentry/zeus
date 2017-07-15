import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import SidebarLink from './SidebarLink';

export default class SidebarProjectItem extends Component {
  static propTypes = {
    project: PropTypes.object.isRequired
  };

  render() {
    const {project} = this.props;
    return (
      <SidebarLink to={`/${project.organization.name}/${project.name}`}>
        <SidebarProjectItemWrapper>
          <SidebarProjectItemName>
            {project.organization.name}/{project.name}
          </SidebarProjectItemName>
          <SidebarProjectItemStatus result={project.result} />
        </SidebarProjectItemWrapper>
      </SidebarLink>
    );
  }
}

const SidebarProjectItemWrapper = styled.div`
  display: flex;
  align-items: center;
  height: 30px;
  position: relative;
`;

const SidebarProjectItemName = styled.div`
  flex: 1;
  padding-right: 5px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

const SidebarProjectItemStatus = styled.div`
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
