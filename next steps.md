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
- skins will be unlockable with points

# NEW GAMES
- stay on the path
    - screen will have a cross on it, the path which the dot can travel
- shaky dot
    - the dot will shake around a few pixels 

- ### categories
    - existing ones will be timed
    - new: untimed/complete the steps

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
