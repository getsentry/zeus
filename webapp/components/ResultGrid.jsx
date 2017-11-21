import React from 'react';
import {Flex, Box} from 'grid-styled';
import styled from 'styled-components';

import media from '../utils/media';

export const ResultGrid = styled.div`
  background: #fff;
  border-radius: 3px;
  margin-bottom: 20px;

  .ResultGrid-Column {
    text-align: center;
  }

  .ResultGrid-Column:last-child {
    text-align: right;
  }

  .ResultGrid-Column:first-child {
    text-align: left;
  }

  .ResultGrid-row:last-child .ResultGrid-Column {
    border-bottom: 0;
  }
`;

export const Column = styled(props => {
  let params = {...props};
  if (!params.width) {
    params.flex = 1;
  }
  params.className = `${params.className || ''} ResultGrid-Column`;
  if (params.textAlign) {
    params.style = {...(params.style || {}), textAlign: params.textAlign};
  }
  return <Box {...params} />;
})`
  overflow: hidden;
  ${props => props.hide && media[props.hide]`display: none`};
`;

export const Header = styled(props => {
  let params = {...props};
  params.className = `${params.className || ''} ResultGrid-Header`;
  return <Flex align="center" {...params} />;
})`
  padding: 0 2px 5px;
  border-bottom: 3px solid #eee;
  font-size: 12px;
  color: #999;
  font-weight: 500;
  text-transform: uppercase;
`;

export const Row = styled(props => {
  let params = {...props};
  params.className = `${params.className || ''} ResultGrid-Row`;
  return <Flex align="center" {...params} />;
})`
  padding: 8px 2px;
  color: #333;
  border-bottom: 1px solid #eee;
  font-size: 14px;
`;

export default {
  Column,
  Header,
  ResultGrid,
  Row
};
