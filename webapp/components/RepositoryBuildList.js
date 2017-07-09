import React, {Component} from 'react';

import Sidebar from './Sidebar';
import BuildList from './BuildList';

export default class RepositoryBuildList extends Component {
  render() {
    return (
      <div>
        <Sidebar />
        <BuildList />
      </div>
    );
  }
}
