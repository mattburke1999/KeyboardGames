
const storageName = 'dotGame-highScore-shrinkingCircle';

function gameStarter() {
    startGame(copyCircle, shrinkCircle, 7000, 1000);
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
