import {Link} from 'react-router';
import styled from 'styled-components';

const TabbedNavItem = styled(Link)`
  cursor: pointer;
  float: left;
  font-size: 15px;
  color: #AAA7BB;
  margin-right: 20px;
  padding: 15px 0;
  border-bottom: 3px solid transparent;

  &.${(props) => props.activeClassName} {
    color: #39364E;
    border-bottom: 3px solid #7B6BE6;
  }
`;

TabbedNavItem.defaultProps = {
  activeClassName: 'active',
};

export default TabbedNavItem;
