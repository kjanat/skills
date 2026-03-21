<script lang="ts">
	import { T } from '@threlte/core';
	import { OrbitControls } from '@threlte/extras';

	type SceneProps = { autoRotate: boolean };

	let { autoRotate = true }: SceneProps = $props();
</script>

<T.DirectionalLight position={5} />

<T.PerspectiveCamera
	makeDefault
	position.z={5}
>
	<OrbitControls {autoRotate} />
</T.PerspectiveCamera>

<T.Mesh>
	<T.MeshNormalMaterial />
	<T.TorusKnotGeometry />
</T.Mesh>
