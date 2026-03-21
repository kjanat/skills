<script>
	import { Canvas } from '@threlte/core';
	import { Studio } from '@threlte/studio';
	import { NoToneMapping } from 'three';
	import Scene from './Scene.svelte';
</script>

<div>
	<Canvas toneMapping={NoToneMapping}>
		<Studio transient>
			<Scene />
		</Studio>
	</Canvas>
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
