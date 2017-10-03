import React, {Component} from 'react';
import PropTypes from 'prop-types';
// This is being pulled form the CDN currently
// import Raven from 'raven-js';

import Logo from '../assets/Logo';
import {Error404} from '../errors';

class ErrorBox extends Component {
  static propTypes = {
    title: PropTypes.string.isRequired,
    subtext: PropTypes.string
  };

  render() {
    return (
      <div style={{margin: 'auto', maxWidth: 600}}>
        <div
          style={{
            border: '10px solid #D6D4EA',
            margin: 20,
            padding: '20px 40px 20px'
          }}>
          {this.props.subtext
            ? <h1 style={{opacity: 0.2, float: 'right'}}>
                {this.props.subtext}
              </h1>
            : null}
          <h1>
            {this.props.title}
          </h1>
          {this.props.children}
        </div>
        <div style={{textAlign: 'center'}}>
          <a href="/">
            <Logo size="30" />
          </a>
        </div>
      </div>
    );
  }
}

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {error: null};
  }

  componentDidCatch(error, errorInfo) {
    this.setState({error});
    if (error.constructor !== Error404 && window.Raven) {
      window.Raven.captureException(error, {extra: errorInfo});
      window.Raven.lastEventId() && window.Raven.showReportDialog();
    }
  }

  render() {
    let {error} = this.state;
    if (error) {
      switch (error.constructor) {
        case Error404:
          return (
            <ErrorBox title="Not Found" subtext="404">
              <p>
                The resource you were trying to access was not found, or you do not have
                permission to view it.
              </p>
              <p>The following may provide you some recourse:</p>
              <ul>
                <li>
                  Wait a few seconds and{' '}
                  <a
                    onClick={() => {
                      window.location.href = window.location.href;
                    }}
                    style={{cursor: 'pointer'}}>
                    reload the page
                  </a>.
                </li>
                <li>
                  If you think this is a bug,{' '}
                  <a href="http://github.com/getsentry/zeus/issues">
                    create an issue
                  </a>{' '}
                  with more details.
                </li>
                <li>
                  Return to the <a href="/">dashboard</a>
                </li>
              </ul>
            </ErrorBox>
          );
        default:
          return (
            <ErrorBox title="Unhandled Error" subtext="500">
              <p>We hit an unexpected error while loading the page.</p>
              <p>The following may provide you some recourse:</p>
              <ul>
                <li>
                  Wait a few seconds and{' '}
                  <a
                    onClick={() => {
                      window.location.href = window.location.href;
                    }}
                    style={{cursor: 'pointer'}}>
                    reload the page
                  </a>.
                </li>
                <li>
                  If you think this is a bug,{' '}
                  <a href="http://github.com/getsentry/zeus/issues">
                    create an issue
                  </a>{' '}
                  with more details.
                </li>
              </ul>
              <div style={{fontSize: 0.8}}>
                <p>
                  {"For the curious, here's what Zeus reported:"}
                </p>
                <pre>
                  {error.toString()}
                </pre>
              </div>
            </ErrorBox>
          );
      }
    } else {
      return this.props.children;
    }
  }
}
