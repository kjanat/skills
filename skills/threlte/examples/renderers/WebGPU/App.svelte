<script lang="ts">
	import { Canvas, extend } from '@threlte/core';
	import * as THREE from 'three/webgpu';
	import Scene from './Scene.svelte';

	extend(THREE);
</script>

<div>
	<Canvas
		createRenderer={(canvas) => {
			return new THREE.WebGPURenderer({
				canvas,
				antialias: true,
				forceWebGL: false,
			});
		}}
	>
		<Scene />
	</Canvas>
</div>

<style>
	div {
		height: 100%;
	}
</style>
