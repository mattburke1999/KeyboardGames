## 1. User Clicks Game

**Frontend:**
- requests user_id through websocket
    - if not logged in, show message saying scores won't be saved unless logged in
    - otherwise skip everything else
- Sends a 'enter_game_room' socket event to server to join game room
    - includes user id and game id
    - recieves duration to use for game timer

**Server:**
- Joins game room with user id and game id
- responds with duration

## 2. Game Start:

**Frontend:**
- Sends a game_start socket event to the server to initiate a new game session.

**Server:**
- Creates a game session, starts a timer for the game duration, and issues a start game token.
- Responds to the frontend with the start token, which the frontend stores for later use.

## 3. Game Timer:

**Server:**
- Tracks the game duration with an internal timer.
- Sends an end game token to the frontend when the game timer expires.
- Prevents further points from being accepted after the timer ends.

## 4. Point Events:

**Frontend:**
- stores current timestamp for point
- Emits a point socket event each time the player scores a point.

**Server:**
- Receives the point event, validates it against:
    - **Time Constraints**: Ensures the point is within the game duration.
    - **Burst Threshold**: Tracks the number of points per second to detect excessive scoring (using a deque or similar structure).
- If valid, issues a point token and appends it to a list of point dictionaries ({token, timestamp}) for the session.
- Tracks bursts in a separate list, noting timestamps of bursts.
- If bursts exceed a certain limit within a defined period:
    - Stops the game by sending an end_game event to the frontend.
    - Flags the user account for review.

## 5. Game End:

**Frontend:**
- Stores the end game token when received.
- Sends a final HTTP request (or socket event) to submit the game result, including:
- The start token, end token, and list of point tokens/timestamps.

## 6. Score Validation and Update:

**Server:**
- Validates:
    - The start token matches the session's initial token.
    - The end token matches the token issued when the timer expired.
    - The point tokens are legitimate (match the stored tokens for the session and align with timing constraints).
        - validates server timestamps against FE timestamps for points, allowing some latency
- If all validations pass:
    - Updates the score in the database.
- If validation fails:
    - Rejects the submission.
    - Flags the user account for review (e.g., logging the event for manual or automated analysis).