<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { AsciiRenderer } from '@threlte/extras';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import type { AsciiEffectOptions } from 'three/examples/jsm/Addons.js';
	import Scene from './Scene.svelte';

	let color = $state(false);

	const options: AsciiEffectOptions = $derived({ color });
</script>

<Pane
	title="render on update"
	position="fixed"
>
	<Checkbox
		bind:value={color}
		label="color"
	/>
</Pane>

<div>
	<Canvas>
		<AsciiRenderer
			autoRender={false}
			{options}
		>
			{#snippet children({ asciiEffect })}
				<Scene {asciiEffect} />
			{/snippet}
		</AsciiRenderer>
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
