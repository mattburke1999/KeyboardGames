
const storageName = 'dotGame-highScore-disappearingDot';

let dotInterval;
function gameStarter() {
    setTimeout(function() {
        dotInterval = setInterval(disappearDot, 2500);
    }, 1600);
    startGame(game_action, 4500, null, 500);
}

function disappearDot() {
    $dot.css('backgroundColor', 'transparent');
    console.log('Dot disappeared!');
    setTimeout(function() {
        $dot.css('backgroundColor', 'black');
    }, 600);
}

function resetCircle(_) { return; }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() {
        clearCircle($(this));
    });
    clearInterval(dotInterval);
}
