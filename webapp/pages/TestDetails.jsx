import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from '@rebass/grid/emotion';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import Collapsable from '../components/Collapsable';
import ListItemLink from '../components/ListItemLink';
import {AggregateDuration} from '../components/ObjectDuration';
import ObjectResult from '../components/ObjectResult';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';

class TestListItem extends Component {
  static propTypes = {
    test: PropTypes.object.isRequired,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired,
    params: PropTypes.object
  };

  constructor(props, context) {
    super(props, context);
    this.state = {expanded: false};
  }

  render() {
    let {build, repo, test} = this.props;
    let link = `/${repo.full_name}/builds/${build.number}`;
    return (
      <ListItemLink to={link}>
        <Row>
          <Column>
            <Flex>
              <Box width={15} mr={2}>
                <ObjectResult data={test} />
              </Box>
              <Box flex="1">
                #{build.number} &mdash; {build.label || ''}
              </Box>
            </Flex>
          </Column>
          <Column width={90} style={{textAlign: 'right'}} hide="sm">
            <AggregateDuration data={test.runs} />
          </Column>
        </Row>
      </ListItemLink>
    );
  }
}

export default class TestDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {testHash} = this.props.params;
    return [
      ['testDetails', `/repos/${repo.full_name}/tests/${testHash}`],
      ['testHistory', `/repos/${repo.full_name}/tests/${testHash}/history`]
    ];
  }

  renderBody() {
    let {testDetails, testHistory} = this.state;
    return (
      <Section>
        <SectionHeading>{testDetails.name}</SectionHeading>
        <ResultGrid>
          <Header>
            <Column>Build</Column>
            <Column width={90} textAlign="right">
              Duration
            </Column>
          </Header>
          <Collapsable
            collapsable={this.props.collapsable}
            maxVisible={this.props.maxVisible}>
            {testHistory.map(test => {
              return (
                <TestListItem
                  build={test.build}
                  repo={this.context.repo}
                  params={this.props.params}
                  test={test}
                  key={test.name}
                />
              );
            })}
          </Collapsable>
        </ResultGrid>
      </Section>
    );
  }
}
