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

function showPurchaseSkinModal(skin_id) {
    const skin = skins.filter(skin => skin.id == skin_id)[0];
    $.ajax({
        url: '/skins/get_skin',
        type: 'POST',
        data: JSON.stringify({skin: skin, page: 'purchase'}),
        contentType: 'application/json',
        success: function(response) {
            $('#modal-backdrop').off('click');
            $('#modal-backdrop').on('click', closePurchaseSkinModal);
            $('#purchase-skin-modal .skin').replaceWith(response);
            $('#purchase-skin-modal').css('display', 'flex');
            $('#modal-backdrop').css('display', 'flex');
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth' // Optional for smooth scrolling
            });              
            document.body.overflow = 'hidden';
        }
    });
}

function closePurchaseSkinModal() {
    $('#purchase-skin-modal').css('display', 'none');
    $('#purchase-skin-modal .skin').empty();
    $('#modal-backdrop').css('display', 'none');
    $('#modal-backdrop').off('click');
    document.body.overflow = 'auto';
}