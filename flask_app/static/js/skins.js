function logout() {
    window.location.href = '/logout';
}

function filterSkins(filter) {
    if (filter === 'all') {
        $('#all-skins-btn').hide();
        $('.filter-skin-btns').show();
        $('.skin').show();
    } else {
        $('#all-skins-btn').show();
        $('.filter-skin-btns').hide();
        if (filter === 'user') {
            $('.skin').each(function() {
                if (!$(this).hasClass('user-skin')) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        } else if (filter === 'purchaseable') {
            $('.skin').each(function() {
                if ($(this).hasClass('not-available') || $(this).hasClass('user-skin')) {
                    $(this).hide();
                } else {
                    $(this).show();
                }
            });
        }
    }
}

function showSkinModal(skin_id, modal_id, closeFunction, page) {
    const skin = skins.filter(skin => skin.id == skin_id)[0];
    $.ajax({
        url: '/skins/get_skin',
        type: 'POST',
        data: JSON.stringify({skin, page}),
        contentType: 'application/json',
        success: function(response) {
            $('#modal-backdrop').off('click');
            $('#modal-backdrop').on('click', () => closeFunction());
            $(`#${modal_id} .skin`).replaceWith(response.html);
            $(`#skin-id-${page}`).val(skin_id);
            $(`#${modal_id}`).css('display', 'flex');
            $('#modal-backdrop').css('display', 'flex');
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth' // Optional for smooth scrolling
            });              
            document.body.overflow = 'hidden';
        }, 
        error: function(response) {
            console.log(response);
            handleError(response);
        }
    });
}

function countSkins() {
    // count skins where with class 'user-skin' and number without class 'not-available'
    const userSkins = $('.skin.user-skin').length;
    $('#user-skin-count').text(`(${userSkins})`);
    $('#user-skin-count').show();
    const userPoints = parseInt($('#user-points').text());
    const purchaseableSkins = skins.filter(skin => !skin.user_skin && skin.points <= userPoints).length;    
    $('#purchaseable-skin-count').text(`(${purchaseableSkins})`);
    $('#purchaseable-skin-count').show();
}

function showPurchaseSkinModal(skin_id) {
    showSkinModal(skin_id, 'purchase-skin-modal', closePurchaseSkinModal, 'purchase');
}

function showSelectSkinModal(skin_id) {
    showSkinModal(skin_id, 'select-skin-modal', closeSelectSkinModal, 'select');
}

function closePurchaseSkinModal() {
    $('#purchase-skin-modal').css('display', 'none');
    $('#purchase-skin-modal .skin').empty();
    $('#modal-backdrop').css('display', 'none');
    $('#modal-backdrop').off('click');
    document.body.overflow = 'auto';
}

function closeSelectSkinModal() {
    $('#select-skin-modal').css('display', 'none');
    $('#select-skin-modal .skin').empty();
    $('#modal-backdrop').css('display', 'none');
    $('#modal-backdrop').off('click');
    document.body.overflow = 'auto';
}

function selectSkin(){
    const skin_id = $('#skin-id-select').val();
    $.ajax({
        url: '/skins/select',
        type: 'POST',
        data: JSON.stringify({skin_id}),
        contentType: 'application/json',
        success: function(response) {
            closeSelectSkinModal();
            location.reload();
        }, 
        error: function(response) {
            console.log(response);
            handleError(response);
        }
    });
}

function purchaseSkin(){
    const skin_id = $('#skin-id-purchase').val();
    $.ajax({
        url: '/skins/purchase',
        type: 'POST',
        data: JSON.stringify({skin_id}),
        contentType: 'application/json',
        success: function(response) {
            closePurchaseSkinModal();
            location.reload();
        }, 
        error: function(response) {
            console.log(response);
            handleError(response);
        }
    });
}