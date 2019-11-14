import React from 'react';
import {Link} from 'react-router';
import styled from '@emotion/styled';

import ObjectResult from './ObjectResult';
import Tooltip from './Tooltip';

export default styled(({repo, build, children, className, to}) => {
  return (
    <Tooltip
      label={
        <React.Fragment>
          <h6>{`#${build.number}: ${build.label}`}</h6>
          <ObjectResult data={build} mr />
          {`${build.result.toUpperCase()} after ${build.finished_at}`}
        </React.Fragment>
      }>
      <span className={className}>
        <Link to={to || `/${repo.full_name}/builds/${build.number}`}>{children}</Link>
      </span>
    </Tooltip>
  );
})`
  display: flex;
  justify-content: center;
  text-transform: none;
  width: 100%;
  color: #999;
`;
