import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {LightAsync as SyntaxHighlighter} from 'react-syntax-highlighter/dist/cjs';
import {atomOneLight as highlightStyle} from 'react-syntax-highlighter/dist/cjs/styles/hljs';

const mapping = {
  py: 'python',
  gyp: 'python',
  wsgi: 'python',
  htm: 'html',
  xhtml: 'html',
  erl: 'erlang',
  jsp: 'java',
  js: 'javascript',
  jsx: 'javascript',
  pl: 'perl',
  rss: 'xml',
  atom: 'xml',
  xsl: 'xml',
  plist: 'xml',
  rb: 'ruby',
  builder: 'ruby',
  gemspec: 'ruby',
  podspec: 'ruby',
  thor: 'ruby',
  diff: 'patch',
  hs: 'haskell',
  icl: 'haskell',
  php3: 'php',
  php4: 'php',
  php5: 'php',
  php6: 'php',
  sh: 'bash',
  zsh: 'bash',
  st: 'smalltalk',
  as: 'actionscript',
  apacheconf: 'apache',
  osacript: 'applescript',
  b: 'brainfuck',
  bf: 'brainfuck',
  clj: 'clojure',
  coffee: 'coffeescript',
  cson: 'coffescript',
  iced: 'coffescript',
  hh: 'cpp',
  jinja: 'django',
  bat: 'dos',
  cmd: 'dos',
  fs: 'fsharp',
  hbs: 'handlebars',
  mk: 'makefile',
  mak: 'makefile',
  md: 'markdown',
  mkdown: 'markdown',
  mkd: 'markdown',
  nginxconf: 'nginx',
  m: 'objectivec',
  mm: 'objectivec',
  ml: 'ocaml',
  rs: 'rust',
  sci: 'scilab',
  vb: 'vbnet',
  vbs: 'vbscript'
};

const filenameToLanguage = f => {
  let ext = f.split('.').reverse()[0];
  return mapping[ext] || ext;
};

export default class SyntaxHighlight extends Component {
  static propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
    lang: PropTypes.string,
    filename: PropTypes.string
  };

  render() {
    let {lang, filename} = this.props;
    if (!lang && filename) {
      lang = filenameToLanguage(filename);
    }

    return (
      <SyntaxHighlighter
        style={highlightStyle}
        language={lang}
        customStyle={{padding: 0}}
        className={this.props.className}>
        {this.props.children}
      </SyntaxHighlighter>
    );
  }
}
