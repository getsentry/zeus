import React, {Component} from 'react';
import {Link} from 'react-router';
import styled from 'styled-components';

export default class BuildList extends Component {
  render() {
    return (
      <BuildListWrapper>
        <BuildListHeader>
          <RepositoryName>getsentry/sentry</RepositoryName>
          <TabbedNav>
            <TabbedNavItem to="/" activeNavClass="active">My builds</TabbedNavItem>
            <TabbedNavItem>All builds</TabbedNavItem>
          </TabbedNav>
        </BuildListHeader>
      </BuildListWrapper>
    );
  }
}

const BuildListWrapper = styled.div`
  position: fixed;
  top: 0;
  left: 220px;
  bottom: 0;
  width: 380px;
  background: #F8F9FB;
  border-right: 1px solid #DBDAE3;
`;

const BuildListHeader = styled.div`
  background: #fff;
  padding: 15px 20px 0;
  box-shadow: inset 0 -1px 0 #DBDAE3;
`;

const RepositoryName = styled.div`
  font-size: 22px;
`;

const TabbedNav = styled.div`
  overflow: hidden;
`;

const TabbedNavItem = styled(Link)`
  cursor: pointer;
  float: left;
  font-size: 15px;
  color: #AAA7BB;
  margin-right: 20px;
  padding: 15px 0;
  border-bottom: 3px solid transparent;

  &.${(props) => props.activeClassName} {
    color: #39364E;
    border-bottom: 3px solid #7B6BE6;
  }
`;

TabbedNavItem.defaultProps = {
  activeClassName: 'active',
};
