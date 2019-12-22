import {Link} from 'react-router';
import styled from '@emotion/styled';

export const Nav = styled.div`
  display: inline-block;
`;
export default Nav;

export const NavItem = styled(Link)`
  cursor: pointer;
  float: left;
  font-size: 15px;
  color: #333;
  margin-left: 10px;
  padding: 5px 10px;
  border: 3px solid #fff;
  border-radius: 4px;

  &:hover {
    color: #333;
  }

  &.active,
  .${props => props.activeClassName} {
    border-color: #7b6be6;
    color: #7b6be6;
  }
`;

NavItem.defaultProps = {
  activeClassName: 'active'
};
