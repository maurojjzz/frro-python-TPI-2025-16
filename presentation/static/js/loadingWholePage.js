document.addEventListener('DOMContentLoaded', function () {
	const loading = document.querySelector('.loading-container');
	const form = document.querySelector('.login-container form');

	if (!loading) return;

	loading.classList.remove('loading-hidden');
	setTimeout(() => loading.classList.add('loading-hidden'), 500);

    if (form) {
		form.addEventListener('submit', () => {
			loading.classList.remove('loading-hidden');
		});
	}
});

