const storageName = 'dotGame-highScore-movingCircles';

function gameStarter() {
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 8000, extra_actions: moveCircle},
        },
        interval: 1500
    });
}

function animationFunc ($circle, xMovement, yMovement) {
    if ($circle.data('done') === 'true') {
        return;
    }
        let circleRect = $circle.get(0).getBoundingClientRect();
        let currentX = circleRect.left;
        let currentY = circleRect.top;
        let newX = currentX + xMovement;
        let newY = currentY + yMovement - 20;
        if (newX < 0) {
            newX = window.innerWidth;
        }
        if (newX > window.innerWidth) {
            newX = 0;
        }
        if (newY < 0) {
            newY = window.innerHeight;
        }
        if (newY > window.innerHeight) {
            newY = 0;
        }
        $circle.css('left', `${newX}px`);
        $circle.css('top', `${newY}px`);
        window.requestAnimationFrame(function () {
            animationFunc($circle, xMovement, yMovement);
        });
}
function moveCircle($circle) {
    let radians = Math.random() * 2 * Math.PI;
    let speed = 2.75; 

    // Calculate movement per frame
    let xMovement = Math.cos(radians) * speed;
    let yMovement = Math.sin(radians) * speed;

    // Start animation
    let animationFrame = window.requestAnimationFrame(() => {
        animationFunc($circle, xMovement, yMovement);
    });
    $circle.data('animationFrame', animationFrame);
    //log all cirlce data
}
function getCurrentCirclePosition($circle) {
    let circleRect = $circle.get(0).getBoundingClientRect();
    return {
        x: circleRect.left,
        y: circleRect.top
    };
}

function resetCircle($circle) { window.cancelAnimationFrame($circle.data('animationFrame')); }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() { clearCircle($(this)); });
}