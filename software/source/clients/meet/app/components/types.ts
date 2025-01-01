import type { Participant, ParticipantKind, Track, TrackPublication } from 'livekit-client';
import type { TrackReference, TrackReferenceOrPlaceholder } from './track-reference-types';

// ## PinState Type
/** @public */
export type PinState = TrackReferenceOrPlaceholder[];
export const PIN_DEFAULT_STATE: PinState = [];

// ## WidgetState Types
/** @public */
export type WidgetState = {
  showChat: boolean;
  unreadMessages: number;
  showSettings?: boolean;
};
export const WIDGET_DEFAULT_STATE: WidgetState = {
  showChat: false,
  unreadMessages: 0,
  showSettings: false,
};

// ## Track Source Types
export type TrackSourceWithOptions = { source: Track.Source; withPlaceholder: boolean };

export type SourcesArray = Track.Source[] | TrackSourceWithOptions[];

// ### Track Source Type Predicates
export function isSourceWitOptions(source: SourcesArray[number]): source is TrackSourceWithOptions {
  return typeof source === 'object';
}

export function isSourcesWithOptions(sources: SourcesArray): sources is TrackSourceWithOptions[] {
  return (
    Array.isArray(sources) &&
    (sources as TrackSourceWithOptions[]).filter(isSourceWitOptions).length > 0
  );
}

// ## Loop Filter Types
export type TrackReferenceFilter = Parameters<TrackReferenceOrPlaceholder[]['filter']>['0'];
export type ParticipantFilter = Parameters<Participant[]['filter']>['0'];

// ## Other Types
/** @internal */
export interface ParticipantClickEvent {
  participant: Participant;
  track?: TrackPublication;
}

export type TrackSource<T extends Track.Source> = RequireAtLeastOne<
  { source: T; name: string; participant: Participant },
  'name' | 'source'
>;

export type ParticipantTrackIdentifier = RequireAtLeastOne<
  { sources: Track.Source[]; name: string; kind: Track.Kind },
  'sources' | 'name' | 'kind'
>;

/**
 * @beta
 */
export type ParticipantIdentifier = RequireAtLeastOne<
  { kind: ParticipantKind; identity: string },
  'identity' | 'kind'
>;

/**
 * The TrackIdentifier type is used to select Tracks either based on
 * - Track.Source and/or name of the track, e.g. `{source: Track.Source.Camera}` or `{name: "my-track"}`
 * - TrackReference (participant and publication)
 * @internal
 */
export type TrackIdentifier<T extends Track.Source = Track.Source> =
  | TrackSource<T>
  | TrackReference;

// ## Util Types
type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = Pick<T, Exclude<keyof T, Keys>> &
  {
    [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>>;
  }[Keys];

export type RequireOnlyOne<T, Keys extends keyof T = keyof T> = Pick<T, Exclude<keyof T, Keys>> &
  {
    [K in Keys]-?: Required<Pick<T, K>> & Partial<Record<Exclude<Keys, K>, undefined>>;
  }[Keys];

export type AudioSource = Track.Source.Microphone | Track.Source.ScreenShareAudio;
export type VideoSource = Track.Source.Camera | Track.Source.ScreenShare;
