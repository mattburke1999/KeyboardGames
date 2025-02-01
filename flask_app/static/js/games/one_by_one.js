const storageName = 'dotGame-highScore-oneByOne';
let movementInterval;
function gameStarter() {
    startGame({
        intervalFunction: {
            function: showCircle,
            inputs: {},
            interval: null
        }
    });
}
const defaultMovement = 100;
function showCircle() {
    $circle = clone_circle_base();
    // $circle.css('left', '1000px');
    // $circle.css('top', '1000px');
    movementInterval = setInterval(function() {
        const circleRect = $circle.get(0).getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const windowWidth = window.innerWidth;
        const bottom = window.innerHeight - circleRect.top > 0 ? window.innerHeight - circleRect.top : 0;
        const right = window.innerWidth - circleRect.left > 0 ? window.innerWidth - circleRect.left : 0;
        const maxMovements = {
            'up': defaultMovement > circleRect.top ? circleRect.top : defaultMovement, // 10
            'down': defaultMovement > bottom ? bottom : defaultMovement, // 50
            'right': defaultMovement > circleRect.left ? circleRect.left : defaultMovement, 
            'left': defaultMovement > right ? right : defaultMovement
        }
        // x can move [-right, left]
        const movementX = Math.random() * (maxMovements['left'] + maxMovements['right']) - maxMovements['right'] + 20;
        // y can move [-down, up]
        const movementY = Math.random() * (maxMovements['up'] + maxMovements['down']) - maxMovements['down'] + 20; // -50, 10
        const currentX = circleRect.left;
        const currentY = circleRect.top;
        // debugger;
        $circle.css('left', `${currentX - movementX}px`);
        $circle.css('top', `${currentY - movementY}px`);
    }, 650);

    document.addEventListener('keydown', function(event) {
        event.stopPropagation();
        if (event.key === ' ' && $circle.data('done') !== 'true') {
            checkDotInsideCircle(event, $circle);
        }
    });
}

function resetCircle(_) { 
    clearInterval(movementInterval); 
}

function clearCircle($circle) { 
    $circle.remove();
    showCircle();
}

function clearCircles() {
    $('.circle').each(function() { $(this).remove(); });
}
