import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

const NavHeading = styled(({label, ...props}) => {
  return (
    <div {...props}>
      {label}
    </div>
  );
})`
  font-size: 13px;
  font-weight: 500;
  text-transform: uppercase;
  margin: 0 0 30px;
  color: #767488;
`;

NavHeading.propTypes = {
  label: PropTypes.string
};

export default NavHeading;
