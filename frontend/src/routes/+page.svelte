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
		gap: clamp(2.25rem, 8vw, 4.5rem);
		width: 100%;
		height: 100%;
	}

	.app-title {
		color: #1f2937;
		font-size: clamp(2.25rem, 6vw, 4.25rem);
		font-weight: 700;
		line-height: 1;
		text-align: center;
	}

	.landing-actions {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.25rem;
		transform: translateY(clamp(0.75rem, 3vw, 1.5rem));
	}

	.landing-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 14rem;
		min-height: 3.5rem;
		padding: 0.875rem 1.25rem;
		border: 3px solid #1f2937;
		border-radius: 9999px;
		color: #1f2937;
		font-size: 1.125rem;
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
