<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let showScene = true;
</script>

<Pane
	title=""
	position="fixed"
>
	<Checkbox bind:value={showScene} />
</Pane>

<div>
	<Canvas>
		{#if showScene}
			<Scene />
		{/if}
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
