document.addEventListener('DOMContentLoaded', () => {
    // Load saved preferences
    const contrastMode = localStorage.getItem('highContrastMode') === 'true';
    const fontSize = localStorage.getItem('fontSize') || 'medium';

    if (contrastMode) {
        document.body.classList.add('high-contrast');
    }

    document.body.classList.add(`font-${fontSize}`);

    // High contrast toggle
    document.getElementById('contrast-toggle').addEventListener('click', () => {
        document.body.classList.toggle('high-contrast');
        const isHighContrast = document.body.classList.contains('high-contrast');
        localStorage.setItem('highContrastMode', isHighContrast);
    });

    // Font size adjustment
    const fontSizeSelector = document.getElementById('font-size-selector');

    fontSizeSelector.addEventListener('change', (event) => {
        const selectedFontSize = event.target.value;
        document.body.classList.remove('font-small', 'font-medium', 'font-large');
        document.body.classList.add(`font-${selectedFontSize}`);
        localStorage.setItem('fontSize', selectedFontSize);
    });

    // Set initial font size from localStorage
    fontSizeSelector.value = fontSize;
});
