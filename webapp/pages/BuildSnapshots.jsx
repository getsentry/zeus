import React from 'react';
import PropTypes from 'prop-types';
import AsyncPage from '../components/AsyncPage';
import ImageDiff from '../components/ImageDiff';

import Section from '../components/Section';

export default class BuildDiff extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired,
    build: PropTypes.object.isRequired
  };

  renderBody() {
    return (
      <Section>
        <ImageDiff />
      </Section>
    );
  }
}
