import React from 'react';
import Icon from 'react-icon-base';

function IconCircleCross(props) {
  return (
    <Icon viewBox="0 0 15 15" {...props}>
      <g stroke="currentColor" strokeWidth="1" fill="none">
        <circle cx="7.5" cy="7.5" r="7" />
        <path d="M4.5,4.5 L10.5,10.5" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M4.5,10.5 L10.5,4.5" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    </Icon>
  );
}

export default IconCircleCross;
