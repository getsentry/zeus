import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';
import Gravatar from 'react-gravatar';
import {MdPerson} from 'react-icons/md';

const Avatar = styled.span`
  img {
    border-radius: 2px;
    overflow: hidden;
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
      authors: PropTypes.arrayOf(
        PropTypes.shape({
          name: PropTypes.string,
          email: PropTypes.email
        })
      ).isRequired
    }).isRequired
  };

  render() {
    let {data} = this.props;
    let authors = data.authors;
    if (!authors.length) return null;
    return (
      <span>
        {authors.map(author => {
          if (!author.email || !author.name) return null;
          return (
            <span key={author.email} style={{marginRight: 10}}>
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
        })}
      </span>
    );
  }
}
