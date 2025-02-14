

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
        // check if current suite is last suite in allSuitesDiv
        if (suite.nextElementSibling === null) {
            suite.querySelector('.suite-test-cases').style.borderBottom = 'none';
        }
        suite.querySelector('.suite-test-cases').style.display = 'flex';
    }
}

function openFailure(failId) {
    const failure = failures[failId];
    console.log(failure);
    document.getElementById('test-name').innerText = failure.name;
    document.getElementById('test-time').innerText = `${failure.time}s`;
    document.getElementById('test-file').innerText = failure.file;
    document.getElementById('test-type').innerText = failure.type;
    document.getElementById('test-message').innerText = failure.message;
    document.getElementById('test-traceback').innerText = failure.traceback;
    document.getElementById('modal-backdrop').style.display = 'block';
    document.getElementById('failure-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeFailure() {
    document.getElementById('modal-backdrop').style.display = 'none';
    document.getElementById('failure-modal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function selectDate(date) {
    document.getElementById('date-select').value = date;
}

function changeDate() {
    const date = document.getElementById('date-select').value;
    // get current date in yyyy-mm-yy format
    const current_date = new Date();
    const year = current_date.getFullYear();
    const month = String(current_date.getMonth() + 1).padStart(2, '0');
    const day = String(current_date.getDate()).padStart(2, '0');
    const current_date_str = `${year}-${month}-${day}`;
    const location = date === current_date_str ? '/' : `/?timestamp=${date}`;
    window.location = location;
}