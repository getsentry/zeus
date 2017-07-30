import React from 'react';
import styled from 'styled-components';

export default styled(props => {
  return (
    <div {...props}>
      {props.children}
      <div style={{clear: 'both'}} />
    </div>
  );
})`
  overflow: hidden;
  height: 66px;
  background: #fff;
  padding: 20px;
  box-shadow: inset 0 -1px 0 #dbdae3;
`;
