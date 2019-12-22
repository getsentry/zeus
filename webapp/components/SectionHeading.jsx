import React from 'react';
import styled from '@emotion/styled';

export default styled(({...props}) => {
  return <div {...props}>{props.children}</div>;
})`
  font-size: 16px;
  line-height: 16px;
  font-weight: 500;
  text-transform: uppercase;
  margin: 0 0 20px;
  letter-spacing: -1px;
  color: #111;

  small {
    float: right;
    color: #999;
    font-size: 14px;
    line-height: 16px;
    font-weight: normal;
    text-transform: none;
  }
`;
