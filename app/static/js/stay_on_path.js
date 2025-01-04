const storageName = 'dotGame-highScore-stayonpath';

function handleMovement() {
    handleMovementCrossPath();
}

function clearCircles() {
    $('.circle').each(function() {
        clearCircle($(this));
    });
    clearInterval(dotInterval);
}

function clearCircle($circle) { $circle.remove(); }

function resetCircle(_) { return; }

function gameStarter() {
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 4500, extra_actions: null},
        },
        interval: 500
    });
}

function clone_circle() {
}
// available circle positions are anything that lie on the center vertical axis
// or the horizontal axis of the screen
const screenWidth = window.innerWidth;
const screenHeight = window.innerHeight;
const availablePositions = [];
for (let i = 0; i < screenWidth; i++) {
    availablePositions.push({x: i, y: screenHeight / 2 - 25, axis: 'x'});
}
for (let i = 0; i < screenHeight; i++) {
    availablePositions.push({x: screenWidth / 2 - 25, y: i, axis: 'y'});
}

function clone_circle({timeout, extra_actions}) {
    const $circleTemplate = $('#circle-template');
    const $circle = $circleTemplate.clone(true);
    $circle.attr('id', '');
    // apply a random position from the available positions
    const randomPosition = availablePositions[Math.floor(Math.random() * availablePositions.length)];
    // pick a random number between -30 and 30
    const randomShift = Math.floor(Math.random() * 100) - 50;
    console.log(randomShift);
    let left = randomPosition.x;
    let top = randomPosition.y;
    if (randomPosition.axis === 'x') {
        top += randomShift;
    } else {
        left += randomShift;
    }
    $circle.css('left', left);
    $circle.css('top', top);
    // display the circle
    $circle.css('display', 'flex');
    $circle.data('pointAdded', 'false');
    $circle.data('done', 'false');
    $circle.appendTo('body');
    
    document.addEventListener('keydown', function(event) {
        event.stopPropagation();
        if (event.key === ' ' && $circle.data('done') !== 'true') {
            checkDotInsideCircle(event, $circle);
        }
    });

    // Automatically remove the circle
    setTimeout(function () {
        document.removeEventListener('keydown', checkDotInsideCircle);
        if ($circle.data('done') !== 'true') {
            circleDone($circle, false);
        }
    }, timeout);
}