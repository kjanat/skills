<script>
	import { Canvas } from '@threlte/core';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let debug = $state(true);
</script>

<Pane
	title="Virtual Environment"
	position="fixed"
>
	<Checkbox
		bind:value={debug}
		label="debug"
	/>
</Pane>

<div>
	<Canvas>
		<Scene {debug} />
	</Canvas>
</div>

<style>
	div {
		background-color: black;
		width: 100%;
		height: 100%;
	}
</style>
