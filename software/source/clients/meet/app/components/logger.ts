import {
    setLogLevel as setClientSdkLogLevel,
    setLogExtension as setClientSdkLogExtension,
    LogLevel as LogLevelEnum,
  } from 'livekit-client';
  import loglevel from 'loglevel'
  
  export const log = loglevel.getLogger('lk-components-js');
  log.setDefaultLevel('WARN');
  
  type LogLevel = Parameters<typeof setClientSdkLogLevel>[0];
  type SetLogLevelOptions = {
    liveKitClientLogLevel?: LogLevel;
  };
  
  /**
   * Set the log level for both the `@livekit/components-react` package and the `@livekit-client` package.
   * To set the `@livekit-client` log independently, use the `liveKitClientLogLevel` prop on the `options` object.
   * @public
   */
  export function setLogLevel(level: LogLevel, options: SetLogLevelOptions = {}): void {
    log.setLevel(level);
    setClientSdkLogLevel(options.liveKitClientLogLevel ?? level);
  }
  
  type LogExtension = (level: LogLevel, msg: string, context?: object) => void;
  type SetLogExtensionOptions = {
    liveKitClientLogExtension?: LogExtension;
  };
  
  /**
   * Set the log extension for both the `@livekit/components-react` package and the `@livekit-client` package.
   * To set the `@livekit-client` log extension, use the `liveKitClientLogExtension` prop on the `options` object.
   * @public
   */
  export function setLogExtension(extension: LogExtension, options: SetLogExtensionOptions = {}) {
    const originalFactory = log.methodFactory;
  
    log.methodFactory = (methodName, configLevel, loggerName) => {
      const rawMethod = originalFactory(methodName, configLevel, loggerName);
  
      const logLevel = LogLevelEnum[methodName];
      const needLog = logLevel >= configLevel && logLevel < LogLevelEnum.silent;
  
      return (msg, context?: [msg: string, context: object]) => {
        if (context) rawMethod(msg, context);
        else rawMethod(msg);
        if (needLog) {
          extension(logLevel, msg, context);
        }
      };
    };
    log.setLevel(log.getLevel()); // Be sure to call setLevel method in order to apply plugin
    setClientSdkLogExtension(options.liveKitClientLogExtension ?? extension);
  }
  