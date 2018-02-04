import PropTypes from 'prop-types';
import React from 'react';

import Button, {ButtonGroup} from './Button';

export default class Paginator extends React.Component {
  static propTypes = {
    links: PropTypes.object,
    location: PropTypes.object,
    onPage: PropTypes.func
  };

  static contextTypes = {
    router: PropTypes.object
  };

  onPage(href, page) {
    if (!!this.props.onPage) return this.props.onPage(href, page);
    let {location} = this.props;
    return this.context.router.push({
      pathname: location.pathname,
      query: {...location.query, page}
    });
  }

  render() {
    let {links} = this.props;

    if (!links) return null;

    let previousPageClassName = 'btn btn-default btn-lg prev';
    if (links.previous && links.previous.results === false) {
      previousPageClassName += ' disabled';
    }

    let nextPageClassName = 'btn btn-default btn-lg next';
    if (links.next && links.next.results === false) {
      nextPageClassName += ' disabled';
    }
    console.log(links.next);

    return (
      <div style={{marginBottom: 20}}>
        <ButtonGroup align="right">
          <Button
            onClick={() => this.onPage(links.previous.href, links.previous.page)}
            className={previousPageClassName}
            disabled={!links.previous || links.previous.results === false}>
            Previous
          </Button>
          <Button
            onClick={() => this.onPage(links.next.href, links.next.page)}
            className={nextPageClassName}
            disabled={!links.next || links.next.results === false}>
            Next
          </Button>
        </ButtonGroup>
      </div>
    );
  }
}
