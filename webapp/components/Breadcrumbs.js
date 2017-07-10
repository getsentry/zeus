import {Link} from 'react-router';
import styled from 'styled-components';

export const Breadcrumbs = styled.div`
  background: #fff;
  padding: 20px;
  box-shadow: inset 0 -1px 0 #dbdae3;
`;

export const CrumbLink = styled(Link)`
  font-size: 22px;
  color: inherit;
`;

export const Crumb = styled.span`font-size: 22px;`;
