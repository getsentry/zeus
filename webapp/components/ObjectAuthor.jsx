import React, {Component} from 'react';
import PropTypes from 'prop-types';
import idx from 'idx';

export default class ObjectAuthor extends Component {
  static propTypes = {
    data: PropTypes.object.isRequired
  };

  render() {
    let {data} = this.props;
    let author = idx(data, _ => _.source.author) || data.author;
    if (!author) return null;
    return (
      <span>
        {author.email || author.name}
      </span>
    );
  }
}
