import {css} from '@emotion/core';
import styled from '@emotion/styled';

export default styled.span`
  font-size: 65%;
  display: inline-block;
  padding: 0.25em 0.5em;
  margin-left: 5px;
  text-transform: uppercase;
  color: #111;
  font-weight: 700;
  border-radius: 8px;
  vertical-align: baseline;

  ${props => {
    switch (props.type) {
      case 'error':
        return css`
          background: #dc3545;
        `;
      case 'warning':
        return css`
          background: #ffc107;
        `;
      case 'dark':
        return css`
          color: #fff;
          background: #343a40;
        `;
      default:
        return css`
          color: #fff;
          background: #868e96;
        `;
    }
  }};
`;
