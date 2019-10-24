import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import {Header} from './ResultGrid';

export default class TestChart extends Component {
  static propTypes = {
    testList: PropTypes.shape({
      builds: PropTypes.object,
      results: PropTypes.object
    }),
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number,
    params: PropTypes.object
  };

  static defaultProps = {
    collapsable: false
  };

  render() {
    const buildsList = Object.entries(this.props.testList.builds);

    return (
      <ResultRow builds={buildsList.length}>
        <Header>Test</Header>
        {buildsList.map(([id, build]) => (
          <Header key={id}>
            <BuildLink
              href={build.url}
              title={`${build.label} finished at ${build.finished_at}`}>
              i
            </BuildLink>
          </Header>
        ))}

        {Object.entries(this.props.testList.results).map(([test, results]) => {
          return (
            <React.Fragment key={test}>
              <TestName title={test}>{test}</TestName>
              {results.map((result, i) => (
                <ResultBox key={i} result={result} />
              ))}
            </React.Fragment>
          );
        })}
      </ResultRow>
    );
  }
}

const ResultRow = styled('div')`
  display: grid;
  grid-gap: 4px;
  align-items: center;
  grid-template-columns: auto repeat(${p => p.builds}, max-content);
`;

const ResultBox = styled('div')`
  width: 24px;
  height: 24px;
  background-color: ${p =>
    p.result === 'passed' ? 'green' : p.result === null ? '#ccc' : 'red'};
`;

const BuildLink = styled('a')`
  display: flex;
  justify-content: center;
  text-transform: none;
  width: 100%;
  color: #999;
`;

const TestName = styled('span')`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;
