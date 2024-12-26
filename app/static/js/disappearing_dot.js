
const storageName = 'dotGame-highScore-disappearingDot';

let dotInterval;
function gameStarter() {
    setTimeout(function() {
        dotInterval = setInterval(disappearDot, 2500);
    }, 1600);
    startGame(copyCircle, 500);
}

function disappearDot() {
    $dot.css('backgroundColor', 'transparent');
    console.log('Dot disappeared!');
    setTimeout(function() {
        $dot.css('backgroundColor', 'black');
    }, 600);
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

    // Automatically remove the circle after 10 seconds
    setTimeout(function () {
        document.removeEventListener('keydown', checkDotInsideCircle);
        if ($circle.data('done') !== 'true') {
            circleDone($circle, false);
        }
    }, 4500);
}

function circleDone($circle, hit) {
    if ($circle.data('done') === 'true') {
        return;
    }
    $circle.data('done', 'true');
    const color = hit ? 'green' : 'red';
    const text = hit ? 'HIT!' : 'MISS!';
    $circle.css('borderColor', color); 
    $circle.css('color', color);
    $circle.css('backgroundColor', 'white');
    $circle.text(text);
    if (!hit) { $circle.css('fontSize', '1.1rem'); }
    setTimeout(function() {
        $circle.remove();
    }, 500);
}



function clearCircles() {
    $('.circle').each(function() {
        if ($(this).id !== 'circle-template') {
            $(this).remove();
        }
    });
    clearInterval(dotInterval);
}
