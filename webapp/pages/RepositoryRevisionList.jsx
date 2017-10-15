import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadRevisionsForRepository} from '../actions/revisions';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import RevisionList from '../components/RevisionList';
import RepositoryContent from '../components/RepositoryContent';
import RepositoryHeader from '../components/RepositoryHeader';

class RepositoryRevisionList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getTitle() {
    return this.context.repo.name;
  }

  renderBody() {
    return (
      <div>
        <RepositoryHeader />
        <RepositoryContent {...this.props}>
          <RevisionListBody {...this.props} />
        </RepositoryContent>
      </div>
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

  shouldFetchUpdates(stateKey, endpoint, params) {
    return false;
  }

  fetchData(refresh) {
    return new Promise((resolve, reject) => {
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
      <RevisionList
        params={this.props.params}
        repo={this.context.repo}
        revisionList={this.props.revisionList}
      />
    );
  }
}

export default connect(
  function(state) {
    return {
      revisionList: state.revisions.items,
      loading: !state.revisions.loaded
    };
  },
  {loadRevisionsForRepository}
)(RepositoryRevisionList);
