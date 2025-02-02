const pressedKeys = {};
let animationFrame;
const dbVersion = 1;
const $dot = $('#dot');
const dotWidth = parseInt($dot.outerWidth());
const dotHeight = parseInt($dot.outerHeight());
const pathTolerance = 10;
const centerX = Math.round(window.innerWidth / 2);
const centerXRange = [centerX - pathTolerance, centerX + pathTolerance];
const centerY = Math.round(window.innerHeight / 2);
const centerYRange = [centerY - pathTolerance, centerY + pathTolerance];
let circleInterval;
let game_socket;
let app_socket;
let loggedIn = false;
let enteredGameRoom = false;
let loadingInterval;
const game_socketServer = `ws://${IP}:3030/ws`;

connectSocket();

function fetchNewSession() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/create_session',
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
async function getNewSession() {
    try {
        let response = await fetchNewSession();
        console.log(response);
        loggedIn = response.logged_in;
        return {logged_in: response.logged_in, session_jwt: response.session_jwt};
    } catch (error) {
        console.error(error);
        return {logged_in: false, session_jwt: null};
    }
}

async function connectSocket() {
    $('#start-game-btn').css('display', 'none');
    let { logged_in, session_jwt } = await getNewSession();
    loggedIn = logged_in;
    user = session_jwt ? 1 : 0;
    console.log(loggedIn, user);
    if (!loggedIn) {
        // notify user that they are not logged in
        // if they want their scores to be saved, they need to log in
        enteredGameRoom = false;
        console.log("User not logged in");
        $('#start-game-btn').css('display', 'block');
        return;
    }
    console.log("Creating sockets");
    game_socket = new WebSocket(game_socketServer);
    game_socket.onopen = () => {
        console.log('Connected to WebSocket server.');
        //emit 'enter_game_room' event and receieve response from same event
        const message = JSON.stringify({
            event: 'enter_game_room', // Define the action
            data: { session_jwt, gameId },  // Your payload
        });
        game_socket.send(message);
        // set up event listners
        game_socket.onmessage = (event) => {
            const response = JSON.parse(event.data);
            console.log(response);
            switch (response.event) {
                case 'entered_game_room_response':
                    entered_game_room_response_Socketlistener(response);
                    break;
                case 'end_game':
                    endGameSocketListener(response);
                    break;
                case 'point_added_response':
                    point_added_response_Socketlistener(response);
                    break;
                case 'start_game_response':
                    start_game_response_Socketlistener(response);
                    break;
                case 'game_data_stored':
                    storedGameDataSocketListener(response);
                    break;
            }
        };
    }
}
function app_socket_on_disconnect() {
    //notify user that they were disconnected from the server
    //disconnect from game sockets
    alert('You have been disconnected from the server. Please reload the page to try again.');
}

function start_app_socket() {
    app_socket = io({transports: ['websocket']});
    app_socket.emit('join_session', (response) => {
        console.log(`app_socket join_session response:`);
        console.log(response);
        if (response.success && response.joined_room){
            $('#start-game-btn').css('display', 'block');
        } else {
            // window.location.reload();

            // Notify user and provide next steps
            alert('Error connecting to the app server. Please reload the page to try again.');
        }
    });
    app_socket.on('disconnect', app_socket_on_disconnect);
}

function entered_game_room_response_Socketlistener(response) {
    if (response.success) {
        enteredGameRoom = true;
        console.log('Entered game room');
        // after the jwt is validated in rust, initiate app socket
        start_app_socket();
        // display Start Button here
        $('#start-game-btn').css('display', 'block');
    } else {
        console.error(response.message);
        window.location.reload();

        // Notify user and provide next steps
        alert('Error connecting to the game server. Please reload the page to try again.');
    }
}

function getDotPosition() {
    return {top: parseInt($dot.css('top')), left: parseInt($dot.css('left'))};
}

function handleMovement() {
    let dotPosition = getDotPosition();
    if (pressedKeys['ArrowUp']) {
        if (dotPosition.top > dotHeight) {
            $dot.css('top', dotPosition.top - 10 + 'px');
        }
    }
    if (pressedKeys['ArrowDown']) {
        if (dotPosition.top < window.innerHeight - dotHeight) {
            $dot.css('top', dotPosition.top + 10 + 'px');
        }
    }
    if (pressedKeys['ArrowLeft']) {
        if (dotPosition.left > dotWidth) {
            $dot.css('left', dotPosition.left - 10 + 'px');
        }
    }
    if (pressedKeys['ArrowRight']) {
        if (dotPosition.left < window.innerWidth - dotWidth) {
            $dot.css('left', dotPosition.left + 10 + 'px');
        }
    }
    animationFrame = requestAnimationFrame(handleMovement);
}

function handleMovementCrossPath() {
    let dotPosition = getDotPosition();
    // Get the center positions of the screen
    if (!(dotPosition.left < centerXRange[1] && dotPosition.left > centerXRange[0]) && !(dotPosition.top < centerYRange[1] && dotPosition.top > centerYRange[0])) {
        // reset the dot to the center of the screen
        $dot.css('left', centerX + 'px');
        $dot.css('top', centerY + 'px');
    }

    if (pressedKeys['ArrowUp']) {
        // Only allow vertical movement if the dot is aligned horizontally at the center
        if (dotPosition.left < centerXRange[1] && dotPosition.left > centerXRange[0] && dotPosition.top > dotHeight) {
            $dot.css('top', dotPosition.top - 10 + 'px');
        }
    }
    if (pressedKeys['ArrowDown']) {
        // Only allow vertical movement if the dot is aligned horizontally at the center
        if (dotPosition.left < centerXRange[1] && dotPosition.left > centerXRange[0] && dotPosition.top < window.innerHeight - dotHeight) {
            $dot.css('top', dotPosition.top + 10 + 'px');
        }
    }
    if (pressedKeys['ArrowLeft']) {
        // Only allow horizontal movement if the dot is aligned vertically at the center
        if (dotPosition.top < centerYRange[1] && dotPosition.top > centerYRange[0] && dotPosition.left > dotWidth) {
            $dot.css('left', dotPosition.left - 10 + 'px');
        }
    }
    if (pressedKeys['ArrowRight']) {
        // Only allow horizontal movement if the dot is aligned vertically at the center
        if (dotPosition.top < centerYRange[1] && dotPosition.top > centerYRange[0] && dotPosition.left < window.innerWidth - dotWidth) {
            $dot.css('left', dotPosition.left + 10 + 'px');
        }
    }
    animationFrame = requestAnimationFrame(handleMovementCrossPath);
}

document.addEventListener('keydown', (event) => {
    if (!pressedKeys[event.key]) {
        pressedKeys[event.key] = true;
    }

    // Start movement loop if not already running
    if (!animationFrame) {
        animationFrame = requestAnimationFrame(handleMovement);
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

function point_added_response_Socketlistener(response) {
    if (response.success) {
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
    } else {
        console.error(response.message);
    }
}

function emitSessionJWT() {
    return new Promise((resolve, reject) => {
        app_socket.emit('get_session', (response) => {
            if (response.success && response.session_jwt) {
                resolve(response.session_jwt);
            } else {
                reject(new Error('Failed to retrieve session JWT'));
            }
        });
    });
}

async function getSessionJWT() {
    try {
        const session_jwt = await emitSessionJWT();
        console.log(`Session id: ${session_jwt}`);
        return session_jwt; // Return the resolved JWT value
    } catch (err) {
        console.error(err.message);
        return null; // Return null in case of an error
    }
}

async function addPointToServer() {
    const session_jwt = await getSessionJWT();
    if (!session_jwt) {
        console.error('No session ID found');
        window.location.reload();
        return;
    } 
    
    const message = JSON.stringify({
        event: 'point_added', // Define the action
        data: { session_jwt, gameId },  // Your payload
    });
    game_socket.send(message);
}

function dotEnteredCircle($circle, extra_actions) {
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
    circleDone($circle, true, extra_actions);
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

function start_game_response_Socketlistener(response) {
    if (!response.success) {
        enteredGameRoom = false;
        console.error(`server error: ${response.message}`);
        // Notify user that there was an error starting the game
        window.location.reload();
    } else {
        console.log(`server sucess: ${response.message}`);
        $('#start_game_token').val(response.start_game_token);
        // create a new list for point tokens to be added to
        resetPointListInDB();
    }
}

async function startGameServer(session_jwt) {
    const message = JSON.stringify({
        event: 'start_game', // Define the action
        data: { session_jwt, gameId },  // Your payload
    });
    game_socket.send(message);
}

function startGame({intervalFunction}) {
    console.log('Starting game!');
    let countDown = 3;
    $('#instructions').css('display', 'none');
    $('#starting').css('display', 'flex');
    const countdownInterval = setInterval(async function() {
        if (countDown > 0) {
            $(`#startCount`).css('color', '#2e2e2e');
            $(`#startCount`).text(countDown);
            countDown--;
        } else {
            clearInterval(countdownInterval);
            $('#starting').css('display', 'none');
            $('#score-card').css('display', 'flex');
            intervalFunction.function(intervalFunction.inputs);
            if (intervalFunction.interval) {
                circleInterval = setInterval(function() {
                    intervalFunction.function(intervalFunction.inputs);
                }, intervalFunction.interval);
            }
            startTimer();
            if (loggedIn && enteredGameRoom) {
                const session_jwt = await getSessionJWT();
                if(session_jwt) {
                    console.log(`UserId starting game`);
                    startGameServer(session_jwt);
                    return;
                }
            }
            console.log('Starting game without server');
            enteredGameRoom = false;
            loggedIn = false;
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

function endGameSocketListener(response) {
    console.log('Game ended from server');
    if (circleInterval) { clearInterval(circleInterval); }
    $('#dot').css('display', 'none');
    clearCircles();
    $('#timer').css('display', 'none');
    startLoadingScreen();
    $('#end_game_token').val(response.end_game_token);
    // wait for stored_game_data event
}

function storedGameDataSocketListener(response) {
    console.log(`Stored game data: ${response}`);
    const end_game_token = $('#end_game_token').val();
    setHighScoreServer(end_game_token);
}
    

async function startLoadingScreen() {
    $('#loading-screen').css('display', 'flex');
    let loadingCount = 1;
    loadingInterval = setInterval(function() {
        if (loadingCount > 3) {
            $('.loading-dot').css('color', 'transparent');
            loadingCount = 1;
        } else {
            $(`#loading-dot${loadingCount}`).css('color', 'white');
            loadingCount++;
        }
    }, 1000);
}

function clearLoadingScreen() {
    clearInterval(loadingInterval);
    $('#loading-screen').css('display', 'none');
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
            clearLoadingScreen();
            if (response.points_added && response.points_added !== 'None') {
                $('#score-rank').text(response.score_rank);
                $('#score-points').text(response.points_added);
            } else {
                $('.score-ranking').css('display', 'none');
            }
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
    if (circleInterval) { clearInterval(circleInterval); }
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

function clone_circle_base() {
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
    return $circle;
}

function clone_circle({timeout, extra_actions}) {
    $circle = clone_circle_base();
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

