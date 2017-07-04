import React, {Component} from 'react';
import styled from 'styled-components';

import Sidebar from './Sidebar';
import BuildList from './BuildList';
import BuildDetails from './BuildDetails';

export default class Dashboard extends Component {
  render() {
    return (
      <DashboardWrapper>
        <Sidebar />
        <BuildList />
        <BuildDetails/>
      </DashboardWrapper>
    );
  }
}

const DashboardWrapper = styled.div`

`;
