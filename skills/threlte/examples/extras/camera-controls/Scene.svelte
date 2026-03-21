<script lang="ts">
	import { T } from '@threlte/core';
	import { CameraControls, type CameraControlsRef, Grid } from '@threlte/extras';
	import { Mesh } from 'three';

	let {
		controls = $bindable(),
		mesh = $bindable(),
	}: {
		controls?: CameraControlsRef;
		mesh?: Mesh;
	} = $props();
</script>

<CameraControls
	bind:ref={controls}
	oncreate={(ref) => {
		ref.setPosition(5, 5, 5);
	}}
/>

<T.Mesh
	bind:ref={mesh}
	position.y={0.5}
>
	<T.BoxGeometry />
	<T.MeshBasicMaterial
		color="#ff3e00"
		wireframe
	/>
</T.Mesh>

<Grid
	sectionColor="#ff3e00"
	sectionThickness={1}
	cellColor="#cccccc"
	gridSize={40}
/>
