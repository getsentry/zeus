import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Duration from './Duration';

const ONE_MINUTE_IN_MS = 60000;

export default class BuildDuration extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      duration: this.getDuration(props.build)
    };
  }

  componentDidMount() {
    this.setDurationTicker();
  }

  componentWillUnmount() {
    if (this.ticker) {
      clearTimeout(this.ticker);
      this.ticker = null;
    }
  }

  setDurationTicker() {
    let {build} = this.props;

    if (!build.finished_at) {
      this.ticker = setTimeout(() => {
        this.setState({
          duration: this.getDuration()
        });
        this.setDurationTicker();
      }, ONE_MINUTE_IN_MS);
    }
  }

  getDuration(build) {
    if (!build) build = this.props.build;
    if (!build.finished_at) {
      if (build.started_at) {
        return new Date().getTime() - new Date(build.started_at).getTime();
      }
      return null;
    }
    return new Date(build.finished_at).getTime() - new Date(build.started_at).getTime();
  }

  render() {
    let {duration} = this.state;
    if (duration === null) return null;
    return <Duration ms={duration} {...this.props} />;
  }
}
