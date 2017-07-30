import React from 'react';

import Section from '../components/Section';
import ScrollView from '../components/ScrollView';

export default props => {
  return (
    <ScrollView>
      <Section>
        {props.children}
      </Section>
    </ScrollView>
  );
};
