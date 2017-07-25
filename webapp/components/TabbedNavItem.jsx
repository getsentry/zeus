import {Link} from 'react-router';
import styled from 'styled-components';

const TabbedNavItem = styled(Link)`
  cursor: pointer;
  float: left;
  font-size: 15px;
  color: #AAA7BB;
  margin-right: 20px;
  padding: 0 0 10px;
  border-bottom: 2px solid transparent;

  &.active {
    color: #39364E;
    border-bottom-color: #7B6BE6;
  }

  &.${props => props.activeClassName} {
    color: #39364E;
    border-bottom-color: #7B6BE6;
  }
`;

TabbedNavItem.defaultProps = {
  activeClassName: 'active'
};

export default TabbedNavItem;
