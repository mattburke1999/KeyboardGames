

function toggleSuite(suite) {
    const caret = suite.querySelector('.caret i');
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
        suite.querySelector('.suite-test-cases').style.display = 'flex';
    } else {
        suite.querySelector('.suite-test-cases').style.display = 'none';
    }
}