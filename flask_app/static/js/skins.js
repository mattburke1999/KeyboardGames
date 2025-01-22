function add_event_listeners() {
    $('#user-skin-btn').on('click', function() {
        showUserSkins(this, 'user');
    });
}

function showUserSkins(btn, filter) {
    console.log('showUserSkins');
    console.log(`filter: ${filter}`);
    if (filter == 'user') {
        $('.skin').each(function() {
            if (!$(this).hasClass('user-skin')) {
                $(this).hide();
            }
        });
        $(btn).text('Show All Skins');
        $(btn).off('click');
        $(btn).on('click', function() {
            showUserSkins(this, 'all');
        });
    } else {
        $('.skin').each(function() {
            $(this).show();
        });
        $(btn).text('View My Skins');
        $(btn).off('click');
        $(btn).on('click', function() {
            showUserSkins(this, 'user');
        });
    }
}
