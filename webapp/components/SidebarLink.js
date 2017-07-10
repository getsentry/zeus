import styled from 'styled-components';
import {Link} from 'react-router';

const SidebarLink = styled(Link)`
  height: 30px;
  color: #B9B6CE;
  display: block;
  line-height: 30px;
  position: relative;

  margin: 0 -20px;
  padding: 0 20px;
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;

  &:hover {
    color: #fff;
  }

  &.${props => props.activeClassName} {
    color: #fff;
    background: #7B6BE6;
    display: block;
  }
`;

SidebarLink.defaultProps = {
  activeClassName: 'active'
};

export default SidebarLink;
