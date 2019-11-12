import React, {Component} from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';

import {Header} from './ResultGrid';

export default class TestChart extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    results: PropTypes.shape({
      builds: PropTypes.object,
      tests: PropTypes.array
    }),
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number,
    params: PropTypes.object
  };

  static defaultProps = {
    collapsable: false
  };

  render() {
    const buildsList = this.props.results.builds;
    const {repo} = this.props;

    return (
      <ResultRow builds={buildsList.length}>
        <Header>Test</Header>
        {buildsList.map(build => (
          <Header key={build.id}>
            <BuildLink
              href={build.url}
              title={`${build.label} finished at ${build.finished_at}`}>
              i
            </BuildLink>
          </Header>
        ))}

        {this.props.results.tests.map(({name, hash, results}) => {
          return (
            <React.Fragment key={hash}>
              <Link to={`/${repo.full_name}/tests/${hash}`}>
                <TestName title={name}>{name}</TestName>
              </Link>

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
  margin-bottom: 20px;
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
