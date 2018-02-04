import PropTypes from 'prop-types';
import React from 'react';

import {ButtonGroup, ButtonLink} from './Button';

export default class Paginator extends React.Component {
  static propTypes = {
    links: PropTypes.object,
    location: PropTypes.object
  };

  static contextTypes = {
    router: PropTypes.object
  };

  render() {
    let {links, location} = this.props;

    if (!links) return null;

    let hasPrev = links.previous && links.previous.results !== false;
    let hasNext = links.next && links.next.results !== false;

    return (
      <div style={{marginBottom: 20}}>
        <ButtonGroup align="right">
          <ButtonLink
            to={
              hasPrev ? `${location.pathname}?${links.previous.href.split('?')[1]}` : null
            }
            disabled={!hasPrev}>
            Previous
          </ButtonLink>
          <ButtonLink
            to={hasNext ? `${location.pathname}?${links.next.href.split('?')[1]}` : null}
            disabled={!hasNext}>
            Next
          </ButtonLink>
        </ButtonGroup>
      </div>
    );
  }
}
