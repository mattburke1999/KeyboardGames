# GAME/SOCKET Communications
## 1. User Clicks Game

**Frontend:**
- requests user_id through websocket
    - if not logged in, show message saying scores won't be saved unless logged in
    - otherwise skip everything else

## 4. Point Events:

**Server:**
- Receives the point event, validates it against:
    - **Burst Threshold**: Tracks the number of points per second to detect excessive scoring (using a deque or similar structure).
- Tracks bursts in a separate list, noting timestamps of bursts.
- If bursts exceed a certain limit within a defined period:
    - Stops the game by sending an end_game event to the frontend.
    - Flags the user account for review.

## 6. Score Validation and Update:

**Server:**
- If validation fails:
    - Rejects the submission.
    - Flags the user account for review (e.g., logging the event for manual or automated analysis).

# SKINS
- points awarded from games
    - possibly make place a multiplier times points scored = profile points
- possible add login bonus
- skins will be unlockable with points

# NEW GAMES
- shaky dot
    - the dot will shake around a few pixels 

- ### categories
    - existing ones will be timed
    - new: untimed/complete the steps
        - time is score

# ADs
- localstorage will hold 2 values: currentPage, and adHasRun
- anytime page loads, first compares current url/page against currentPage in localstorage
    - if different, set adHasRun to false
        - if home page (regardless if same or dif), set adHasRun to false
    - after logic to set adHasRun, set currentPage in localstorage
    - check to see if ad should be run
    - if adHasRun = false and the current page is not home page, redirect to ad route
- upon ad completion:
    - set adHasRun to true
    - the 'next url' will be stored somehere, redirect


# NEW UPDATES WITH RUST
## Flask Changes
### 1. User Login
- When a user logs in:
    - Validate their credentials.
    - Generate a session ID (e.g., UUID) and an expiration timestamp.
    - Store the session ID and expiration in the database.
    - Generate a JWT that includes the user_id and session_id as claims.
    - Return the JWT to the client.
- Example JWT Claims:

```
{
    "user_id": "12345",
    "session_id": "abcdef123456",
    "exp": 1700000000  // Expiration timestamp (optional)
}
```
### 2. /current_user Endpoint
- Update the /current_user endpoint to return the JWT:
    - Decode the Flask session to retrieve the user_id and session_id.
    - Generate a new JWT if needed and return it.
- Example Response:
```
{
    "logged_in": true,
    "jwt": "your_jwt_here"
}
```
### 3. User Logout
- When the user logs out:
     - Delete the session ID from the database.
## Socket (Rust) Changes
### 1. enter_game_room Event

- Receive the JWT from the client.
- Validate the JWT:
    - Decode the JWT using the shared secret.
    - Extract the user_id and session_id claims.
- Verify the session:
    - Query the database to ensure the session_id is valid and not expired.
- Create or update the game room:
    - Use the client's WebSocket Sender as the unique key in the game_rooms structure.
- Database Query to Validate Session:
```
SELECT session_id FROM user_sessions
WHERE user_id = ? AND session_id = ? AND session_expires_at > NOW();
```
### 2. Game Room Management
- Each game room is stored in memory with the Sender as the key.
- Use the user_id and session_id from the JWT for validation but avoid exposing it in socket messages.
## Database Updates
### 1. user_sessions Table
- Create a user_sessions table to store session details:
```
CREATE TABLE user_sessions (
    user_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    session_expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, session_id),
    FOREIGN KEY (user_id) REFERENCES accounts(id)
);
```
### 2. Session Management
- On Login:
    - Insert a new session ID and expiration time into the user_sessions table:
    ```
    INSERT INTO user_sessions (user_id, session_id, session_expires_at)
    VALUES (?, ?, ?);
    ```
- On Logout:
    - Delete the session ID:
    ```
    DELETE FROM user_sessions WHERE session_id = ?;
    ```
- Sockets/heartbeat
    - flask will have a single socket listener for heartbeat, checking logged in users
        - if the user has not sent a heartbeat within a certain period, clear their session data