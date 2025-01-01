import * as React from 'react';
import { warnAboutMissingStyles } from './utils';

/**
 * @internal
 */
export function useWarnAboutMissingStyles() {
  React.useEffect(() => {
    warnAboutMissingStyles();
  }, []);
}
