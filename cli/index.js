#!/usr/bin/env node
/* eslint-env node */

const {createReadStream} = require('fs');
const {basename} = require('path');
const request = require('request');

const ZEUS_HOOK_BASE = process.env.ZEUS_HOOK_BASE;
if (!ZEUS_HOOK_BASE) {
  console.error('ERROR: Missing ZEUS_HOOK_BASE environment variable');
  process.exit(1);
}

let CI_SYSTEM = null;
let BUILD_ID = null;
let JOB_ID = null;

if (process.env.TRAVIS === 'true') {
  CI_SYSTEM = 'travis';
  BUILD_ID = process.env.TRAVIS_BUILD_ID;
  JOB_ID = process.env.TRAVIS_JOB_ID;
}

if (process.env.APPVEYOR === 'True') {
  CI_SYSTEM = 'appveyor';
  BUILD_ID = process.env.APPVEYOR_BUILD_ID;
  JOB_ID = process.env.APPVEYOR_JOB_ID;
}

if (!CI_SYSTEM) {
  console.error('ERROR: No supported CI system detected');
  process.exit(1);
}

require('yargs')
  .demandCommand()
  .command(
    'upload <file> [type]',
    'Upload a build artifact',
    yargs =>
      yargs
        .positional('file', {
          describe: 'Path to the artifact',
          type: 'string'
        })
        .positional('type', {
          describe: 'Mime type of the file to upload',
          type: 'string'
        }),
    argv => {
      const url = `${ZEUS_HOOK_BASE}/builds/${BUILD_ID}/jobs/${JOB_ID}/artifacts`;
      const formData = {
        type: argv.type,
        file: {
          value: createReadStream(argv.file),
          options: {
            filename: basename(argv.file)
          }
        }
      };
      request.post({url, formData}, err => {
        if (err) {
          console.error('Artifact upload failed: ', err);
          process.exit(1);
        }

        console.log('Artifact upload completed');
      });
    }
  )
  .help().argv;
