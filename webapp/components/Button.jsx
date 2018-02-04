import {Link} from 'react-router';
import styled, {css} from 'styled-components';

// TODO(dcramer): how do we avoid copy pasta?
export const ButtonGroup = styled.div`
  a {
    margin-right: 5px;
  }
  a:last-child {
    margin-right: 0;
  }

  ${props => {
    switch (props.align) {
      case 'right':
        return css`
          text-align: right;
        `;
      default:
        return css`
          text-align: left;
        `;
    }
  }};
`;

export const ButtonLink = styled(Link)`
  background: #7b6be6;
  color: #fff;
  display: inline-block;
  border: 2px solid #7b6be6;
  border-radius: 3px;
  cursor: pointer;
  font-weight: 500;

  ${props => {
    switch (props.type) {
      case 'danger':
        return css`
          background: #fff;
          color: #e03e2f;
          border-color: #e03e2f;
          &:hover {
            background: #7b6be6;
            color: #fff;
          }
        `;
      case 'primary':
        return css`
          background: #fff;
          color: #7b6be6;
          border-color: #7b6be6;
        `;
      case 'light':
        return css`
          background: #fff;
          color: #999;
          border-color: #eee;
        `;
      default:
        return css`
          background: #fff;
          color: #111;
          border-color: #111;
          &:hover {
            background: #111;
            color: #fff;
          }
        `;
    }
  }};

  ${props => {
    switch (props.size) {
      case 'xs':
        return css`
          font-size: 9px;
          padding: 2px 4px;
        `;
      case 'small':
        return css`
          font-size: 12px;
          padding: 4px 8px;
        `;
      case 'large':
        return css`
          font-size: 16px;
          padding: 8px 12px;
        `;
      default:
        return css`
          font-size: 14px;
          padding: 8px 12px;
        `;
    }
  }};

  ${props =>
    props.disabled &&
    `
    cursor: not-allowed;
    opacity: 0.3;

    &:hover {
      background: inherit;
      color: inherit;
    }
  `};
`;

export default ButtonLink.withComponent('a');
