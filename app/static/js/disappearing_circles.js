
const storageName = 'dotGame-highScore-disappearingCircle';

function gameStarter() {
    startGame(game_action, 8000, setCircleDisappearingInterval, 1000);
}


function setCircleDisappearingInterval($circle) {
    $circle.addClass('disappear');
}

function resetCircle($circle) { //clearInterval($circle.data('disappearingInterval')); 
    $circle.removeClass('disappear');
}

function clearCircle($circle) { $circle.remove(); }

function clearCircles() { $('.circle').each(function() { clearCircle($(this)); }); }
