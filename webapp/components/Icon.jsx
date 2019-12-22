import styled from '@emotion/styled';

export default styled.div(
  {
    display: 'inline-block',
    verticalAlign: 'text-top',
    width: 16,
    height: 16,
    fontSize: 16
  },
  props => ({
    marginRight: props.mr ? 5 : 0
  })
);
