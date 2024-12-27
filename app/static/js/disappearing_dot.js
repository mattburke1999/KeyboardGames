
const storageName = 'dotGame-highScore-disappearingDot';

let dotInterval;
function gameStarter() {
    setTimeout(function() {
        $dot.addClass('disappear');
    }, 3200);
    startGame(game_action, 4500, null, 500);
}

function resetCircle(_) { return; }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() {
        clearCircle($(this));
    });
    clearInterval(dotInterval);
}
