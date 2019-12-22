import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadRevisionsForRepository} from '../actions/revisions';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import Paginator from '../components/Paginator';
import RevisionList from '../components/RevisionList';

export class RepositoryRevisionList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    return <RevisionListBody {...this.props} />;
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
      this.props.loadRevisionsForRepository(
        repo.full_name,
        this.props.location.query,
        !refresh
      );
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
        />
        <Paginator links={this.props.links} {...this.props} />
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
)(RepositoryRevisionList);
