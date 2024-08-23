
function runTest(event, appId) {
    event.preventDefault();
    var link = event.currentTarget;
    var spinnerContainer = document.getElementById('spinner-container-' + appId);

    // Hide the link and show the spinner
    link.style.display = 'none';
    spinnerContainer.style.display = 'block';

    // Redirect to the run_test view
    window.location.href = '/run_test/' + appId + '/';
}
