import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import idx from 'idx';
import Gravatar from 'react-gravatar';
import MdPerson from 'react-icons/lib/md/person';

const Avatar = styled.span`
  img {
    border-radius: 2px;
  }

  img,
  svg {
    margin-right: 5px;
    display: inline-block;
    vertical-align: text-top;
  }
`;

export default class ObjectAuthor extends Component {
  static propTypes = {
    data: PropTypes.shape({
      author: PropTypes.shape({
        name: PropTypes.string,
        email: PropTypes.email
      }),
      source: PropTypes.shape({
        author: PropTypes.shape({
          name: PropTypes.string,
          email: PropTypes.email
        })
      })
    }).isRequired
  };

  render() {
    let {data} = this.props;
    let author = idx(data, _ => _.source.author) || data.author;
    if (!author || !(author.name || author.email)) return null;
    return (
      <span>
        <Avatar>
          {author.email ? (
            <Gravatar email={author.email} size={16} />
          ) : (
            <MdPerson size="16" />
          )}
        </Avatar>
        {author.name || author.email.split('@', 1)[0]}
      </span>
    );
  }
}
