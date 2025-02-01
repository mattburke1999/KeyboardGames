
const storageName = 'dotGame-highScore-disappearingCircle';

function gameStarter() {
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 8000, extra_actions: setCircleDisappearingInterval},
            interval: 1000
        }
    });
}


function setCircleDisappearingInterval($circle) {
    $circle.addClass('disappear');
}

function resetCircle($circle) { //clearInterval($circle.data('disappearingInterval')); 
    $circle.removeClass('disappear');
}

function clearCircle($circle) { $circle.remove(); }

function clearCircles() { $('.circle').each(function() { clearCircle($(this)); }); }
