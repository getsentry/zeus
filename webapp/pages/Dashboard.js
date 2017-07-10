import React from 'react';

import AsyncComponent from '../components/AsyncComponent';
import Sidebar from '../components/Sidebar';

export default class Dashboard extends AsyncComponent {
  renderBody() {
    return (
      <div>
        <Sidebar />
        {this.props.children}
      </div>
    );
  }
}
