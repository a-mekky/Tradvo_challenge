
function runTest(event, appId) {
    event.preventDefault();
    var link = event.currentTarget;
    var spinnerContainer = document.getElementById('spinner-container-' + appId);

    // Hide the link and show the spinner
    link.style.display = 'none';
    spinnerContainer.style.display = 'block';

    // Disable all other links
    var allLinks = document.querySelectorAll('a');
    allLinks.forEach(function(l) {
        if (l !== link) {
            l.style.pointerEvents = 'none';
            l.style.color = 'gray'; // Optional: Change color to indicate disabled state
        }
    });

    // Redirect to the run_test view
    window.location.href = '/run_test/' + appId + '/';
}
