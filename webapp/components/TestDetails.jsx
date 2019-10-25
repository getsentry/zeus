import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import {Client} from '../api';

import ObjectResult from './ObjectResult';

const TestDetailsWrapper = styled.div`
  margin-top: 10px;
  padding: 5px 0 0 25px;
  color: #39364e;
  font-size: 12px;
  line-height: 1.4em;
  border-top: 1px solid #eee;

  pre {
    font-size: inherit;
    margin: 0;
    background: #f9f9f9;
    padding: 5px;
    border-radius: 4px;
  }

  h5 {
    margin-bottom: 5px;
    font-size: 13px;
  }
`;

export default class TestDetails extends Component {
  static propTypes = {
    test: PropTypes.object.isRequired,
    build: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {loading: true};
    this.api = new Client();
  }

  componentDidMount() {
    let {test} = this.props;
    this.api.request(`/tests/${test.id}`).then(testDetails => {
      this.setState({loading: false, testDetails});
    });
  }

  componentWillUnmount() {
    this.api.clear();
  }

  // TODO(dcramer): make this more useful
  render() {
    let {build} = this.props;
    if (this.state.loading) return <TestDetailsWrapper>(loading)</TestDetailsWrapper>;
    let {testDetails} = this.state;
    return (
      <TestDetailsWrapper>
        <h5>
          <ObjectResult data={testDetails} size={12} />#{build.number}.
          {testDetails.job.number}
          {testDetails.job.label && ` - ${testDetails.job.label}`}
        </h5>
        <pre>{testDetails.message || <em>no output captured</em>}</pre>
      </TestDetailsWrapper>
    );
  }
}
