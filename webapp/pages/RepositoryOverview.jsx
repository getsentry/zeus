import React, {Component} from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import moment from 'moment';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';
import {Line as LineChart} from 'react-chartjs-2';
import ViewAllIcon from 'react-icons/lib/md/input';

import {loadRevisionsForRepository} from '../actions/revisions';
import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import RevisionList from '../components/RevisionList';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import {getDuration} from '../utils/duration';
import {getSize} from '../utils/fileSize';

class GenericLineChart extends Component {
  static propTypes = {
    data: PropTypes.array.isRequired,
    formatValue: PropTypes.func.isRequired,
    label: PropTypes.string.isRequired
  };

  render() {
    let {data, formatValue, label} = this.props;
    let labels = [];
    let values = [];
    data.reverse().forEach(({time, value}) => {
      labels.push(moment(time).toDate());
      values.push(value);
    });
    return (
      <LineChart
        data={{
          labels: labels,
          datasets: [
            {
              label: label,
              borderColor: '#7b6be6',
              data: values,
              fill: false
            }
          ]
        }}
        options={{
          responsive: true,
          title: false,
          legend: {display: false},
          scales: {
            xAxes: [
              {
                type: 'time',
                time: {
                  tooltipFormat: 'll'
                },
                ticks: {
                  display: false
                }
              }
            ],
            yAxes: [
              {
                scaleLabel: {display: false},
                ticks: {
                  beginAtZero: true,
                  userCallback: formatValue
                }
              }
            ]
          }
        }}
        height="100"
      />
    );
  }
}

class CoverageChart extends AsyncPage {
  getEndpoints({repo}) {
    let endpoint = `/repos/${repo.full_name}/stats`;
    let params = {resolution: '1d', points: 30};
    return [
      ['covered', endpoint, {query: {stat: 'coverage.lines_covered', ...params}}],
      ['uncovered', endpoint, {query: {stat: 'coverage.lines_uncovered', ...params}}]
    ];
  }

  renderError(error) {
    return <div>Error loading chart</div>;
  }

  renderBody() {
    let {covered, uncovered} = this.state;
    let data = [];
    covered.forEach((coveredPoint, idx) => {
      let uncoveredPoint = uncovered[idx];
      if (coveredPoint.time !== uncoveredPoint.time) {
        throw new Error('invalid data');
      }
      data.push({
        time: coveredPoint.time,
        value: coveredPoint.value
          ? parseInt(
              coveredPoint.value / (coveredPoint.value + uncoveredPoint.value) * 1000,
              10
            ) / 10
          : 0
      });
    });
    return <GenericLineChart formatValue={v => v + '%'} data={data} label="% Coverage" />;
  }
}

class RepositoryChart extends AsyncPage {
  static defaultProps = {
    formatValue: value => {
      return value.toLocaleString();
    }
  };

  getEndpoints({repo, stat}) {
    let endpoint = `/repos/${repo.full_name}/stats`;
    let params = {resolution: '1d', points: 30};
    return [['data', endpoint, {query: {stat: stat, ...params}}]];
  }

  renderError(error) {
    return <div>Error loading chart</div>;
  }

  renderBody() {
    return (
      <GenericLineChart
        {...this.props}
        data={this.state.data}
        label={this.props.label || this.props.stat}
      />
    );
  }
}

export class RepositoryOverview extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    let {repo} = this.context;
    return (
      <Flex>
        <Box flex="1" width={8 / 12} pr={15}>
          <Section>
            <SectionHeading>
              Latest Commits
              <Link to={`/${repo.full_name}/revisions`} style={{marginLeft: 10}}>
                <ViewAllIcon size={18} style={{verticalAlign: 'text-bottom'}} />
              </Link>
            </SectionHeading>
            <RevisionListBody {...this.props} />
          </Section>
        </Box>
        <Box width={4 / 12}>
          <Section>
            <SectionHeading>Duration</SectionHeading>
            <RepositoryChart
              repo={repo}
              formatValue={v => getDuration(v, true)}
              stat="builds.duration"
            />
          </Section>
          <Section>
            <SectionHeading>Coverage</SectionHeading>
            <CoverageChart repo={repo} />
          </Section>
          <Section>
            <SectionHeading>Bundle Size</SectionHeading>
            <RepositoryChart
              repo={repo}
              formatValue={getSize}
              stat="bundle.total_asset_size"
            />
          </Section>
        </Box>
      </Flex>
    );
  }
}

class RevisionListBody extends AsyncComponent {
  static propTypes = {
    revisionList: PropTypes.array
  };

  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  fetchData(refresh) {
    return new Promise((resolve, reject) => {
      let {repo} = this.context;
      this.props.loadRevisionsForRepository(repo.full_name, {per_page: 10}, !refresh);
      return resolve();
    });
  }

  renderBody() {
    return (
      <div>
        <RevisionList
          params={this.props.params}
          repo={this.context.repo}
          revisionList={this.props.revisionList}
          columns={[]}
        />
      </div>
    );
  }
}

export default connect(
  function(state) {
    return {
      revisionList: state.revisions.items,
      links: state.revisions.links,
      loading: !state.revisions.loaded
    };
  },
  {loadRevisionsForRepository}
)(RepositoryOverview);
