import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Content from './Content';
import Header from './Header';
import Footer from './Footer';

export default class Layout extends Component {
  static propTypes = {
    children: PropTypes.node,
    title: PropTypes.string
  };

  render() {
    return (
      <div>
        <Header />
        <Content>{this.props.children}</Content>
        <Footer />
      </div>
    );
  }
}
