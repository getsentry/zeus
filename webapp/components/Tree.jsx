import {Link} from 'react-router';
import styled from 'styled-components';

import Section from './Section';

export const Tree = styled.div`
  margin-bottom: 20px;
`;

export const Leaf = styled(Link)`
  color: #000;
  font-weight: 400;

  &:after {
    margin: 0 5px;
    content: ' / ';
    color: #ddd;
  }

  &:last-child {
    color: #666;
    &:after {
      display: none;
    }
  }
`;

export const TreeWrapper = styled(Section)`
  border: 2px solid #eee;
  padding: 10px;
`;

export const TreeSummary = styled.div`
  font-size: 0.8em;

  p {
    margin-bottom: 10px;
  }

  p:last-child {
    margin-bottom: 0;
  }
`;
