import React from 'react';
import {render} from 'enzyme';

import ObjectResult from '../ObjectResult';

describe('ObjectResult', () => {
  it('renders queued', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'queued',
          result: 'unknown'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders in-progress', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'in_progress',
          result: 'unknown'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders finished unknown', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'finished',
          result: 'unknown'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders finished passed', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'finished',
          result: 'passed'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders finished failed', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'finished',
          result: 'failed'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders finished errored', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'finished',
          result: 'errored'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders finished aborted', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'finished',
          result: 'aborted'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('handles unknown', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'unknown',
          result: 'unknown'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('handles empty data', () => {
    const tree = render(<ObjectResult data={null} />);
    expect(tree).toMatchSnapshot();
  });

  it('renders size', () => {
    const tree = render(
      <ObjectResult
        data={{
          status: 'finished',
          result: 'passed'
        }}
        size={12}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
