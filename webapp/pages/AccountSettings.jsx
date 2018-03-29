import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {addIndicator, removeIndicator} from '../actions/indicators';
import AsyncPage from '../components/AsyncPage';
import Badge from '../components/Badge';
import {ResultGrid, Column, Row} from '../components/ResultGrid';
import Label from '../components/Label';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';

class AccountSettings extends AsyncPage {
  static contextTypes = {
    router: PropTypes.object.isRequired
  };

  getTitle() {
    return 'Account Settings';
  }

  getEndpoints() {
    return [['emailList', '/users/me/emails'], ['user', '/users/me']];
  }

  toggleNotifications = e => {
    let {user} = this.state;
    let indicator = this.props.addIndicator('Saving changes..', 'loading');
    this.api
      .put('/users/me', {
        data: {
          options: {
            mail: {notify_author: user.options.mail.notify_author === '1' ? '0' : '1'}
          }
        }
      })
      .then(result => {
        this.props.removeIndicator(indicator);
        this.props.addIndicator('Changes saved!', 'success', 5000);
        this.setState({user: result});
      })
      .catch(error => {
        this.props.addIndicator('An error occurred.', 'error', 5000);
        this.props.removeIndicator(indicator);
        throw error;
      });
  };

  renderBody() {
    let {emailList, user} = this.state;
    return (
      <div>
        <SectionHeading>Notifications</SectionHeading>
        <Section>
          <p>
            {
              "We'll send notifications to email address which is listed on the commit, but only if it's known and verified."
            }
          </p>
          <Label>
            <input
              type="checkbox"
              checked={user.options.mail.notify_author === '1'}
              onChange={this.toggleNotifications}
            />{' '}
            Receive email notifications for build failures
          </Label>
        </Section>
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
                  {!email.verified && (
                    <span>
                      {' '}
                      &mdash; <em>unverified</em>
                    </span>
                  )}
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
  {
    addIndicator,
    removeIndicator
  }
)(AccountSettings);
