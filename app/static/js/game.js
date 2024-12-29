const pressedKeys = {};
let animationFrame;
const dbVersion = 1;
const $dot = $('#dot');
const dotWidth = parseInt($dot.outerWidth());
const dotHeight = parseInt($dot.outerHeight());
let circleInterval;
let socket;
let loggedIn = false;
let enteredGameRoom = false;

connectSocket();

function fetchUserId() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/current_user',
            type: 'GET',
            contentType: 'application/json',
            success: function(response) {
                resolve(response);
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}

// Usage with async/await
async function getUserId() {
    let userId = localStorage.getItem('keyboard-games-userId');
    if (!loggedIn || !userId) {
        try {
            let response = await fetchUserId();
            console.log(response);
            localStorage.setItem('keyboard-games-userId', response.user_id);
            loggedIn = response.logged_in;
            return {logged_in: response.logged_in, userId: response.user_id};
        } catch (error) {
            console.error(error);
            return false, null;
        }
    }
    return {logged_in: true, userId};
}


async function connectSocket() {
    let { logged_in, userId } = await getUserId();
    loggedIn = logged_in;
    console.log(loggedIn, userId);
    if (!loggedIn) {
        // notify user that they are not logged in
        // if they want their scores to be saved, they need to log in
        enteredGameRoom = false;
        console.log("User not logged in");
        return;
    }
    localStorage.setItem('userId', userId);
    console.log("Creating socket");
    socket = io({transports: ['websocket']});
    //emit 'enter_game_room' event and receieve response from same event
    socket.emit('enter_game_room', {userId, gameId}, (response) => {
        if (response.success) {
            console.log(response.message);
            enteredGameRoom = true;
            endGameSocketListener(socket);
        } else {
            console.error(response.message);
            enteredGameRoom = false;
            // Notify user that there was an error conneting to server, reload page to try again
            // otherwise results will not be saved
        }
    });
}


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
            clearInterval(timer);
            if (!enteredGameRoom) {
                console.log('Finshing game on client side');
                finishGame();
            } else {
                // socket listener handles finishing the game
                console.log('Finishing game on server side');
                // add a 3 second timer, if the server does not finish the game, finish it manually on client side
                return;
            }
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
    const highScoreList = $('#high-score-offline ol');
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

async function addPointToServer() {
    let { logged_in, userId } = await getUserId();
    if (!logged_in) {
        enteredGameRoom = false;
        loggedIn = false;
        return;
    }
    console.log('Adding point to server');
    
    socket.emit('point_added', { user_id: userId, game_id: gameId }, (response) => {
        console.log(response);

        // Open IndexedDB and add the point
        const dbRequest = indexedDB.open('KeyboardGamesDB', dbVersion);

        dbRequest.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction('points', 'readwrite');
            const store = transaction.objectStore('points');

            // Add the new point to IndexedDB
            const point = {
                point_token: response.point_token,
                point_time: new Date().toISOString(),
            };
            const addRequest = store.put(point);

            addRequest.onsuccess = () => {
                console.log('Point successfully added to IndexedDB:', point);
            };

            addRequest.onerror = (error) => {
                console.error('Failed to add point to IndexedDB:', error);
            };
        };

        dbRequest.onerror = (event) => {
            console.error('Failed to open IndexedDB:', event.target.error);
        };
    });
}

function dotEnteredCircle($circle) {
    console.log('Dot entered this circle!');
    if ($circle.data('pointAdded') === 'true') {
        return;
    }
    $circle.data('pointAdded', 'true');
    if (enteredGameRoom) {
        addPointToServer();
    }
    let currentScore = parseInt($('#score').text());
    $('#score').text(currentScore + 1);
    $('#final-score').text(currentScore + 1);
    // Perform a specific action for this circle
    circleDone($circle, true);
}

function resetPointListInDB() {
    const dbRequest = indexedDB.open('KeyboardGamesDB', dbVersion);

    dbRequest.onupgradeneeded = (event) => {
        const db = event.target.result;
    
        // Check if the object store exists
        if (!db.objectStoreNames.contains('points')) {
            db.createObjectStore('points', { keyPath: 'point_token' });
            console.log('Created "points" object store in IndexedDB.');
        }
    };

    dbRequest.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction('points', 'readwrite');
        const store = transaction.objectStore('points');

        // Clear the existing point list
        const clearRequest = store.clear();
        clearRequest.onsuccess = () => {
            console.log('Point list reset in IndexedDB.');
        };
        clearRequest.onerror = () => {
            console.error('Failed to reset point list in IndexedDB.');
        };
    };

    dbRequest.onerror = (event) => {
        console.error('Failed to open IndexedDB:', event.target.error);
    };
}

async function startGameServer(userId) {
    socket.emit('start_game', {user_id: userId, game_id: gameId}, (response) => {
        if (!response.success) {
            enteredGameRoom = false;
            console.error(response.message);
            // Notify user that there was an error starting the game
        } else {
            console.log(response.message);
            $('#start_game_token').val(response.start_game_token);
            // create a new list for point tokens to be added to
            resetPointListInDB();
        }
    });
}

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
            if (enteredGameRoom) {
                userId = localStorage.getItem('userId');
                startGameServer(userId);
            }
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

function endGameSocketListener(socket) {
    console.log('setting socket listener for end_game');
    socket.on('end_game', (response) => {
        console.log(response);
        finishGameFromSocket(response.end_game_token);
    });
}

function finishGameFromSocket(end_game_token) {
    clearInterval(circleInterval);
    $('#dot').css('display', 'none');
    clearCircles();
    $('#timer').css('display', 'none');
    // TODO: add a loading screen here later
    setHighScoreServer(end_game_token);
}

async function getFinalPointListFromDB() {
    return new Promise((resolve, reject) => {
        const dbRequest = indexedDB.open('KeyboardGamesDB', dbVersion);

        dbRequest.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction('points', 'readonly');
            const store = transaction.objectStore('points');

            const getAllRequest = store.getAll();

            getAllRequest.onsuccess = () => {
                resolve(getAllRequest.result); // Returns the list of points
            };

            getAllRequest.onerror = (error) => {
                reject(error); // Handles any errors during retrieval
            };
        };

        dbRequest.onerror = (event) => {
            reject(event.target.error); // Handles errors opening the database
        };
    });
}

async function setHighScoreServer(end_game_token) {
    const score = parseInt($('#score').text());
    const start_game_token = $('#start_game_token').val();
    const pointList = await getFinalPointListFromDB();
    console.log(pointList);
    $.ajax({
        url: `/game/${gameId}/score_update`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({start_game_token, end_game_token, score, pointList}),
        success: function(response) {
            console.log(response);
            const highScoreListTop10 = $('#top10');
            response.top10.forEach(function(item) {
                let styling = item.current_score ? 'style="color: white; font-weight: bold;"' : '';
                highScoreListTop10.append(`<li ${styling}>${item.username} - ${item.score} (${item.date})</li>`);
            });
            const highScoreListTop3 = $('#top3');
            response.top3.forEach(function(item) {
                let styling = item.current_score ? 'style="color: white; font-weight: bold;"' : '';
                highScoreListTop3.append(`<li ${styling}>${item.score} (${item.date})</li>`);
            });
            $('#high-score-online').css('display', 'flex');
            $('#game-over').css('display', 'flex');
            $('#restart').on('click', function() {
                window.location.reload();
            });
        },
        error: function(error) {
            console.log(error);
            // add some error message to the user
        }
    });
}

function finishGame() {
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
    $circle.attr('id', '');
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

