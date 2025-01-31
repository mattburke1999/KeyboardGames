# GAME/SOCKET Communications
## 1. User Clicks Game


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
- create a new simple app that can be run locally for adding new skins to make it easier
    - if an admin page is created, this could be moved into that
- add a base_colors table for colors that skin_input_values can link to

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

## Socket (Rust) Changes

### Session Management
- rust will have background task to remove outdated session data from both in memory hash and redis

## Flask Changes
### Session Management
- Sockets/heartbeat
    - flask will have a single socket listener for heartbeat, checking logged in users
        - if the user has not sent a heartbeat within a certain period, clear their session data from db and redis