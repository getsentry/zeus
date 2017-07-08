import React from 'react';

import AsyncComponent from './AsyncComponent';
import Sidebar from './Sidebar';

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
