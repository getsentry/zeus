import React, {Component} from 'react';
import {Link} from 'react-router';
import styled from '@emotion/styled';

class UnstyledFooter extends Component {
  render() {
    let props = this.props;
    let release = window.ZEUS_RELEASE ? window.ZEUS_RELEASE.substr(0, 14) : 'unknown';
    return (
      <div className={props.className}>
        <div>
          <a
            href="https://github.com/getsentry/zeus"
            style={{color: 'inherit', fontWeight: 500}}>
            Zeus
          </a>{' '}
          is Open Source Software
          <br />
          <small>
            Build {release} &mdash; <Link to="/install">Install Overview</Link>
          </small>
        </div>
        {props.children}
        <div style={{clear: 'both'}} />
      </div>
    );
  }
}

export default styled(UnstyledFooter)`
  text-align: center;
  color: #333;
  font-size: 0.8em;
  padding: 20px 0;
  background: #fff;
`;
