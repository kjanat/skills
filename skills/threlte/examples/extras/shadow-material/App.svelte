<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Color, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let color = $state('#000000');
</script>

<Canvas>
	<Scene {color} />
</Canvas>
<Pane
	title="shadow material"
	position="fixed"
>
	<Color
		bind:value={color}
		label="shadow color"
	/>
</Pane>
