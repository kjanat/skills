<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { Checkbox, Pane } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	let follow = $state(true);
</script>

<Pane
	title="Billboard"
	position="fixed"
>
	<Checkbox
		label="follow"
		bind:value={follow}
	/>
</Pane>

<Canvas>
	<Scene {follow} />
</Canvas>
