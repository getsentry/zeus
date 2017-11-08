import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Collapsable from './Collapsable';
import {ResultGrid, Column, Header, Row} from './ResultGrid';

export default class ArtifactsList extends Component {
  static propTypes = {
    artifacts: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number
  };

  static defaultProps = {
    collapsable: false
  };

  constructor(props, context) {
    super(props, context);
    this.state = {collapsable: props.collapsable};
  }

  humanFileSize(size) {
    if (size === 0) return '0 B';
    if (!size) return null;

    let i = Math.floor(Math.log(size) / Math.log(1024));
    return (
      (size / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i]
    );
  }

  render() {
    return (
      <ResultGrid>
        <Header>
          <Column>File</Column>
          <Column width={120}>Type</Column>
          <Column width={90} textAlign="right">
            Size
          </Column>
        </Header>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.artifacts.map(artifact => {
            return (
              <Row key={artifact.id}>
                <Column>
                  {this.props.collapsable ? (
                    artifact.name
                  ) : (
                    <div>
                      <a href={artifact.download_url}>{artifact.name}</a>
                      <br />
                      <small>
                        {artifact.job.provider} #{artifact.job.number}
                      </small>
                    </div>
                  )}
                </Column>
                <Column width={120} textAlign="right">
                  {artifact.type}
                </Column>
                <Column width={90} textAlign="right">
                  {this.humanFileSize(artifact.file.size)}
                </Column>
              </Row>
            );
          })}
        </Collapsable>
      </ResultGrid>
    );
  }
}
