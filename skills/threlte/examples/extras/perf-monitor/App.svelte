<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { PerfMonitor } from '@threlte/extras';
	import Scene from './Scene.svelte';
</script>

<div>
	<Canvas>
		<PerfMonitor />
		<Scene />
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
