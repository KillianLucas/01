/**
 * The TrackReference type is a logical grouping of participant publication and/or subscribed track.
 *
 */

import type { Participant, Track, TrackPublication } from 'livekit-client';
// ## TrackReference Types

/** @public */
export type TrackReferencePlaceholder = {
  participant: Participant;
  publication?: never;
  source: Track.Source;
};

/** @public */
export type TrackReference = {
  participant: Participant;
  publication: TrackPublication;
  source: Track.Source;
};

/** @public */
export type TrackReferenceOrPlaceholder = TrackReference | TrackReferencePlaceholder;

// ### TrackReference Type Predicates
/** @internal */
export function isTrackReference(trackReference: unknown): trackReference is TrackReference {
  if (typeof trackReference === 'undefined') {
    return false;
  }
  return (
    isTrackReferenceSubscribed(trackReference as TrackReference) ||
    isTrackReferencePublished(trackReference as TrackReference)
  );
}

function isTrackReferenceSubscribed(trackReference?: TrackReferenceOrPlaceholder): boolean {
  if (!trackReference) {
    return false;
  }
  return (
    trackReference.hasOwnProperty('participant') &&
    trackReference.hasOwnProperty('source') &&
    trackReference.hasOwnProperty('track') &&
    typeof trackReference.publication?.track !== 'undefined'
  );
}

function isTrackReferencePublished(trackReference?: TrackReferenceOrPlaceholder): boolean {
  if (!trackReference) {
    return false;
  }
  return (
    trackReference.hasOwnProperty('participant') &&
    trackReference.hasOwnProperty('source') &&
    trackReference.hasOwnProperty('publication') &&
    typeof trackReference.publication !== 'undefined'
  );
}

export function isTrackReferencePlaceholder(
  trackReference?: TrackReferenceOrPlaceholder,
): trackReference is TrackReferencePlaceholder {
  if (!trackReference) {
    return false;
  }
  return (
    trackReference.hasOwnProperty('participant') &&
    trackReference.hasOwnProperty('source') &&
    typeof trackReference.publication === 'undefined'
  );
}
