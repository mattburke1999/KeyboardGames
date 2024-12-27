const pressedKeys = {};
let animationFrame;
const GAME_DURATION = 60; // seconds

const $dot = $('#dot');
const dotWidth = parseInt($dot.outerWidth());
const dotHeight = parseInt($dot.outerHeight());
let circleInterval;

function handleMovement() {
    let currentOffsetTop = parseInt($dot.css('top'));
    let currentOffsetLeft = parseInt($dot.css('left'));
    if (pressedKeys['ArrowUp']) {
        if (currentOffsetTop > dotHeight) {
            $dot.css('top', currentOffsetTop - 10 + 'px');
        }
    }
    if (pressedKeys['ArrowDown']) {
        if (currentOffsetTop < window.innerHeight - dotHeight) {
            $dot.css('top', currentOffsetTop + 10 + 'px');
        }
    }
    if (pressedKeys['ArrowLeft']) {
        if (currentOffsetLeft > dotWidth) {
            $dot.css('left', currentOffsetLeft - 10 + 'px');
        }
    }
    if (pressedKeys['ArrowRight']) {
        if (currentOffsetLeft < window.innerWidth - dotWidth) {
            $dot.css('left', currentOffsetLeft + 10 + 'px');
        }
    }
    animationFrame = requestAnimationFrame(handleMovement);
}

document.addEventListener('keydown', (event) => {
    if (!pressedKeys[event.key]) {
        pressedKeys[event.key] = true;
    }

    // Start movement loop if not already running
    if (!animationFrame) {
        handleMovement();
    }
});

document.addEventListener('keyup', (event) => {
    pressedKeys[event.key] = false;

    // If no keys are pressed, stop the animation frame
    if (!Object.values(pressedKeys).some((value) => value)) {
        cancelAnimationFrame(animationFrame);
        animationFrame = null;
    }
});

function startTimer() {
    let timeLeft = GAME_DURATION;
    $('#time').text(timeLeft);
    const timer = setInterval(function() {
        timeLeft--;
        $('#time').text(timeLeft);
        if (timeLeft === 0) {
            finishGame(timer);
            clearInterval(timer);
        }
    }, 1000);
}

function setHighScore(score) {
    let highScores = JSON.parse(localStorage.getItem(storageName));
    const currentDate = new Date();
    const dateStr = currentDate.getMonth() + 1 + '/' + currentDate.getDate() + '/' + currentDate.getFullYear();
    let currentScore = {dateStr, score};
    if (!highScores){
        highScores = [currentScore];
        localStorage.setItem(storageName, JSON.stringify(highScores));
    } else {
        console.log(highScores);
        if ((highScores.length === 5 && highScores[4].score < score) || highScores.length < 5) {
            highScores.push(currentScore);
            highScores.sort((a, b) => b.score - a.score);
            highScores = highScores.slice(0, 5);
            console.log(highScores);
            localStorage.setItem(storageName, JSON.stringify(highScores));
        }
    }
    const highScoreList = $('#high-score ol');
    let currentAdded = false;
    highScores.forEach(function(item) {
        let styling = '';
        if (item.score === score && item.dateStr === dateStr && !currentAdded) {
            styling = 'style="color: white; font-weight: bold;"';
            currentAdded = true;
        }
        highScoreList.append(`<li ${styling}>${item.score} (${item.dateStr})</li>`);
    });
}

function dotEnteredCircle($circle) {
    console.log('Dot entered this circle!');
    if ($circle.data('pointAdded') === 'true') {
        return;
    }
    $circle.data('pointAdded', 'true');
    let currentScore = parseInt($('#score').text());
    $('#score').text(currentScore + 1);
    $('#final-score').text(currentScore + 1);
    // Perform a specific action for this circle
    circleDone($circle, true);
}
//intervalFunc, intervalFuncInterval, intervalFuncActions, interval
// startGame({
//     intervalFunction: {
//         function: game_action,
//         inputs: {interval: 4500, actions: null},
//     },
//     interval: 500
// });
function startGame({intervalFunction, interval}) {
    console.log('Starting game!');
    let countDown = 3;
    $('#instructions').css('display', 'none');
    $('#starting').css('display', 'flex');
    const countdownInterval = setInterval(function() {
        if (countDown > 0) {
            $(`#startCount`).css('color', '#2e2e2e');
            $(`#startCount`).text(countDown);
            countDown--;
        } else {
            clearInterval(countdownInterval);
            $('#starting').css('display', 'none');
            $('#score-card').css('display', 'flex');
            intervalFunction.function(intervalFunction.inputs);
            circleInterval = setInterval(function() {
                intervalFunction.function(intervalFunction.inputs);
            }, interval);
            startTimer();
        }
    }, 1000);
}

function checkDotInsideCircle(event, $circle) {
    event.stopPropagation();
    const circleRect = $circle.get(0).getBoundingClientRect();
    const radius = circleRect.width / 2;
    const centerX = circleRect.left + radius;
    const centerY = circleRect.top + radius;

    const dotRect = $dot.get(0).getBoundingClientRect();
    const dotCenterX = dotRect.left + dotRect.width / 2;
    const dotCenterY = dotRect.top + dotRect.height / 2;

    const distance = Math.sqrt(
        Math.pow(dotCenterX - centerX, 2) +
        Math.pow(dotCenterY - centerY, 2)
    );

    if (distance <= radius) {
        dotEnteredCircle($circle);
    }
}

function finishGame(timer) {
    clearInterval(timer);
    clearInterval(circleInterval);
    $('#dot').css('display', 'none');
    clearCircles();
    $('#timer').css('display', 'none');
    setHighScore(parseInt($('#score').text()));
    $('#game-over').css('display', 'flex');
    $('#restart').on('click', function() {
        window.location.reload();
    });
}

function circleDone($circle, hit) {
    if ($circle.data('done') === 'true') {
        return;
    }
    $circle.data('done', 'true');
    const color = hit ? 'green' : 'red';
    const text = hit ? 'HIT!' : 'MISS!';
    resetCircle($circle, hit);
    $circle.css('borderColor', color); 
    $circle.css('color', color);
    $circle.css('backgroundColor', 'white');
    $circle.text(text);
    if (!hit) { $circle.css('fontSize', '1.1rem'); }
    setTimeout(function() {
        clearCircle($circle);
    }, 500);
}

function clone_circle({timeout, extra_actions}) {
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

    if (extra_actions) {
        extra_actions($circle);
    }
    
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