import React from 'react';
import {Flex, Box} from 'grid-styled';
import styled from 'styled-components';

export const ResultGrid = styled.div`
  background: #fff;
  border: 1px solid #dbdae3;
  border-radius: 3px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .03);
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

export const Column = props => {
  let params = {...props};
  if (!params.width) {
    params.flex = 1;
  }
  params.className = `${params.className || ''} ResultGrid-Column`;
  if (params.textAlign) {
    params.style = {...(params.style || {}), textAlign: params.textAlign};
  }
  return <Box {...params} />;
};

export const Header = styled(props => {
  let params = {...props};
  params.className = `${params.className || ''} ResultGrid-Header`;
  return <Flex align="center" {...params} />;
})`
  padding: 0 0 5px;
  border-bottom: 2px solid #eee;
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
  padding: 10px 15px;
  color: #39364e;
  border-bottom: 1px solid #dbdae3;
  font-size: 14px;
`;

export default {
  Column,
  Header,
  ResultGrid,
  Row
};
