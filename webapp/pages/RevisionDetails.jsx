import BuildDetailsBase from '../components/BuildDetailsBase';

export default class RevisionDetails extends BuildDetailsBase {
  getBuildEndpoint() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return `/repos/${repo.full_name}/revisions/${sha}`;
  }

  getBaseRoute() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return `/${repo.full_name}/revisions/${sha}`;
  }

  getTitle() {
    return 'Build Details';
  }
}
