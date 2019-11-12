import {Link} from 'react-router';
import styled from '@emotion/styled';

const ListItemLink = styled(Link)`
  display: block;

  &:hover {
    background-color: #f0eff5;
  }

  &.${props => props.activeClassName} {
    color: #fff;
    background: #7b6be6;

    > div {
      color: #fff !important;

      svg {
        color: #fff;
        opacity: 0.5;
      }
    }
  }
`;

ListItemLink.defaultProps = {
  activeClassName: 'active'
};

export default ListItemLink;
