<script>
	import { Canvas } from '@threlte/core';
	import { Suspense } from '@threlte/extras';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let debug = $state(true);
	let mixEnvironment = $state(true);
</script>

<Pane
	title="Virtual Environment"
	position="fixed"
>
	<Checkbox
		bind:value={debug}
		label="debug"
	/>
	<Checkbox
		bind:value={mixEnvironment}
		label="Mix Environment Map"
	/>
</Pane>

<div>
	<Canvas>
		<Scene
			{debug}
			{mixEnvironment}
		/>
	</Canvas>
</div>

<style>
	div {
		background-color: black;
		width: 100%;
		height: 100%;
	}
</style>
