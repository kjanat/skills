<script lang="ts">
	import { T, useTask } from '@threlte/core';
	import { Float, Instance, InstancedMesh, Outlines, Wireframe } from '@threlte/extras';
	import type { InstancedMesh as ThreeInstancedMesh } from 'three';
	import { Quaternion, type QuaternionTuple, Vector3, type Vector3Tuple } from 'three';
	import Character from './Character.svelte';

	let { wireframeProps } = $props();

	let boxes = $state.raw<ThreeInstancedMesh>();

	let poses: {
		position: Vector3Tuple;
		quaternion: QuaternionTuple;
	}[] = [];

	const numCubes = 70;
	for (let i = 0; i < numCubes; i += 1) {
		const position = new Vector3().randomDirection().multiplyScalar(1)
			.toArray();
		position[1] += 1.2;
		poses.push({
			position,
			quaternion: new Quaternion().random().toArray(),
		});
	}

	useTask((delta) => {
		if (boxes) boxes.rotation.y += delta / 60;
	});
</script>

<T.PerspectiveCamera
	makeDefault
	position={[-0.8, 1.2, 1.7]}
	oncreate={(ref) => {
		ref.lookAt(0, 1, 0);
	}}
/>

<T.AmbientLight />
<T.DirectionalLight
	position={[10, 5, 5]}
	castShadow
/>

<Character {wireframeProps} />

<T.Mesh
	rotation.x={-90 * (Math.PI / 180)}
	receiveShadow
>
	<T.CircleGeometry args={[3, 72]} />
	<T.MeshStandardMaterial color={'white'} />

	<Outlines
		color="red"
		thickness={10}
	/>
</T.Mesh>

<InstancedMesh
	bind:ref={boxes}
	castShadow
>
	<T.BoxGeometry args={[0.07, 0.07, 0.07]} />
	<T.MeshStandardMaterial />

	<Wireframe {...wireframeProps} />
	{#each poses as { position, quaternion }, index}
		<Float seed={Math.random() * index}>
			<Instance
				{position}
				{quaternion}
			/>
		</Float>
	{/each}
</InstancedMesh>
