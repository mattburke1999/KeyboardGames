const numCircles = 25;
const storageName = 'dotGame-highScore-secondCircle';
const allCircles = [];
const displayedCircles = [];
createCircles();

function createCircles() {
    const $circle = $('#circle-1');
    const $circleGrid = $('#circle-grid');
    for (let i = 0; i < numCircles - 1; i++) {
        const $newCircle = $circle.clone();
        const id = `circle-${i + 2}`;
        $newCircle.attr('id', id);
        $newCircle.appendTo($circleGrid);
        allCircles.push(id);
    }
}

function gameStarter() {
    startGame({
        intervalFunction: {
            function: display_circles,
            inputs: {},
            interval: 890
        }
    });
}

function randomAmplitude(upAndDown=false) {
    // amplitude is random vlaue between 5 and 10
    let amplitude = Math.random() * 7 + 3;
    if (upAndDown) {
        let min = (amplitude / 10) * 100;
        return [amplitude, min];
    } else {
        return amplitude;
    }
}


function display_circles() {
    //create a list of circles in allCircles but not in displayedCircles
    const hiddenCircles = allCircles.filter((circle) => !displayedCircles.includes(circle));
    console.log(displayedCircles.length)
    // pick a random circle from the list
    let circleId = hiddenCircles[Math.floor(Math.random() * hiddenCircles.length)];
    console.log(circleId);
    $(`#${circleId} .circle`).css('borderColor', 'white');
    let sideToSideAmp = randomAmplitude();
    $(`#${circleId}`).css('--side-to-side-amplitude', `${sideToSideAmp}vw`);
    $(`#${circleId}`).addClass('slide');
    let [upAndDownAmp, min] = randomAmplitude(true);
    $(`#${circleId} .circle`).css('--up-and-down-amplitude', `min(${min}px, ${upAndDownAmp}vh)`);
    $(`#${circleId} .circle`).addClass('slide');
    $(`#${circleId} .circle`).data('pointAdded', 'false');
    $(`#${circleId} .circle`).data('done', 'false');
    displayedCircles.push(circleId);
    

    // Listen for the dot's movement
    document.addEventListener('keydown', function(event) {
        event.stopPropagation();
        if (event.key === ' ' && $(`#${circleId} .circle`).data('done') !== 'true') {
            checkDotInsideCircle(event, $(`#${circleId} .circle`));
        }
    });

    setTimeout(function () {
        document.removeEventListener('keydown', checkDotInsideCircle);
        if ($(`#${circleId} .circle`).data('done') !== 'true') {
            circleDone($(`#${circleId} .circle`), false);
        }
    }, 7500);
}

function getCurrentCirclePosition($circle) {
    // Get the computed style of the circle
    const computedStyle = window.getComputedStyle($circle[0]);
    const transformMatrix = computedStyle.transform;
    let yVal = 0;
    // Extract the translateX value from the matrix
    if (transformMatrix && transformMatrix !== 'none') {
      const matrixValues = transformMatrix.match(/matrix.*\((.+)\)/)[1].split(', ');
      yVal = parseFloat(matrixValues[5]);
    }
    // get computed style of circle-wrapper
    const computedStyleWrapper = window.getComputedStyle($circle.parent()[0]);
    const transformMatrixWrapper = computedStyleWrapper.transform;
    let xVal = 0;
    if (transformMatrixWrapper && transformMatrixWrapper !== 'none') {
        const matrixValuesWrapper = transformMatrixWrapper.match(/matrix.*\((.+)\)/)[1].split(', ');
        xVal = parseFloat(matrixValuesWrapper[4]);
    }
    return {x: xVal, y: yVal};
  }



function resetCircle($circle) {
    let circlePosition = getCurrentCirclePosition($circle);
    $circle.removeClass('slide');
    $circle.parent().removeClass('slide');
    $circle.css('transform', `translate(${circlePosition.x}px, ${circlePosition.y}px)`);
}

function clearCircle($circle) {
    $circle.css('borderColor', 'transparent');
    $circle.css('backgroundColor', 'transparent');
    $circle.text('');
    displayedCircles.splice(displayedCircles.indexOf($circle.parent().attr('id')), 1);
}

function clearCircles() {
    $('#circle-grid').css('display', 'none');
}



