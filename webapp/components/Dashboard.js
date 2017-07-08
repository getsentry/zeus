import React, {Component} from 'react';

import Sidebar from './Sidebar';
import BuildList from './BuildList';
import BuildDetails from './BuildDetails';

export default class Dashboard extends Component {
  render() {
    return (
      <div>
        <Sidebar />
        <BuildList />
        <BuildDetails />
      </div>
    );
  }
}
