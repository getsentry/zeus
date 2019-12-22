import React, {Component} from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import {Flex, Box} from '@rebass/grid/emotion';
import {Line as LineChart} from 'react-chartjs-2';
import {MdInput} from 'react-icons/md';
import * as Sentry from '@sentry/browser';

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
    label: PropTypes.string.isRequired,
    minValue: PropTypes.number,
    maxValue: PropTypes.number
  };

  render() {
    let {data, formatValue, label, minValue, maxValue} = this.props;
    let labels = [];
    let values = [];
    data.reverse().forEach(({build, value}) => {
      labels.push(`#${build}`);
      values.push(value);
    });
    return (
      <LineChart
        redraw={true}
        data={{
          labels: labels,
          datasets: [
            {
              label: label,
              borderColor: '#7b6be6',
              pointRadius: 1,
              data: values,
              fill: false
            }
          ]
        }}
        options={{
          responsive: true,
          title: false,
          legend: {display: false},
          hover: {
            intersect: false
          },
          tooltips: {
            intersect: false,
            callbacks: {
              label: item => {
                return formatValue(item.yLabel);
              }
            }
          },
          scales: {
            xAxes: [
              {
                gridLines: {
                  display: false
                },
                type: 'category',
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
                  suggestedMin: minValue,
                  suggestedMax: maxValue,
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
  static propTypes = {
    repo: PropTypes.object.isRequired,
    title: PropTypes.string
  };

  getEndpoints({repo}) {
    let endpoint = `/repos/${repo.full_name}/stats`;
    let params = {resolution: '1d', points: 90, aggregate: 'build'};
    return [
      ['covered', endpoint, {query: {stat: 'coverage.lines_covered', ...params}}],
      ['uncovered', endpoint, {query: {stat: 'coverage.lines_uncovered', ...params}}]
    ];
  }

  componentDidCatch(error, errorInfo) {
    Sentry.captureException(error, {extra: errorInfo});
  }

  renderError() {
    return <div>Error loading chart</div>;
  }

  renderBody() {
    let {covered, uncovered} = this.state;
    let data = covered.map((coveredPoint, idx) => {
      let uncoveredPoint = uncovered[idx];
      if (!uncoveredPoint || coveredPoint.build !== uncoveredPoint.build) {
        Sentry.captureMessage('Mismatched builds for CoverageChart', 'error');
        return this.renderError();
      }
      return {
        build: coveredPoint.build,
        value: coveredPoint.value
          ? parseInt(
              (coveredPoint.value / (coveredPoint.value + uncoveredPoint.value)) * 1000,
              10
            ) / 10
          : coveredPoint.value
      };
    });
    if (!data.length) return null;
    let currentValue = data.length && data[0].value;
    return (
      <Section>
        {!!this.props.title && (
          <SectionHeading>
            {this.props.title}
            {currentValue !== false && <small>{currentValue}%</small>}
          </SectionHeading>
        )}
        <GenericLineChart
          {...this.props}
          formatValue={v => v + '%'}
          data={data}
          maxValue={100}
          label="% Coverage"
        />
      </Section>
    );
  }
}

class RepositoryChart extends AsyncPage {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    label: PropTypes.string,
    stat: PropTypes.string.isRequired,
    title: PropTypes.string,
    formatValue: PropTypes.func
  };

  static defaultProps = {
    formatValue: value => {
      return value.toLocaleString();
    }
  };

  componentDidCatch(error, errorInfo) {
    Sentry.captureException(error, {extra: errorInfo});
  }

  getEndpoints({repo, stat}) {
    let endpoint = `/repos/${repo.full_name}/stats`;
    let params = {resolution: '1d', points: 90, aggregate: 'build'};
    return [['data', endpoint, {query: {stat: stat, ...params}}]];
  }

  renderError() {
    return <div>Error loading chart</div>;
  }

  renderBody() {
    let {label, stat} = this.props;
    if (!this.state.data.length) return null;
    let currentValue = this.state.data.length && this.state.data[0].value;
    return (
      <Section>
        {!!this.props.title && (
          <SectionHeading>
            {this.props.title}
            {currentValue !== false && (
              <small>{this.props.formatValue(currentValue)}</small>
            )}
          </SectionHeading>
        )}
        <GenericLineChart {...this.props} data={this.state.data} label={label || stat} />
      </Section>
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
        <Box flex="1" width={8 / 12} pr={2}>
          <Section>
            <SectionHeading>
              Latest Commits
              <Link to={`/${repo.full_name}/revisions`} style={{marginLeft: 10}}>
                <MdInput size={18} style={{verticalAlign: 'text-bottom'}} />
              </Link>
            </SectionHeading>
            <RevisionListBody {...this.props} />
          </Section>
        </Box>
        <Box width={4 / 12}>
          <RepositoryChart
            {...this.props}
            title="Duration"
            repo={repo}
            formatValue={v => getDuration(v, true)}
            stat="builds.duration"
          />
          <CoverageChart title="Coverage" {...this.props} repo={repo} />
          <RepositoryChart
            {...this.props}
            title="Bundle Size"
            repo={repo}
            formatValue={getSize}
            stat="bundle.total_asset_size"
          />
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

  loadData(refresh) {
    return new Promise(resolve => {
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
