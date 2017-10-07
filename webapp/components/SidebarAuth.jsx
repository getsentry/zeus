import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {connect} from 'react-redux';
import {logout} from '../actions/auth';

const AuthContainer = styled.div`
  position: fixed;
  color: #fff;
  font-size: 11px;
  left: 20px;
  bottom: 15px;
  width: 220px;
  line-height: 1.5;
`;

class SidebarAuth extends Component {
  static propTypes = {
    isAuthenticated: PropTypes.bool,
    user: PropTypes.object,
    logout: PropTypes.func.isRequired
  };

  render() {
    let {isAuthenticated, user} = this.props;
    if (isAuthenticated === null) return null;
    return (
      <AuthContainer>
        {this.props.isAuthenticated
          ? <span>
              <strong>{user.email}</strong> <br />
              <a onClick={this.props.logout} style={{cursor: 'pointer'}}>
                Sign out
              </a>
            </span>
          : <em>anonymous</em>}
      </AuthContainer>
    );
  }
}

function mapStateToProps(state) {
  return {
    user: state.auth.user,
    isAuthenticated: state.auth.isAuthenticated
  };
}

export default connect(mapStateToProps, {logout})(SidebarAuth);
