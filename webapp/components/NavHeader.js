import React, {PropTypes} from 'react';
import styled from 'styled-components';

const NavHeader = styled(({label, ...props}) => <div {...props} children={label} />)`
  font-size: 13px;
  font-weight: 400;
  text-transform: uppercase;
  margin: 20px 0;
  color: #767488;
`;

NavHeader.propTypes = {
  label: PropTypes.string
};

export default NavHeader;
