import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Duration from './Duration';

export default class BuildDuration extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired
  };

  getDuration(build) {
    if (!build.finished_at) {
      if (build.started_at) {
        return new Date().getTime() - new Date(build.started_at).getTime();
      }
      return null;
    }
    return new Date(build.finished_at).getTime() - new Date(build.started_at).getTime();
  }

  render() {
    let duration = this.getDuration(this.props.build);
    if (duration === null) return null;
    return <Duration ms={duration} {...this.props} />;
  }
}
