import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Duration from './Duration';

export default class BuildDuration extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired
  };

  getDuration(build) {
    if (!build.finished_at && build.started_at) {
      return new Date().getTime() - new Date(build.finished_at).getTime();
    }
    return new Date(build.finished_at).getTime() - new Date(build.started_at).getTime();
  }

  render() {
    return <Duration ms={this.getDuration(this.props.build)} {...this.props} />;
  }
}
