<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Button, Folder, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let scene = $state<Scene>();
	let animating = $state(false);

	const actions = $derived(scene?.actions);
	const action = $derived($actions?.['Take 001']);

	// start animating as soon as the action is ready
	$effect(() => {
		action?.play();
		animating = true;
	});
</script>

<Pane
	position="fixed"
	title="littlest tokyo"
>
	<Folder title="animation">
		<Button
			disabled={animating}
			on:click={() => {
				action?.play();
				animating = true;
			}}
			title="play"
		/>
		<Button
			disabled={!animating}
			on:click={() => {
				action?.stop();
				animating = false;
			}}
			title="stop"
		/>
		<Button
			disabled={!animating}
			on:click={() => {
				action?.reset();
			}}
			title="reset"
		/>
	</Folder>
</Pane>

<div>
	<Canvas>
		<Scene bind:this={scene} />
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
