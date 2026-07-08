document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;

  toggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);

    try {
      localStorage.setItem('theme-preference', newTheme);
    } catch (e) {
      console.warn('Could not save theme preference:', e);
    }
  });
});
