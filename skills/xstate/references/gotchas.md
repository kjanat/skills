# Gotchas

Common mistakes and v4 → v5 migration pitfalls.

## v4 → v5 breaking changes

| v4 pattern                          | v5 replacement                          | Notes                                                  |
| ----------------------------------- | --------------------------------------- | ------------------------------------------------------ |
| `createMachine({ ... })`            | `setup({}).createMachine({})`           | `setup()` required for type-safe actions/guards/actors |
| `Machine()`                         | removed                                 | Use `setup().createMachine()`                          |
| `interpret(machine)`                | `createActor(machine)`                  |                                                        |
| `service.start()`                   | `actor.start()`                         |                                                        |
| `service.send('EVENT')`             | `actor.send({ type: 'EVENT' })`         | String events removed; always use objects              |
| `service.state`                     | `actor.getSnapshot()`                   |                                                        |
| `context: { ... }` (static)         | `context: ({ input }) => ({})`          | Context factory for dynamic initial values             |
| `actions: (ctx, evt) => {}`         | `actions: ({ context, event }) => {}`   | Destructured single-object param                       |
| `guards: (ctx, evt) => bool`        | `guards: ({ context, event }) => bool`  | Same destructured pattern                              |
| `services: {}`                      | `actors: {}` in `setup()`               | Renamed                                                |
| `invoke: { src: (ctx) => fetch() }` | `invoke: { src: 'namedActor' }`         | Must use named actors from `setup()`                   |
| `send()` action creator             | `sendTo()` or `raise()`                 | `send()` removed                                       |
| `assign({ key: (ctx) => val })`     | `assign({ key: ({ context }) => val })` | Destructured param                                     |
| `activities`                        | removed                                 | Use invoked actors instead                             |
| `state.matches('a.b')`              | `snapshot.matches({ a: 'b' })`          | Object syntax for nested                               |
| `.withConfig()`                     | `.provide()`                            |                                                        |
| `.withContext()`                    | `createActor(machine, { input })`       | Use input system                                       |

## Common mistakes

### Forgetting `setup()`

```ts
// WRONG — no type inference for actions/guards
const machine = createMachine({
	actions: { foo: () => {} }, // won't type-check params
});

// RIGHT
const machine = setup({
	actions: { foo: (_, params: { x: number }) => {} },
}).createMachine({/* ... */});
```

### String events

```ts
// WRONG — string events removed in v5
actor.send('TOGGLE');

// RIGHT
actor.send({ type: 'TOGGLE' });
```

### Inline actor sources

```ts
// WRONG — inline functions not allowed as invoke src in v5
invoke: { src: (context) => fetch(`/api/${context.id}`) }

// RIGHT — declare in setup, reference by name
setup({
  actors: {
    fetchData: fromPromise(async ({ input }: { input: { id: string } }) =>
      fetch(`/api/${input.id}`).then(r => r.json())
    ),
  },
})
// ...
invoke: { src: 'fetchData', input: ({ context }) => ({ id: context.id }) }
```

### Mutating context directly

```ts
// WRONG — mutates context directly
entry: ({ context }) => {
  context.count += 1
},

// RIGHT — use assign action
entry: assign({ count: ({ context }) => context.count + 1 }),
```

### Missing initial state

```ts
// WRONG — no initial specified
states: { a: {}, b: {} }

// RIGHT
initial: 'a',
states: { a: {}, b: {} }
```

### Accessing snapshot wrong

```ts
// WRONG — .state removed
const value = actor.state.value;

// RIGHT
const snapshot = actor.getSnapshot();
const value = snapshot.value;
const ctx = snapshot.context;
```

## Framework-specific gotchas

### React

- `useSelector(actorRef, selector)` — always pass a selector, don't subscribe to entire snapshot
- `useMachine` removed in `@xstate/react` v4+ — use `useActor` or `useActorRef`
- Selectors should be referentially stable (define outside component or `useCallback`)

### Svelte

- Use `useActor` from `@xstate/svelte`
- Snapshot is a Svelte store — access with `$snapshot`

### Vue

- Use `useMachine` from `@xstate/vue`
- Returns reactive refs

## Debugging tips

- Use `@stately/inspect` for visual debugging
- `actor.subscribe(snapshot => console.log(snapshot))` — log all transitions
- Check `snapshot.status` for actor completion: `'active'`, `'done'`, `'error'`, `'stopped'`
- `snapshot.can({ type: 'EVENT' })` — check if event would cause transition
