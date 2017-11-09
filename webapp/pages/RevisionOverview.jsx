import BuildOverviewBase from '../components/BuildOverviewBase';

export default class RevisionOverview extends BuildOverviewBase {
  getBuildEndpoint() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return `/repos/${repo.full_name}/revisions/${sha}`;
  }
}
