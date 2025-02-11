

function toggleSuite(suite) {
    const caret = suite.querySelector('.suite-caret i');
    const caretClass = caret.classList[1];
    const allSuites = document.querySelectorAll('.suite');
    allSuites.forEach(suite => {
        suite.querySelector('.suite-caret i').classList.remove('fa-caret-down');
        suite.querySelector('.suite-caret i').classList.add('fa-caret-right');
        suite.querySelector('.suite-test-cases').style.display = 'none';
    });
    if (caretClass === 'fa-caret-right') {
        caret.classList.remove('fa-caret-right');
        caret.classList.add('fa-caret-down');
        suite.querySelector('.suite-test-cases').style.display = 'flex';
    }
}

function openFailure(failId) {
    const failure = JSON.parse(failures[failId]);
    document.getElementById('test-name').innerText = failure.name;
    document.getElementById('test-time').innerText = `${failure.time}s`;
    document.getElementById('test-file').innerText = failure.file;
    document.getElementById('test-type').innerText = failure.failure.type;
    document.getElementById('test-message').innerText = failure.failure.message;
    document.getElementById('test-traceback').innerText = failure.failure.traceback;
    document.getElementById('modal-backdrop').style.display = 'block';
    document.getElementById('failure-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeFailure() {
    document.getElementById('modal-backdrop').style.display = 'none';
    document.getElementById('failure-modal').style.display = 'none';
    document.body.style.overflow = 'auto';
}