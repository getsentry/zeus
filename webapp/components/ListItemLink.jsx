import {Link} from 'react-router';
import styled from 'styled-components';

const ListItemLink = styled(Link)`
display: block;

&:hover {
  background-color: #F0EFF5;
}

&.${props => props.activeClassName} {
  color: #fff;
  background: #7B6BE6;

  > div {
    color: #fff !important;

    svg {
      color: #fff;
      opacity: .5;
    }
  }
}
`;

ListItemLink.defaultProps = {
  activeClassName: 'active'
};

export default ListItemLink;
