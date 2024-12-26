
const storageName = 'dotGame-highScore-disappearingCircle';

function gameStarter() {
    startGame(game_action, setCircleDisappearingInterval, 8000, 1000);
}

function disappearCircle($circle) {
    if ($circle.data('done') === 'true') {
        return;
    }
    $circle.css('borderColor', 'transparent');
    setTimeout(function() {
        $circle.css('borderColor', 'white');
    }, 500);
}

function setCircleDisappearingInterval($circle) {
    disappearingInterval = setInterval(function() {
        if ($circle.data('done') !== 'true') {
            disappearCircle($circle);
        }
    }, 1500);
    $circle.data('disappearingInterval', disappearingInterval);
}

function resetCircle($circle) {
    clearInterval($circle.data('disappearingInterval'));
}

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() { clearCircle($(this)); });
}
