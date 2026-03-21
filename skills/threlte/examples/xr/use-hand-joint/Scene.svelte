<script lang="ts">
	import { T } from '@threlte/core';
	import { Text } from '@threlte/extras';
	import { Attractor, Debug } from '@threlte/rapier';
	import { Hand, useXR, XR } from '@threlte/xr';
	import Cubes from './Cube.svelte';
	import JointCollider from './JointBody.svelte';

	const { isHandTracking } = useXR();

	let debug = false;
</script>

{#if debug}
	<Debug />
{/if}

<XR>
	<Hand
		left
		onpinchend={() => (debug = !debug)}
	/>
	<Hand
		right
		onpinchend={() => (debug = !debug)}
	/>

	{#if $isHandTracking}
		{#each { length: 25 } as _, jointIndex}
			<JointCollider
				{jointIndex}
				hand="left"
			/>
			<JointCollider
				{jointIndex}
				hand="right"
			/>
		{/each}
	{/if}

	<Text
		position={[0, 1.7, -1]}
		text="Pinch to toggle physics debug."
	/>
</XR>

<Cubes />

<T.PerspectiveCamera
	makeDefault
	position={[0, 1, 1]}
	oncreate={(ref) => ref.lookAt(0, 1.8, 0)}
/>

<T.AmbientLight />

<T.SpotLight
	position={[1, 8, 1]}
	angle={0.3}
	penumbra={1}
	intensity={30}
	castShadow
	target.x={0}
	target.y={1.8}
	target.z={0}
/>

<Attractor
	range={50}
	strength={0.000001}
	position={[0, 1.7, 0]}
/>
