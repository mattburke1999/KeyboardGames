
const storageName = 'dotGame-highScore-firstCircle';

function gameStarter() {
    startGame(game_action, 4500, null, 500);
}

function resetCircle(_) { return; }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() { clearCircle($(this)); });
}
