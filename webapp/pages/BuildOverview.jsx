import BuildOverviewBase from '../components/BuildOverviewBase';

export default class BuildOverview extends BuildOverviewBase {
  getBuildEndpoint() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return `/repos/${repo.full_name}/builds/${buildNumber}`;
  }
}
