import React from 'react';
import {mount} from 'enzyme';

import RevisionList from '../RevisionList';

describe('RevisionList', () => {
  it('renders', done => {
    let repo = TestStubs.Repository();
    let revision = TestStubs.Revision();
    let location = TestStubs.location({pathname: `/${repo.provider}/${repo.full_name}`});

    let context = TestStubs.standardContext();

    const wrapper = mount(
      <RevisionList
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name
        }}
        repo={repo}
        revisionList={[revision]}
        location={location}
      />,
      context
    );
    setTimeout(() => {
      expect(wrapper).toMatchSnapshot();
      done();
    });
  });
});
