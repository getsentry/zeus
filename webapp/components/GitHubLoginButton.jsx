import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Button from './Button';

export default class GitHubLoginButton extends Component {
  static propTypes = {
    url: PropTypes.string,
    next: PropTypes.string,
    text: PropTypes.string
  };

  static defaultProps = {
    url: '/auth/github',
    text: 'Login with GitHub'
  };

  render() {
    let {url, next, text} = this.props;
    let fullUrl = next
      ? url.indexOf('?') !== -1
        ? `${url}&next=${window.encodeURIComponent(next)}`
        : `${url}?next=${window.encodeURIComponent(next)}`
      : url;
    return (
      <Button href={fullUrl} size="large">
        {text}
      </Button>
    );
  }
}
