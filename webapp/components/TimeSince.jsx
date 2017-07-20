import React, {Component} from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';

export default class TimeSince extends Component {
  static propTypes = {
    date: PropTypes.any.isRequired,
    suffix: PropTypes.string,
    clock24Hours: PropTypes.bool
  };

  static defaultProps = {
    suffix: 'ago',
    clock24Hours: false
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      relative: this.getRelativeDate()
    };
  }

  componentDidMount() {
    this.setRelativeDateTicker();
  }

  componentWillUnmount() {
    if (this.ticker) {
      clearTimeout(this.ticker);
      this.ticker = null;
    }
  }

  setRelativeDateTicker() {
    const ONE_MINUTE_IN_MS = 60000;

    this.ticker = setTimeout(() => {
      this.setState({
        relative: this.getRelativeDate()
      });
      this.setRelativeDateTicker();
    }, ONE_MINUTE_IN_MS);
  }

  getRelativeDate() {
    let date = new Date(this.props.date);
    if (!this.props.suffix) {
      return moment(date).fromNow(true);
    } else if (this.props.suffix === 'ago') {
      return moment(date).fromNow();
    } else if (this.props.suffix == 'old') {
      return `${moment(date).fromNow(true)} old`;
    } else {
      throw new Error('Unsupported time format suffix');
    }
  }

  render() {
    let date = new Date(this.props.date);
    let format = this.props.clock24Hours ? 'MMMM D YYYY HH:mm:ss z' : 'LLL z';

    return (
      <time
        dateTime={date.toISOString()}
        title={moment(date).format(format)}
        className={this.props.className}>
        {this.state.relative}
      </time>
    );
  }
}
