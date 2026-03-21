<script lang="ts">
	import { List, Pane, ThemeUtils } from 'svelte-tweakpane-ui';

	export let controls: '<TrackballControls>' | '<OrbitControls>' = '<OrbitControls>';
</script>

<Pane
	theme={ThemeUtils.presets.light}
	position="fixed"
	title="TransformControls"
>
	<List
		label="Camera Controls"
		bind:value={controls}
		options={{
			'<TrackballControls>': '<TrackballControls>',
			'<OrbitControls>': '<OrbitControls>',
		}}
	/>
</Pane>
