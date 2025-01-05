
const storageName = 'dotGame-highScore-disappearingDot';
let dotInterval;
function gameStarter() {
    setTimeout(function() {
        $dot.addClass('disappear');
    }, 3200);
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 4500, extra_actions: null},
        },
        interval: 500
    });
}

function resetCircle(_) { return; }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() {
        clearCircle($(this));
    });
    clearInterval(dotInterval);
}
