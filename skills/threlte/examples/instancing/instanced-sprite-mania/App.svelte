<script lang="ts">
	import { Canvas, T } from '@threlte/core';
	import { OrbitControls } from '@threlte/extras';
	import { MathUtils } from 'three';
	import Scene from './Scene.svelte';
	import Settings from './Settings.svelte';

	let billboarding = $state(true);
	let fps = $state(9);
</script>

<div>
	<Canvas>
		<T.PerspectiveCamera
			makeDefault
			position.z={14}
			position.y={4}
		>
			<OrbitControls
				autoRotate
				autoRotateSpeed={0.5}
				minPolarAngle={MathUtils.DEG2RAD * 65}
				maxPolarAngle={MathUtils.DEG2RAD * 85}
			/>
		</T.PerspectiveCamera>

		<Scene
			{billboarding}
			{fps}
		/>
	</Canvas>

	<Settings
		bind:billboarding
		bind:fps
	/>
</div>

<style>
	div {
		height: 100%;
	}
</style>
