function showForm(form) {
    clearForm();
    $('.auth-form').css('display', 'none');
    $(`#${form}-form`).css('display', 'flex');
    history.pushState(null, null, `/${form}`);
    if (form === 'register') {
        addOnChangeEventListeners();
    }
}

function clearForm() {
    $('input').val('');
    $('.invalid-input').css('display', 'none');
}

function addOnChangeEventListeners() {
    // check if #username has onchange event listener
    // console.log('adding event listeners');
    if ($('#register-form').data('onchange-listeners') !== 'true') {
        console.log('adding event listeners');
        $('#username').on('change', function() {
            checkUniqueUsername($('#username').val());
        });
        $('#email').on('change', function() {
            checkUniqueEmail($('#email').val());
        });
        $('#confirm-password').on('change', function() {
            checkConfirmPassword('confirm-password');
        });
        $('#password').on('change', function() {
            checkConfirmPassword('password');
        });
    } else {
        console.log('not adding event listeners');
    }
    $('#register-form').data('onchange-listeners', 'true');
}

function checkUniqueUsername(username) {
    $.ajax({
        url: '/unique_username',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({username}),
        success: function(response) {
            console.log(response);
            if (response.unique) {
                $('#username-unique').css('display', 'none');
                $('#username').css('border-color', '#b4b4b4');
            } else {
                $('#username-unique').css('display', 'block');
                $('#username').css('border-color', 'red');
            }
        },
        error: function(err) {
            console.log(err);
        }
    });
}

function checkUniqueEmail(email) {
    $.ajax({
        url: '/unique_email',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({email}),
        success: function(response) {
            console.log(response);
            if (response.unique) {
                $('#email-unique').css('display', 'none');
                $('#email').css('border-color', '#b4b4b4');
            } else {
                $('#email-unique').css('display', 'block');
                $('#email').css('border-color', 'red');
            }
        },
        error: function(err) {
            console.log(err);
        }
    });
}

function checkConfirmPassword(type){
    const password = $('#password').val();
    const confirmPassword = $('#confirm-password').val();
    if (type === 'password' && confirmPassword === '') {
        return;
    }
    if (password !== confirmPassword) {
        $('#password-mismatch').css('display', 'block');
        $('#confirm-password').css('border-color', 'red');
    } else {
        $('#password-mismatch').css('display', 'none');
        $('#confirm-password').css('border-color', '#b4b4b4');
    }
}

function getFormData(form) {
    const inputs = $(`#${form}-form form input[name]`);
    const formData = {};
    inputs.each(function() {
        formData[$(this).attr('name')] = $(this).val();
    });
    return formData;
}

function register(event) {
    event.preventDefault();
    const formData = getFormData('register');
    $.ajax({
        url: '/register',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({formData}),
        success: function(response) {
            console.log(response);
            if (response.registered) {
                window.location.href = '/';
            }
        },
        error: function(err) {
            console.log(err);
        }
    });
}

function login(event) {
    event.preventDefault();
    const formData = getFormData('login');
    $.ajax({
        url: '/login',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({formData}),
        success: function(response) {
            console.log(response);
            if (response.logged_in) {
                window.location.href = '/';
            }
        },
        error: function(err) {
            console.log(err);
        }
    });
}