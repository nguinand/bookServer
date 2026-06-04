<script lang="ts">
	import { goto } from '$app/navigation';
	import GradientRing, { type GradientRingState } from '$lib/components/GradientRing.svelte';

	let ringState = $state<GradientRingState>('open');
	let isRegisterTransitionActive = $state(false);

	function handleRegisterClick(event: MouseEvent) {
		event.preventDefault();

		if (isRegisterTransitionActive) {
			return;
		}

		isRegisterTransitionActive = true;
		ringState = 'closing';
	}

	function handleRingClosed() {
		if (!isRegisterTransitionActive) {
			return;
		}

		ringState = 'closed';
		void goto('/signup');
	}
</script>

<div class="flex min-h-screen items-center justify-center p-4">
	<GradientRing state={ringState} onclosed={handleRingClosed}>
		<div class="landing-content">
			<div class="app-title">Reader Robin</div>
			<div class="landing-actions">
				<a href="/login" class="landing-btn">Login</a>
				<a
					href="/signup"
					class="landing-btn"
					aria-disabled={isRegisterTransitionActive}
					onclick={handleRegisterClick}
				>
					Register
				</a>
			</div>
		</div>
	</GradientRing>
</div>

<style>
	.landing-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: clamp(1.5rem, 11cqw, 4.5rem);
		width: 100%;
		height: 100%;
	}

	.app-title {
		max-width: 78cqw;
		color: #1f2937;
		font-size: clamp(1.5rem, 10cqw, 4.25rem);
		font-weight: 700;
		line-height: 1;
		text-align: center;
		text-wrap: balance;
	}

	.landing-actions {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: clamp(0.75rem, 3.25cqw, 1.25rem);
		transform: translateY(clamp(0.25rem, 3cqw, 1.5rem));
	}

	.landing-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: clamp(8rem, 44cqw, 14rem);
		max-width: 80cqw;
		min-height: clamp(2.75rem, 10cqw, 3.5rem);
		padding: clamp(0.625rem, 2.5cqw, 0.875rem) clamp(1rem, 4cqw, 1.25rem);
		border: 3px solid #1f2937;
		border-radius: 9999px;
		color: #1f2937;
		font-size: clamp(0.95rem, 3.3cqw, 1.125rem);
		font-weight: 500;
		text-decoration: none;
		transition:
			background-color 0.15s ease,
			color 0.15s ease;
	}

	.landing-btn:hover {
		background-color: #1f2937;
		color: #fcfcfc;
	}

	.landing-btn[aria-disabled='true'] {
		pointer-events: none;
	}
</style>
