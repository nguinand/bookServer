<div class="flex min-h-screen items-center justify-center p-4">
	<div class="gradient-ring">
		<div class="gradient-ring-inner">
			<a href="/login" class="landing-btn">Login</a>
			<a href="/signup" class="landing-btn">Register</a>
		</div>
	</div>
</div>

<style>
	@property --gradient-ring-angle {
		syntax: '<angle>';
		initial-value: 0deg;
		inherits: false;
	}

	.gradient-ring {
		width: 23.1rem;
		height: 23.1rem;
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
		padding: 20px;
		animation: gradient-ring-spin 8s linear infinite;
	}

	@keyframes gradient-ring-spin {
		to {
			--gradient-ring-angle: 360deg;
		}
	}

	.gradient-ring-inner {
		width: 100%;
		height: 100%;
		border-radius: 50%;
		background: #fcfcfc;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
	}

	.landing-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 10rem;
		padding: 0.5rem 1rem;
		border: 2px solid #1f2937;
		border-radius: 9999px;
		color: #1f2937;
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
</style>
