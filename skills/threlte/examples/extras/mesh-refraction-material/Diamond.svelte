<script lang="ts">
	import { T, useLoader } from '@threlte/core';
	import { MeshRefractionMaterial, useDraco, useGltf } from '@threlte/extras';
	import { Mesh } from 'three';

	import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';

	let { ...props } = $props();

	type GLTFResult = {
		nodes: {
			Diamond_1_0: Mesh;
		};
		materials: {};
	};

	const dracoLoader = useDraco();
	const gltf = useGltf<GLTFResult>('/models/diamond/dflat.glb', {
		dracoLoader,
	});
	const env = useLoader(RGBELoader).load(
		'/textures/equirectangular/hdr/aerodynamics_workshop_1k.hdr',
	);
</script>

{#await gltf then { nodes }}
	<T.Mesh
		castShadow
		receiveShadow
		geometry={nodes.Diamond_1_0.geometry}
		{...props}
	>
		{#await env then e}
			<MeshRefractionMaterial
				envMap={e}
				fresnel={0.5}
				ior={2.75}
				aberrationStrength={0.04}
				bounces={3}
				color={'#ffdddd'}
			/>
		{/await}
	</T.Mesh>
{/await}
