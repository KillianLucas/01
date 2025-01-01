import * as React from 'react';
import { mergeProps as mergePropsReactAria } from './mergeProps'
import { log } from './logger';
import clsx from 'clsx';

/** @internal */
export function isProp<U extends HTMLElement, T extends React.HTMLAttributes<U>>(
  prop: T | undefined,
): prop is T {
  return prop !== undefined;
}

/** @internal */
export function mergeProps<
  U extends HTMLElement,
  T extends Array<React.HTMLAttributes<U> | undefined>,
>(...props: T) {
  return mergePropsReactAria(...props.filter(isProp));
}

/** @internal */
export function cloneSingleChild(
  children: React.ReactNode | React.ReactNode[],
  props?: Record<string, any>,
  key?: any,
) {
  return React.Children.map(children, (child) => {
    // Checking isValidElement is the safe way and avoids a typescript
    // error too.
    if (React.isValidElement(child) && React.Children.only(children)) {
      if (child.props.class) {
        // make sure we retain classnames of both passed props and child
        props ??= {};
        props.class = clsx(child.props.class, props.class);
        props.style = { ...child.props.style, ...props.style };
      }
      return React.cloneElement(child, { ...props, key });
    }
    return child;
  });
}

/**
 * @internal
 */
export function warnAboutMissingStyles(el?: HTMLElement) {
  if (
    typeof window !== 'undefined' &&
    typeof process !== 'undefined' &&
    // eslint-disable-next-line turbo/no-undeclared-env-vars
    (process?.env?.NODE_ENV === 'dev' ||
      // eslint-disable-next-line turbo/no-undeclared-env-vars
      process?.env?.NODE_ENV === 'development')
  ) {
    const target = el ?? document.querySelector('.lk-room-container');
    if (target && !getComputedStyle(target).getPropertyValue('--lk-has-imported-styles')) {
      log.warn(
        "It looks like you're not using the `@livekit/components-styles package`. To render the UI with the default styling, please import it in your layout or page.",
      );
    }
  }
}
