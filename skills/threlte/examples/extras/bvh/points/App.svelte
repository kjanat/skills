<script lang="ts">
	import { Canvas } from '@threlte/core';
	import { type BVHOptions, BVHSplitStrategy } from '@threlte/extras';
	import { Checkbox, List, Pane, Slider } from 'svelte-tweakpane-ui';
	import Scene from './Scene.svelte';

	const options = $state<
		Required<BVHOptions> & { helper: boolean; firstHitOnly: boolean }
	>({
		enabled: true,
		strategy: BVHSplitStrategy.SAH,
		indirect: false,
		verbose: false,
		maxDepth: 40,
		maxLeafTris: 20,
		setBoundingBox: true,

		firstHitOnly: false,
		helper: false,
	});
</script>

<Pane
	title="bvh"
	position="fixed"
>
	<Checkbox
		label="enabled"
		bind:value={options.enabled}
	/>
	<Checkbox
		label="helper"
		bind:value={options.helper}
	/>
	<Checkbox
		label="firstHitOnly"
		bind:value={options.firstHitOnly}
	/>
	<Checkbox
		label="setBoundingBox"
		bind:value={options.setBoundingBox}
	/>
	<List
		bind:value={options.strategy}
		label="strategy"
		options={{
			SAH: BVHSplitStrategy.SAH,
			CENTER: BVHSplitStrategy.CENTER,
			AVERAGE: BVHSplitStrategy.AVERAGE,
		}}
	/>
	<Slider
		label="maxDepth"
		bind:value={options.maxDepth}
		step={1}
	/>
	<Slider
		label="maxLeafTris"
		bind:value={options.maxLeafTris}
		step={1}
	/>
</Pane>

<Canvas>
	<Scene {...options} />
</Canvas>
