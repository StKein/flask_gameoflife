# Game of Life
Flask 2-player variation
## Installation
1. Install python
2. Clone repository to local/hosting server
3. Open terminal, cd into directory you cloned repository to
4. (preferably) Make virtual environment, activate it
5. Type following:
- pip install -r requirements.txt
## Running
1. Open terminal in cloned repository directory
2. (if venv was added) Activate venv
3. Type following:
- flask run
4. Now you can connect to game server
## Notes:
- login is required for server actions
- you can watch others' games as well as participate
- games are stored in local db, so you can "pause" them any time
## Known bugs:
- server crash/error during generations-step phase leads to game being stuck
  - so far the only way to fix it is to either send (one!) required ajax manually once server is back online
  - otherwise just start a new game