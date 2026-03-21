<script>
	import { Canvas } from '@threlte/core';
	import { Studio } from '@threlte/studio';
	import Scene from './Scene.svelte';
	import Tour from './Tour/Tour.svelte';
</script>

<div>
	<Canvas>
		<Studio transient>
			<Scene />
			<Tour />
		</Studio>
	</Canvas>

	<div id="tour-target"></div>
</div>

<style>
	:global(body) {
		margin: 0;
	}

	div {
		width: 100%;
		height: 100%;
	}
</style>
