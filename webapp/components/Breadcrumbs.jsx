import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from 'styled-components';

export const Breadcrumbs = styled.div``;

export const CrumbLink = props => {
  return (
    <Crumb {...props}>
      <Link to={props.to}>
        {props.children}
      </Link>
    </Crumb>
  );
};

CrumbLink.propTypes = {
  to: PropTypes.string.isRequired
};

export const Crumb = styled.span`
  font-size: 22px;
  color: #000;

  &:after {
    margin: 0 5px;
    content: ' / ';
    color: #ddd;
  }

  &:last-child {
    color: #666;
    &:after {
      display: none;
    }
  }
`;
