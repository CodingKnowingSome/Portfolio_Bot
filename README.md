# Portfolio Bot

A Discord bot created by *KapitanyDrake* for showcase purposes.

- Python 3.14
- `discord.py`
- Flask
- SQLite3

Features the duty state workflow, KoS checker, blacklists, AA student promotion notifications and other misc. features.

## Features

### Duty State Submission and Grading

- **Duty State Formatter:** `/dsmake` formats your duty state based on user inputs.
- **Format checking:** The bot verifies the formatting before adding the duty state to the pending list.
- **Grading**: Pulls the oldest duty state, uses a modal to get the denial reason.
- **Leaderboard:** Leaderboard of the Officers with the amount of graded duty state, updates every minute.

### AA

- **Promotion Shout:** A shout notifies the students once they are promoted, pinging the ones in the server.
- **Leaderboard:** Leaderboard of the Staff with the amount of lessons, updates every minute.

### Inactivity Notices

- **Auto role:** Automatically gives and removes the IN role when it is approved and the message is deleted.
- **Leaderboards:** The leaderboards shows who are on inactivity notice.

### Flask and Roblox API

- **API and Database:** Runs a Flask API on port 5000 with its own database.
- **KoS:** Keeps track of current and past KoS users by their Roblox ID.
- **Blacklists:** Keeps track of current blacklists by Roblox IDs.

## Repository Structure

- **Main Folder:** `main.py`, loggers, config and API.
- **/AA:** AA Leaderboard and promotion shouts.
- **/commands:** Slash commands.
- **/data:** The database files.
- **/DutyStates:** Leaderboard, duty state grading.
- **/Events:** Misc. event, duty state submissions.
- **/Functions:** Helper functions used across the bot.

## Slash Commands

| Command               | Description                                                                 | Permission |
|:----------------------|:----------------------------------------------------------------------------|:-----------|
| `/aaleaderboardreset` | Resets the AA leaderboard and archives the current state.                   | Officer+   |
| `/blacklist`          | Blacklist or unblacklist a user.                                            | Tester     |
| `/blacklist-list`     | Lists all the current blacklists.                                           | Everyone   |
| `/dice`               | Outputs a random number between 1 and the user given max.                   | Everyone   |
| `/dsmake`             | Formats the duty state based on the user inputs and the already known info. | Guest+     |
| `/is-blacklisted`     | Checks if a user is blacklisted.                                            | Everyone   |
| `/kos`                | Checks the user's KoS status.                                               | Everyone   |
| `/kosmake`            | Used to edit a user's KoS status.                                           | Tester     |
| `/leaderboardreset`   | Resets and archives the Officer leaderboard.                                | Overwatch  |
| `/pending`            | Checks the amount of pending duty states the user has.                      | Guest+     |
| `/ping`               | Responds with the latency of the bot.                                       | Everyone   |
| `/sendfetch`          | Sends a new duty state fetch message.                                       | Admin      |

## Running It

### Prequisites

- Python 3.12+
- Git

### Installation

```bash
git clone https://github.com/CodingKnowingSome/Portfolio_Bot.git
cd Portfolio_Bot
pip install -r requirements.txt
```

### .env Setup

```dotenv
DISCORD_TOKEN=bot_token
TEST_GUILD_ID=your_server_id
LOG_CHANNEL_ID=log_channel_id
PING_ROLE_ID=log_channel_ping_role_id
AA_LOGS_CHANNEL_ID=aa_logs_channel_id
GUEST_ROLE_ID=guest_role_id
OVERWATCH_ROLE_ID=overwatch_role_id
ARCHIVE_CHANNEL_ID=officer_archive_channel_id
ADMIN_ROLE_ID=admin_role_id
DSGRADE_CHANNEL_ID=dutystate_grade_channel_id
DS_CHANNEL_ID=dutystate_channel_id
LD_CHANNEL_ID=leaderboard_channel_id
PROMOTION_SHOUTS_CHANNEL_ID=aa_promotion_shouts_channel_id
AA_LEADERBOARD_CHANNEL_ID=aa_learerboard_channel_id
AA_LEADERBOARD_ARCHIVE_CHANNEL_ID=aa_leaderaboard_archive_channel_id
OFFICER_ROLE_ID=officer_role_id
IN_ROLE_ID=inactivity_notice_role_id
IN_CHANNEL_ID=inactivity_notice_submission_channel_id
API_URL=http://127.0.0.1:5000/api
TESTER_ROLE_ID=tester_role_id
APPROVE_EMOJI_NAME=approve_emoji_name
DENY_EMOJI_NAME=deny_emoji_name
```

### Running the Bot

```bash
python3 main.py
```