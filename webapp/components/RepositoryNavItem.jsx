import {Link} from 'react-router';
import styled from 'styled-components';

const RepositoryNavItem = styled(Link)`
  cursor: pointer;
  float: left;
  font-size: 15px;
  color: #aaa7bb;
  padding: 10px 20px;
  border-left: 1px solid #dbdae3;

  &:last-item {
    border-right: 1px solid #dbdae3;
  }

  &.active {
    background: #7b6be6;
    color: #fff;
  }

  &.${props => props.activeClassName} {
    background: #7b6be6;
    color: #fff;
  }
`;

RepositoryNavItem.defaultProps = {
  activeClassName: 'active'
};

export default RepositoryNavItem;
