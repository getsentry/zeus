import {Link} from 'react-router';
import styled from 'styled-components';

const TabbedNavItem = styled(Link)`
  cursor: pointer;
  display: inline-block;
  font-size: 15px;
  color: #aaa7bb;
  margin-right: 20px;
  padding: 0 0 10px;
  margin-bottom: -4px;
  border-bottom: 4px solid transparent;
  text-decoration: none;

  &.active,
  ${props => props.activeClassName} {
    color: #39364e;
    border-bottom-color: #7b6be6;
  }
`;

TabbedNavItem.defaultProps = {
  activeClassName: 'active'
};

export default TabbedNavItem;
