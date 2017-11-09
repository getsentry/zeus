import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import AsyncPage from '../components/AsyncPage';
import Badge from '../components/Badge';
import {ResultGrid, Column, Row} from '../components/ResultGrid';
import SectionHeading from '../components/SectionHeading';

class AccountSettings extends AsyncPage {
  static contextTypes = {
    user: PropTypes.object,
    router: PropTypes.object.isRequired
  };

  getTitle() {
    return 'Account Settings';
  }

  getEndpoints() {
    return [['emailList', '/users/me/emails']];
  }

  renderBody() {
    let {user} = this.props;
    let {emailList} = this.state;
    return (
      <div>
        <SectionHeading>Associated Email Addresses</SectionHeading>
        <p>
          {"We've synced these from GitHub, and will use them to identify your commits."}
        </p>
        <ResultGrid>
          {emailList.map(email => {
            return (
              <Row key={email.email}>
                <Column>
                  {email.email}
                  {email.email === user.email && <Badge>Primary</Badge>}
                  {!email.verified &&
                    <span>
                      {' '}&mdash; <em>unverified</em>
                    </span>}
                </Column>
              </Row>
            );
          })}
        </ResultGrid>
      </div>
    );
  }
}

export default connect(
  ({auth}) => ({
    user: auth.user
  }),
  {}
)(AccountSettings);
