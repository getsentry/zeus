import styled from '@emotion/styled';

export default styled.dl`
  margin: 0 0 20px;
  padding-left: ${props => props.prefixWidth || 140}px;

  &::after {
    content: '';
    clear: both;
    display: table;
  }
  dt {
    float: left;
    clear: left;
    margin-left: -${props => props.prefixWidth || 140}px;
    width: ${props => (props.prefixWidth ? props.prefixWidth - 20 : 120)}px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 0.5rem;
    color: #999;
  }
  dd {
    margin-bottom: 0.5rem;
  }
`;
