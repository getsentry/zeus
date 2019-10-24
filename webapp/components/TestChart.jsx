import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Collapsable from './Collapsable';
import {ResultGrid, Column, Header} from './ResultGrid';

export default class TestChart extends Component {
  static propTypes = {
    testList: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number,
    params: PropTypes.object
  };

  static defaultProps = {
    collapsable: false
  };

  render() {
    return (
      <ResultGrid>
        <Header>
          <Column>Tests</Column>
        </Header>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          <ResultRow jobs={this.props.testList.jobs.length}>
            {Object.entries(this.props.testList.results).map(([test, results]) => {
              return (
                <React.Fragment key={test}>
                  {test}
                  {results.map((result, i) => (
                    <ResultBox key={i} result={result} />
                  ))}
                </React.Fragment>
              );
            })}
          </ResultRow>
        </Collapsable>
      </ResultGrid>
    );
  }
}

const ResultRow = styled('div')`
  display: grid;
  grid-gap: 4px;
  grid-template-columns: max-content repeat(${p => p.jobs}, max-content);
`;

const ResultBox = styled('div')`
  width: 24px;
  height: 24px;
  background-color: ${p =>
    p.result === 1 ? 'green' : p.result === null ? '#ccc' : 'red'};
`;
