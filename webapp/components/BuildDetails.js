import React, {Component} from 'react';
import styled, {css} from 'styled-components';

import NavHeading from './NavHeading';
import TabbedNavItem from './TabbedNavItem';

import IconCircleCheck from '../assets/IconCircleCheck';
import IconCircleCross from '../assets/IconCircleCross';
import IconClock from '../assets/IconClock';

export default class BuildDetails extends Component {
  render() {
    return (
      <div>
        <BuildSummary>
          <Header>
            <Message>various improvements</Message>
            <Branch>master</Branch>
          </Header>
          <Meta>
            <Duration status="pass">
              <IconCircleCheck size="18" />
              passed in 12 mins
            </Duration>
            <Time>
              <IconClock size="18" />
              started 2 hours ago
            </Time>
            <Commit>111asd9</Commit>
          </Meta>
          <Tabs>
            <TabbedNavItem to="/">Jobs</TabbedNavItem>
            <TabbedNavItem to="/tests">Tests</TabbedNavItem>
            <TabbedNavItem to="/tests">Coverage</TabbedNavItem>
          </Tabs>
        </BuildSummary>
        <Section>
          <NavHeading label="Build Jobs" />
          <List>
            <ListItem>just</ListItem>
            <ListItem>finna</ListItem>
            <ListItem>make</ListItem>
            <ListItem>these</ListItem>
            <ListItem>a</ListItem>
            <ListItem>list</ListItem>
            <ListItem>for</ListItem>
            <ListItem>now</ListItem>
          </List>
        </Section>
      </div>
    );
  }
}

const Section = styled.div`
  padding: 30px;
`;

const BuildSummary = styled(Section)`
  padding-top: 15px;
  padding-bottom: 0;
  box-shadow: inset 0 -1px 0 #E0E4E8;
`;

const Tabs = styled.div`
  margin-top: 5px;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 4px;
`;

const Message = styled.div`
  font-size: 24px;
  font-weight: 500;
  flex: 1;
  padding-right: 5px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

const Branch = styled.div`
  font-family: "Monaco", monospace;
`;

const Meta = styled.div`
  display: flex;
  align-items: center;
  margin-top: 5px;
  color: #7F7D8F;
  font-size: 14px;

  > div {
    margin-right: 20px;

    &:last-child {
      margin-right: 0;
    }
  }

  svg {
    margin-right: 6px;
    color: #BFBFCB;
    position: relative;
    top: -1px;
  }
`;

const Duration = styled.div`
  ${(props) => {
    switch (props.status) {
      case 'pass':
        return css`
          svg {
            color: #76D392;
          }
        `;
      case 'fail':
        return css`
          color: #F06E5B;
          svg {
            color: #F06E5B;
          }
        `;
      default:
        return css`
          svg {
            color: #BFBFCB;
          }
        `;
    }
  }}
`;

const Time = styled.div`

`;

const Commit = styled(Branch)`
  flex: 1;
  text-align: right;
`;

const List = styled.div`
  border: 1px solid #D8D7E0;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0, .06);
`;

const ListItem = styled.div`
  border-top: 1px solid #E0E4E8;
  display: flex;
  align-items: center;
  padding: 10px 15px;

  &:first-child {
    border: 0;
  }
`;
