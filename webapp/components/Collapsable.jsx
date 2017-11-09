import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import ResultGridRow from './ResultGridRow';

export default class Collapsable extends Component {
  static propTypes = {
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number
  };

  static defaultProps = {
    collapsable: false,
    maxVisible: 10
  };

  constructor(props, context) {
    super(props, context);
    this.state = {collapsed: props.collapsable};
  }

  render() {
    let {children, maxVisible} = this.props;
    let totalChildren = children.length;
    let collapsed = this.state.collapsed;
    let visibleChildren = totalChildren;
    if (totalChildren <= maxVisible) {
      collapsed = false;
    } else if (collapsed) {
      children = children.slice(0, 5);
      visibleChildren = 5;
    }

    return (
      <div>
        {children}
        {collapsed &&
          <ExpandLink onClick={() => this.setState({collapsed: false})}>
            <ResultGridRow style={{color: 'inherit'}}>
              Show {totalChildren - visibleChildren} other item(s)
            </ResultGridRow>
          </ExpandLink>}
      </div>
    );
  }
}

const ExpandLink = styled.a`
  display: block;
  cursor: pointer;
  color: #7b6be6;

  &:hover {
    background-color: #f0eff5;
  }
`;
