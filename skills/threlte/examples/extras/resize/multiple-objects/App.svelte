<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let resize = $state(true);
</script>

<Pane
	position="fixed"
	title="objects"
>
	<Checkbox
		bind:value={resize}
		label="resize"
	/>
</Pane>

<div>
	<Canvas>
		<Scene {resize} />
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
