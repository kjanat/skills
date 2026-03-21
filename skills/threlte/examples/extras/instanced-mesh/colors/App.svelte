<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Pane, Slider } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let size = $state(10);
</script>

<Pane
	position="fixed"
	title="Instanced Colors"
>
	<Slider
		min={10}
		max={50}
		step={10}
		bind:value={size}
	/>
</Pane>

<Canvas>
	<Scene {size} />
</Canvas>
