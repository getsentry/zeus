import React, {PropTypes} from 'react';
import styled from 'styled-components';

const NavHeading = styled(({label, ...props}) => <div {...props} children={label} />)`
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
