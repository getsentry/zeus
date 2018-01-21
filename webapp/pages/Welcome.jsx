import React, {Component} from 'react';
import {Link} from 'react-router';
import styled from 'styled-components';

import {Logo} from '../assets/Logo';
import BuildDetailsScreenshot from '../assets/screenshots/BuildDetails.png';
import GitHubLoginButton from '../components/GitHubLoginButton';
import SyntaxHighlight from '../components/SyntaxHighlight';

const TRAVIS_EXAMPLE = `
after_success:
  - npm install -g @zeus-ci/cli
  - $(npm bin -g)/zeus upload -t "application/x-junit+xml" junit.xml
  - $(npm bin -g)/zeus upload -t "application/x-cobertura+xml" coverage.xml
after_failure:
  - npm install -g @zeus-ci/cli
  - $(npm bin -g)/zeus upload -t "application/x-junit+xml" junit.xml
  - $(npm bin -g)/zeus upload -t "application/x-cobertura+xml" coverage.xml
notifications:
  webhooks:
    urls:
      - https://zeus.ci/hooks/9c238278-feee-11e7-8d56-784f4374a3b4/public/provider/travis/webhook
    on_success: always
    on_failure: always
    on_start: always
    on_cancel: always
    on_error: always
  email: false
`;

export default class Welcome extends Component {
  render() {
    return (
      <WelcomeWrapper>
        <Header>
          <Container>
            <Logo height="25" color="#fff" />
            <Nav>
              <Link to="/login">Login</Link>
            </Nav>
          </Container>
        </Header>
        <Hero>
          <Container>
            <p>Zeus is a dashboard for your change control process.</p>
            <HeroImage>
              <img src={BuildDetailsScreenshot} />
            </HeroImage>
          </Container>
        </Hero>
        <Body>
          <Container>
            <Section>
              <h3>Setup is Easy</h3>
              <ol>
                <li>You&apos;ll login to Zeus using your GitHub credentials</li>
                <li>
                  Add a repository in Zeus via{' '}
                  <strong>Settings &rsaquo; Repositories</strong>
                </li>
                <li>
                  Within your repository, create a new Travis-bound hook via{' '}
                  <strong>Settings &rsaquo; Hooks</strong>
                </li>
                <li>
                  Configure your build via <code>.travis.yml</code> to push results to
                  Zeus:
                  <SyntaxHighlight lang="yaml">{TRAVIS_EXAMPLE}</SyntaxHighlight>
                </li>
              </ol>
              <p>
                For more detailed instructions, see the{' '}
                <a href="https://github.com/getsentry/zeus#user-guide">User Guide</a> on
                GitHub
              </p>
            </Section>
            <Section>
              <h3>Zeus is Open Source</h3>
              <p>
                The entirety of Zeus &mdash; including the infrastructure that runs
                zeus.ci &mdash; is on{' '}
                <a href="https://github.com/getsentry/zeus">GitHub</a>.
              </p>
              <p>
                Want to help improve Zeus? We suggest opening a discussion on the{' '}
                <a href="https://github.com/getsentry/zeus/issues">issue tracker</a> to
                get started.
              </p>
              <p>
                Hosting is graciously sponsored by <a href="https://sentry.io">Sentry</a>,
                but this project is not affiliated other than it&apos;s built by the team
                behind Sentry.
              </p>
            </Section>

            <GetStarted>
              <p>Ready to get started with Zeus?</p>
              <GitHubLoginButton />
            </GetStarted>
          </Container>
        </Body>
        <Footer>
          <Container>
            <a
              href="https://github.com/getsentry/zeus"
              style={{color: 'inherit', fontWeight: 500}}>
              Zeus
            </a>{' '}
            is Open Source Software
          </Container>
        </Footer>
      </WelcomeWrapper>
    );
  }
}

const WelcomeWrapper = styled.div`
  font-size: 18px;
`;

const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

const Header = styled.div`
  padding: 40px 0;
  background: #7b6be6;
  color: #fff;
`;

const Nav = styled.div`
  float: right;

  a {
    color: #fff;

    &:active,
    &:focus,
    &:hover {
      color: #fff;
    }
  }
`;

const Hero = styled.div`
  margin-bottom: 40px;
  padding: 20px;
  background: #7b6be6;
  color: #fff;
  text-align: center;
`;

const HeroImage = styled.div`
  margin: 0 auto 20px;
`;

const Body = styled.div`
  margin-bottom: 40px;
`;

const Section = styled.div`
  margin-bottom: 40px;

  > ol > li {
    margin-bottom: 20px;
  }
`;

const GetStarted = styled.div`
  border: 4px solid #111;
  text-align: center;
  padding: 20px;
`;

const Footer = styled.div`
  text-align: center;
  color: #333;
  font-size: 0.8em;
  padding: 20px 0;
`;
