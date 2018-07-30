import React, {Component} from 'react';
import {CSSTransition, TransitionGroup} from 'react-transition-group';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import ToastIndicator from './ToastIndicator';

const FadeTransition = props => (
  <CSSTransition {...props} classNames="fade" timeout={500} />
);

class Indicators extends Component {
  static propTypes = {
    items: PropTypes.array
  };

  render() {
    return (
      <div>
        <TransitionGroup
          transitionName="toast"
          transitionEnter={false}
          transitionLeaveTimeout={500}>
          {this.props.items.map(indicator => {
            return (
              <FadeTransition key={indicator.id}>
                <ToastIndicator type={indicator.type}>{indicator.message}</ToastIndicator>
              </FadeTransition>
            );
          })}
        </TransitionGroup>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    items: state.indicators.items
  };
}

export default connect(
  mapStateToProps,
  {}
)(Indicators);
