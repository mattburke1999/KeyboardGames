

function toggleSuite(suite) {
    const caret = suite.querySelector('.caret i');
    const caretClass = caret.classList[1];
    allSuites = document.querySelectorAll('.suite');
    allSuites.forEach(suite => {
        suite.querySelector('.caret i').classList.remove('fa-caret-down');
        suite.querySelector('.caret i').classList.add('fa-caret-right');
        suite.querySelector('.suite-test-cases').style.display = 'none';
    });
    if (caretClass === 'fa-caret-right') {
        caret.classList.remove('fa-caret-right');
        caret.classList.add('fa-caret-down');
        suite.querySelector('.suite-test-cases').style.display = 'flex';
    }
}

function toggleTestCase(testCase) {
    const caret = testCase.querySelector('.caret i');
    const caretClass = caret.classList[1];
    let open = false;
    if (caretClass === 'fa-caret-right') {
        caret.classList.remove('fa-caret-right');
        caret.classList.add('fa-caret-down');
        open = true;
    } else {
        caret.classList.remove('fa-caret-down');
        caret.classList.add('fa-caret-right');
    }
    if (open) {
        testCase.querySelector('.failure').style.display = 'flex';
    } else {
        testCase.querySelector('.failure').style.display = 'none';
    }
}