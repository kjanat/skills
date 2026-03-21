import type { LumaSplatsSource, LumaSplatsThree } from '@lumaai/luma-web';
import type { Props } from '@threlte/core';
import type { Snippet } from 'svelte';

export type LumaSplatsThreeProps = Props<LumaSplatsThree> & {
	source: LumaSplatsSource;
	mode?: 'object' | 'object-env' | 'env';
	loadingAnimationEnabled?: boolean;
	particleRevealEnabled?: boolean;
	enableThreeShaderIntegration?: boolean;
	children?: Snippet<[any]>;
	[key: string]: any;
};
