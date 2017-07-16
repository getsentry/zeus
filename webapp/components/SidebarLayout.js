import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {Breadcrumbs, Crumb, CrumbLink} from './Breadcrumbs';
import Content from './Content';
import ScrollView from './ScrollView';
import Sidebar from './Sidebar';

export default class SidebarLayout extends Component {
  static propTypes = {
    crumbs: PropTypes.arrayOf(PropTypes.object),
    title: PropTypes.string
  };

  getCrumbs() {
    if (this.props.crumbs) {
      return this.props.crumbs.map((crumb, n) => {
        let genComponent = crumb.to ? CrumbLink : Crumb;
        return (
          <genComponent {...crumb.params} key={n}>
            {crumb.name}
          </genComponent>
        );
      });
    }
    return (
      <Crumb>
        {this.props.title}
      </Crumb>
    );
  }

  render() {
    return (
      <div>
        <Sidebar params={this.props.params} />
        <Content>
          <Breadcrumbs>
            {this.getCrumbs()}
          </Breadcrumbs>
          <ScrollView>
            {this.props.children}
          </ScrollView>
        </Content>
      </div>
    );
  }
}
