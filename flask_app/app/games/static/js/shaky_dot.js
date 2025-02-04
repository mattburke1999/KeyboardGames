
const storageName = 'dotGame-highScore-shakyDot';

function gameStarter() {
    startGame({
        intervalFunction: {
            function: clone_circle,
            inputs: {timeout: 4500, extra_actions: null},
            interval: 500
        }
    });
}
shakeDot();
const baseMove = 75;
const dotShake = {
    left_minus: -1*baseMove,
    left_plus: baseMove,
    top_minus: -1*baseMove,
    top_plus: baseMove
}
const dotShakes = ['left_minus', 'left_plus', 'top_minus', 'top_plus'];

function shakeDot(){
    setInterval(function(){
        const randomShake = dotShakes[Math.floor(Math.random() * dotShakes.length)];
        const shake = dotShake[randomShake];
        const dotPos = {
            left: parseInt($dot.css('left')),
            top: parseInt($dot.css('top'))
        }
        const dir = randomShake.replace('_minus', '').replace('_plus', '');
        const newPos = dotPos[dir] + shake;
        $dot.css(dir, `${newPos}px`);
    }, 650);
}

function resetCircle(_) { return; }

function clearCircle($circle) { $circle.remove(); }

function clearCircles() {
    $('.circle').each(function() { clearCircle($(this)); });
}
