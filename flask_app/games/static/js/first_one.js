
const storageName = 'dotGame-highScore-firstCircle';

function gameStarter() {
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 4500, extra_actions: null},
            interval: 500
        }
    });
}

function resetCircle(_) { return; }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() { clearCircle($(this)); });
}
