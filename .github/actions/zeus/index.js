const core = require('@actions/core');
const http = require('@actions/http-client');

// npm install -g @zeus-ci/cli
// $(npm bin -g)/zeus upload -t "application/x-junit+xml" .artifacts/*.junit.xml
// $(npm bin -g)/zeus upload -t "application/x-cobertura+xml" .artifacts/coverage.xml
// $(npm bin -g)/zeus upload -t "application/x-cobertura+xml" .artifacts/coverage/cobertura-coverage.xml
// $(npm bin -g)/zeus upload -t "application/x-checkstyle+xml" .artifacts/*.checkstyle.xml
// $(npm bin -g)/zeus upload -t "text/x-pycodestyle" .artifacts/flake8.log
// $(npm bin -g)/zeus upload -t "application/webpack-stats+json" .artifacts/webpack-stats.json

try {
  // const artifactList = core.getInput('artifacts');
  // console.log(`Artifacts: ${artifactList}!`);
  // const time = new Date().toTimeString();
  // core.setOutput('time', time);

  // https://help.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#github-context
  // const action = context.action; // self1

  console.log(JSON.stringify(process.env.STEPS_CONTEXT, null, 2));

  const buildId = process.env.GITHUB_RUN_ID;
  const repository = process.env.REPOSITORY;
  const sha = process.env.GITHUB_SHA;
  const workflow = process.env.GITHUB_WORKFLOW; // zeus
  const jobId = core.getInput('job-id');
  const jobResult = core.getInput('job-result');
  const jobStatus = core.getInput('job-status');
  const zeusHookBase = core.getInput('zeus-hook-base');

  const http = new http.HttpClient();
  // await http.postJson(`${zeusHookBase}/builds/${buildId}`, {
  //   ref: sha,
  //   url: `https://github.com/${repository}/actions/runs/${buildId}`
  // });
  // await http.postJson(`${zeusHookBase}/builds/${buildId}/jobs/${jobId}`, {
  //   label: workflow,
  //   url: `https://github.com/${repository}/actions/runs/${buildId}`,
  //   status: finished ? 'finished' : 'in_progress',
  //   result: 'unknown'
  // });
} catch (error) {
  core.setFailed(error.message);
}
