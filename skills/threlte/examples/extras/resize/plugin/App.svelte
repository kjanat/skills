<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import { NoToneMapping } from 'three';
	import Scene from './Scene.svelte';

	let showCylinder = $state(true);
	let auto = $state(true);
</script>

<Pane
	title="Resize"
	position="fixed"
>
	<Checkbox
		label="Show Cylinder"
		bind:value={showCylinder}
	/>
	<Checkbox
		label="Auto"
		bind:value={auto}
	/>
</Pane>

<div>
	<Canvas toneMapping={NoToneMapping}>
		<Scene
			{showCylinder}
			{auto}
		/>
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
