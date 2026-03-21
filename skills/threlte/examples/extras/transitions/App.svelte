<script>
	import { Canvas } from '@threlte/core';
	import { Suspense } from '@threlte/extras';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let red = $state(true);
	let blue = $state(true);
</script>

<Pane
	title="Transitions"
	position="fixed"
>
	<Checkbox
		bind:value={red}
		label="Toggle Red"
	/>

	<Checkbox
		bind:value={blue}
		label="Toggle Blue"
	/>
</Pane>

<div>
	<Canvas>
		<Suspense>
			<Scene
				{red}
				{blue}
			/>
		</Suspense>
	</Canvas>
</div>

<style>
	:global(body) {
		margin: 0;
	}

	div {
		width: 100%;
		height: 100%;
	}
</style>
