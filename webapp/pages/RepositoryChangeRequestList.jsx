import React, {Component} from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {fetchChangeRequests} from '../actions/changeRequests';
import {subscribe} from '../decorators/stream';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import ChangeRequestList from '../components/ChangeRequestList';
import Paginator from '../components/Paginator';

class RepositoryChangeRequestList extends AsyncPage {
  static propTypes = {
    ...AsyncPage.propTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    return <ChangeRequestListBody {...this.props} />;
  }
}

class ChangeRequestListBody extends AsyncComponent {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    changeRequestList: PropTypes.array,
    links: PropTypes.object
  };

  fetchData() {
    return new Promise(resolve => {
      let {repo} = this.props;
      this.props.fetchChangeRequests({
        repository: repo.full_name,
        ...this.props.location.query
      });
      return resolve();
    });
  }

  renderBody() {
    return (
      <div>
        <ChangeRequestList
          params={this.props.params}
          changeRequestList={this.props.changeRequestList}
          repo={this.props.repo}
        />
        <Paginator links={this.props.links} {...this.props} />
      </div>
    );
  }
}

// We force the repo param into props so that we can read it as part of connect
// in order to filter down the data we're propagating to the child
// XXX(dcramer): this is super tricky/sketch atm
const DecoratedRepositoryChangeRequestList = connect(
  ({changeRequests}, {repo}) => ({
    changeRequestList: changeRequests.items.filter(
      cr => !cr.repository || cr.repository.full_name === repo.full_name
    ),
    links: changeRequests.links,
    loading: !changeRequests.loaded
  }),
  {fetchChangeRequests}
)(
  subscribe(({repo}) => [`repos:${repo.full_name}:change-requests`])(
    RepositoryChangeRequestList
  )
);

export default class RepositoryChangeRequestListWithRepoProp extends Component {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  render() {
    return (
      <DecoratedRepositoryChangeRequestList {...this.props} repo={this.context.repo} />
    );
  }
}
