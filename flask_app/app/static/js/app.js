function logout() {
    window.location.href = '/auth/logout';
}

function handleError(response) {
    if (!response.logged_in) {
        alert(response.message);
        window.location.href = '/';
    }
}
function get_profile() {
    if($('#profile-username').text() === '') {
        $.ajax({
            url: '/auth/profile',
            type: 'GET',
            success: function(response) {
                console.log(response);
                populate_profile_modal(response);
            }, 
            error: function(response) {
                console.log(response);
                handleError(response);
            }
        });
    } else {
        show_profile_modal();
    }
}
function close_profile_modal() {
    $('#profile-modal').css('display', 'none');
    $('#modal-backdrop').css('display', 'none');
    document.body.style.overflow = 'auto';
    $('#modal-backdrop').off('click');
}

function show_profile_modal() {
    $('#profile-modal').css('display', 'flex');
    $('#modal-backdrop').css('display', 'block');
    document.body.style.overflow = 'hidden';
    // clear any click events
    $('#modal-backdrop').off('click');
    $('#modal-backdrop').click(close_profile_modal);
}

function populate_profile_modal(user) {
    console.log(user);
    $('#profile-username').text(user.username);
    $('#profile-created').text(user.created_time);
    $('#profile-top10').text(user.num_top10);
    $('#profile-points').text(user.points);
    const top3Div = $('#profile-top3');
    top3Div.empty();
    user.ranks.forEach(item => {
        const rank = item.rank === 1 ? '1st' : item.rank === 2 ? '2nd' : '3rd' + ' Place';
        const rankCSS = item.rank === 1 ? 'first' : item.rank === 2 ? 'second' : 'third';
        top3Div.append(`<h3><span class='rank-${rankCSS}'>${rank}: </span>${item.score} - ${item.game_name}</h3>`);
    });
    show_profile_modal();
}