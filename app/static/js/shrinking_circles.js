
const storageName = 'dotGame-highScore-shrinkingCircle';

function gameStarter() {
    startGame(copyCircle, 1000);
}

function copyCircle() {
    const $circleTemplate = $('#circle-template');
    const $circle = $circleTemplate.clone(true);
    // apply a random position on the screen
    $circle.css('left', Math.floor(Math.random() * window.innerWidth) + 'px');
    $circle.css('top', Math.floor(Math.random() * window.innerHeight) + 'px');
    // display the circle
    $circle.css('display', 'flex');
    $circle.data('pointAdded', 'false');
    $circle.data('done', 'false');
    $circle.appendTo('body');
    // Add event listener to the circle

    // Listen for the dot's movement
    
    document.addEventListener('keydown', function(event) {
        event.stopPropagation();
        if (event.key === ' ' && $circle.data('done') !== 'true') {
            checkDotInsideCircle(event, $circle);
        }
    });
    setTimeout(function() {
        $circle.addClass('shrink');
    }, 1000);

    // Automatically remove the circle after 10 seconds
    setTimeout(function () {
        document.removeEventListener('keydown', checkDotInsideCircle);
        if ($circle.data('done') !== 'true') {
            circleDone($circle, false);
        }
    }, 7000);
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
