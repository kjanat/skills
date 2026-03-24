# XState v5 Cheatsheet

Quick syntax reference. For full docs, see vendored `docs/` files.

## Install

```bash
npm install xstate
```

## Create a machine

```ts
import { assign, createActor, setup } from 'xstate';

const machine = setup({
	/* types, actions, guards, actors */
}).createMachine({
	id: 'toggle',
	initial: 'active',
	context: { count: 0 },
	states: {
		active: {
			entry: assign({ count: ({ context }) => context.count + 1 }),
			on: { toggle: { target: 'inactive' } },
		},
		inactive: {
			on: { toggle: { target: 'active' } },
		},
	},
});

const actor = createActor(machine);
actor.subscribe((snapshot) => console.log(snapshot.value));
actor.start();
actor.send({ type: 'toggle' });
```

## Actor types

### Promise actor

```ts
import { createActor, fromPromise } from 'xstate';

const logic = fromPromise(async () => {
	const res = await fetch('https://api.example.com/data');
	return res.json();
});
```

### Transition actor (reducer)

```ts
import { createActor, fromTransition } from 'xstate';

const logic = fromTransition(
	(state, event) => {
		switch (event.type) {
			case 'inc':
				return { ...state, count: state.count + 1 };
			default:
				return state;
		}
	},
	{ count: 0 },
);
```

### Observable actor

```ts
import { interval } from 'rxjs';
import { fromObservable } from 'xstate';
const logic = fromObservable(() => interval(1000));
```

### Callback actor

```ts
import { fromCallback } from 'xstate';

const logic = fromCallback(({ sendBack, receive }) => {
	const i = setTimeout(() => sendBack({ type: 'timeout' }), 1000);
	receive((event) => {
		if (event.type === 'cancel') clearTimeout(i);
	});
	return () => clearTimeout(i);
});
```

## Parent (nested) states

```ts
states: {
  active: {
    initial: 'one',
    states: {
      one: { on: { NEXT: { target: 'two' } } },
      two: {},
    },
    on: { NEXT: { target: 'inactive' } },
  },
  inactive: {},
}
```

## Actions

Define in `setup()`, reference by name:

```ts
const machine = setup({
	actions: {
		activate: () => {/* ... */},
		notify: (_, params: { message: string }) => {/* ... */},
	},
}).createMachine({
	states: {
		active: {
			entry: { type: 'activate' },
			exit: { type: 'deactivate' },
			on: {
				toggle: {
					target: 'inactive',
					actions: [{ type: 'notify', params: { message: 'Toggled' } }],
				},
			},
		},
	},
});
```

## Guards

```ts
const machine = setup({
	guards: {
		canToggle: ({ context }) => context.canActivate,
		isAfterTime: (_, params: { time: string }) => {
			const [h, m] = params.time.split(':');
			const now = new Date();
			return now.getHours() > +h && now.getMinutes() > +m;
		},
	},
}).createMachine({
	states: {
		inactive: {
			on: {
				toggle: [
					{ target: 'active', guard: 'canToggle' },
					{ actions: 'notifyBlocked' },
				],
			},
		},
		active: {
			on: {
				toggle: {
					guard: { type: 'isAfterTime', params: { time: '16:00' } },
					target: 'inactive',
				},
			},
		},
	},
});
```

## Invoke actors

```ts
const machine = setup({
	actors: { loadUser: fromPromise(async () => {/* ... */}) },
}).createMachine({
	states: {
		loading: {
			invoke: {
				id: 'loadUser',
				src: 'loadUser',
				onDone: {
					target: 'success',
					actions: assign({ user: ({ event }) => event.output }),
				},
				onError: { target: 'failure' },
			},
		},
	},
});
```

## Spawn actors

```ts
on: {
  loadUser: {
    actions: assign({
      userRef: ({ spawn }) => spawn('loadUserLogic'),
    }),
  },
}
```

## Input

```ts
const machine = setup({
	types: {
		context: {} as { message: string },
		input: {} as { name: string },
	},
}).createMachine({
	context: ({ input }) => ({ message: `Hello, ${input.name}` }),
});

const actor = createActor(machine, { input: { name: 'World' } });
```

## Invoke with input

```ts
invoke: {
  src: 'loadUser',
  input: { id: 3 },
  onDone: { /* ... */ },
}
```

## Type declarations in setup()

```ts
setup({
	types: {
		context: {} as { count: number },
		events: {} as
			| { type: 'inc' }
			| { type: 'dec' }
			| { type: 'incBy'; amount: number },
		actions: {} as
			| { type: 'notify'; params: { message: string } }
			| { type: 'handleChange' },
		guards: {} as
			| { type: 'canToggle' }
			| { type: 'isAfterTime'; params: { time: string } },
		children: {} as { promise1: 'someSrc' },
		delays: 'shortTimeout' | 'longTimeout',
		tags: 'loading' | 'error',
		input: number,
		output: string,
	},
});
```
