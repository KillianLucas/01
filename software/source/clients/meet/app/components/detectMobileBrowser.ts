/**
 * @internal
 */
export function isWeb(): boolean {
    return typeof document !== 'undefined';
  }
  
  /**
   * Mobile browser detection based on `navigator.userAgent` string.
   * Defaults to returning `false` if not in a browser.
   *
   * @remarks
   * This should only be used if feature detection or other methods do not work!
   *
   * @see https://developer.mozilla.org/en-US/docs/Web/HTTP/Browser_detection_using_the_user_agent#mobile_device_detection
   */
  export function isMobileBrowser(): boolean {
    return isWeb() ? /Mobi/i.test(window.navigator.userAgent) : false;
  }
  