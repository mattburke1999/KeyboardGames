
const storageName = 'dotGame-highScore-shrinkingCircle';

function gameStarter() {
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 7000, extra_actions: shrinkCircle},
            interval: 1000
        }
    });
}

function shrinkCircle($circle) {
    setTimeout(function() {
        $circle.addClass('shrink');
    }, 1000);
}

function getCurrentTransformScale($circle) {
    const style = window.getComputedStyle($circle[0]);
    const matrix = new WebKitCSSMatrix(style.transform);
    return matrix.a;
}

function resetCircle($circle, hit) {
    if(!hit) {
        $circle.css('transform', 'scale(1)');
    } else {
        let currentScale = getCurrentTransformScale($circle);
        $circle.css('transform', `scale(${currentScale})`);
    }
}
function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() { clearCircle($(this)); });
}
