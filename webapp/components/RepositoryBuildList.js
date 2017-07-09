import React, {Component} from 'react';

import Sidebar from './Sidebar';
import BuildList from './BuildList';

export default class RepositoryBuildList extends Component {
  render() {
    return (
      <div>
        <Sidebar params={this.props.params} />
        <BuildList params={this.props.params} />
      </div>
    );
  }
}
