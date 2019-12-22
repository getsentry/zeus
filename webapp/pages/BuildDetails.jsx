import BuildDetailsBase from '../components/BuildDetailsBase';

export default class BuildDetails extends BuildDetailsBase {
  getBuildEndpoint() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return `/repos/${repo.full_name}/builds/${buildNumber}`;
  }

  getBaseRoute() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return `/${repo.full_name}/builds/${buildNumber}`;
  }

  getTitle() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return `${repo.owner_name}/${repo.name}#${buildNumber}`;
  }
}
