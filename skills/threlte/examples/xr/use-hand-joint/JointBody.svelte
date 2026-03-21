<script lang="ts">
	import type { RigidBody as RapierRigidBody } from '@dimforge/rapier3d-compat';
	import { useTask } from '@threlte/core';
	import { Collider, RigidBody } from '@threlte/rapier';
	import { handJoints, useHandJoint } from '@threlte/xr';

	interface Props {
		jointIndex: number;
		hand: 'left' | 'right';
	}

	let { jointIndex, hand }: Props = $props();

	let body = $state.raw<RapierRigidBody>();

	const joint = useHandJoint(hand, handJoints[jointIndex]!);

	const radius = $derived($joint?.jointRadius);

	useTask(
		() => {
			if (joint.current === undefined || body === undefined) return;

			const { x, y, z } = joint.current.position;
			body.setNextKinematicTranslation({ x, y, z });
		},
		{
			running: () => body !== undefined && $joint !== undefined && radius !== undefined,
		},
	);
</script>

{#if radius}
	<RigidBody
		bind:rigidBody={body}
		type="kinematicPosition"
	>
		<Collider
			shape="ball"
			args={[radius]}
		/>
	</RigidBody>
{/if}
