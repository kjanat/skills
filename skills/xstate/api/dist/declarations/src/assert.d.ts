import { EventDescriptor, EventObject } from "./types.js";
type NormalizeAssertedDescriptor<TDescriptor extends string> = TDescriptor extends '*' ? string : TDescriptor extends `${infer TLeading}.*` ? TLeading | `${TLeading}.${string}` : TDescriptor;
type AssertedEvent<TEvent extends EventObject, TDescriptor extends string> = (TEvent extends {
    type: infer TType extends string;
} ? true extends (TType extends NormalizeAssertedDescriptor<TDescriptor> ? true : false) ? TEvent : never : never) | (string extends TEvent['type'] ? TEvent : never);
/**
 * Asserts that the given event object is of the specified type or types. Throws
 * an error if the event object is not of the specified types.
 * Partial wildcard descriptors such as `feedback.*` match both `feedback` and
 * its descendants, such as `feedback.good`.
 *
 * @example
 *
 * ```ts
 * // ...
 * entry: ({ event }) => {
 *   assertEvent(event, 'doNothing');
 *   // event is { type: 'doNothing' }
 * },
 * // ...
 * exit: ({ event }) => {
 *   assertEvent(event, 'greet');
 *   // event is { type: 'greet'; message: string }
 *
 *   assertEvent(event, ['greet', 'notify']);
 *   // event is { type: 'greet'; message: string }
 *   // or { type: 'notify'; message: string; level: 'info' | 'error' }
 * },
 * ```
 */
export declare function assertEvent<TEvent extends EventObject, TAssertedDescriptor extends EventDescriptor<TEvent>>(event: TEvent, type: TAssertedDescriptor | readonly TAssertedDescriptor[]): asserts event is AssertedEvent<TEvent, TAssertedDescriptor>;
export {};
