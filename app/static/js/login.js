function showForm(form) {
    $('.auth-form').css('display', 'none');
    $(`#${form}-form`).css('display', 'flex');
    history.pushState(null, null, `/${form}`);
}