function logout() {
    $.ajax({
        url: '/logout',
        type: 'POST',
        success: function(response) {
            console.log(response);
            window.location.reload();
        },
        error: function(err) {
            console.log(err);
        }
    });
}