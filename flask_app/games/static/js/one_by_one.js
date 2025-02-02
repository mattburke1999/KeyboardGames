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
    movementInterval = setInterval(function() {
        const circleRect = $circle.get(0).getBoundingClientRect();
        const bottom = window.innerHeight - circleRect.top > 0 ? window.innerHeight - circleRect.top : 0;
        const right = window.innerWidth - circleRect.left > 0 ? window.innerWidth - circleRect.left : 0;
        const maxMovements = {
            'up': defaultMovement > circleRect.top ? circleRect.top : defaultMovement, // 10
            'down': defaultMovement > bottom ? bottom : defaultMovement, // 50
            'right': defaultMovement > circleRect.left ? circleRect.left : defaultMovement, 
            'left': defaultMovement > right ? right : defaultMovement
        }
        // x can move [-right, left]
        const movementX = Math.random() * (maxMovements['left'] + maxMovements['right']) - maxMovements['right'];
        // y can move [-down, up]
        const movementY = Math.random() * (maxMovements['up'] + maxMovements['down']) - maxMovements['down']; // -50, 10
        const currentX = circleRect.left;
        let newX = currentX - movementX;
        if (newX < 10) {
            newX = 10;
        } else if (newX > window.innerWidth - 10) {
            newX = window.innerWidth - 10;
        }
        const currentY = circleRect.top;
        let newY = currentY - movementY;
        if (newY < 10) {
            newY = 10;
        } else if (newY > window.innerHeight - 10) {
            newY = window.innerHeight - 10;
        }
        $circle.css('left', `${newX}px`);
        $circle.css('top', `${newY - 20}px`);
    }, 750);

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
