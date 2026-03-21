<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { List, type ListOptions, Pane } from 'svelte-tweakpane-ui';
	import { NoToneMapping } from 'three';
	import Scene from './Scene.svelte';

	const options: ListOptions<number> = {
		logo: 0,
		ordering: 1,
	};
	let selection = 0;
</script>

<div>
	<Canvas toneMapping={NoToneMapping}>
		<Scene {selection} />
	</Canvas>
</div>

<Pane
	position="fixed"
	title="SVG"
>
	<List
		bind:value={selection}
		label="scene"
		{options}
	></List>
</Pane>

<style>
	div {
		height: 100%;
	}
</style>
