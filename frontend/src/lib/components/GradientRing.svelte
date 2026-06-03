<script lang="ts" module>
	export type GradientRingState = 'open' | 'closing' | 'closed' | 'opening';
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';

	type Props = {
		state?: GradientRingState;
		children?: Snippet;
		onclosed?: () => void;
	};

	let { state = 'open', children, onclosed }: Props = $props();

	function handleTransitionEnd(event: TransitionEvent) {
		if (event.target !== event.currentTarget || event.propertyName !== 'transform') {
			return;
		}

		if (state === 'closing') {
			onclosed?.();
		}
	}
</script>

<div class="gradient-ring-frame">
	<div class="gradient-ring" data-state={state} ontransitionend={handleTransitionEnd}>
		<div class="gradient-ring-inner">
			<div class="gradient-ring-content" aria-hidden={state === 'closed' || state === 'closing'}>
				{#if children}
					{@render children()}
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	@property --gradient-ring-angle {
		syntax: '<angle>';
		initial-value: 0deg;
		inherits: false;
	}

	.gradient-ring-frame {
		--gradient-ring-size: clamp(26rem, 70vw, 42rem);
		width: min(var(--gradient-ring-size), calc(100vw - 2rem), calc(100vh - 2rem));
		aspect-ratio: 1;
		display: grid;
		place-items: center;
	}

	.gradient-ring {
		width: 100%;
		height: 100%;
		border-radius: 50%;
		--gradient-ring-angle: 0deg;
		background: conic-gradient(
			from var(--gradient-ring-angle) in oklch,
			#256eff,
			#ff495c,
			#3ddc97,
			#256eff
		);
		display: grid;
		place-items: center;
		padding: clamp(1rem, 3vw, 1.5rem);
		transform-origin: center;
		overflow: hidden;
		animation: gradient-ring-spin 8s linear infinite;
		transition:
			transform 420ms cubic-bezier(0.65, 0, 0.35, 1),
			border-radius 420ms cubic-bezier(0.65, 0, 0.35, 1);
	}

	.gradient-ring[data-state='closed'],
	.gradient-ring[data-state='closing'] {
		border-radius: 50% / 10%;
		transform: scaleY(0);
	}

	.gradient-ring[data-state='open'],
	.gradient-ring[data-state='opening'] {
		border-radius: 50%;
		transform: scaleY(1);
	}

	@keyframes gradient-ring-spin {
		to {
			--gradient-ring-angle: 360deg;
		}
	}

	.gradient-ring-inner {
		width: 100%;
		height: 100%;
		border-radius: inherit;
		background: #fcfcfc;
		display: grid;
		place-items: center;
		overflow: hidden;
	}

	.gradient-ring-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		width: 100%;
		height: 100%;
		opacity: 1;
		transform: scale(1);
		transition:
			opacity 180ms ease,
			transform 240ms ease;
	}

	.gradient-ring[data-state='closed'] .gradient-ring-content,
	.gradient-ring[data-state='closing'] .gradient-ring-content {
		opacity: 0;
		pointer-events: none;
		transform: scale(0.92);
	}
</style>
