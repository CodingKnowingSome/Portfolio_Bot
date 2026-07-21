# Portfolio_Bot
A custom Discord bot created with Python and discord.py. Recreates some functionalities of AEGIS OS such as duty states, and introduces new functionalities such as automated shouts for AA student promotions. Logs are saved in a .log file, while warnings and above are also sent in a designated Discord channel. All commands and functions are coded asynchronously.

## Features
- **Configuration:** Channels and roles are loaded from a dotenv file by *config.py*.
- **Duty States Submissions:** Messages sent in the specified channel are first checked for formatting issue (*Events/DutyListener.py*). The correctly formatted are saved into a database. The incorrect ones are informed of the incorrect formatting.
- **Duty State Grading:** A permanent fetch button (created with *Commands/sendfetch.py*) fetches the oldest pending duty state. 2 buttons, accept and deny are presented, deny gives an option to input the denial reason.
- **Duty State Maker:** Formats the duty state based on the inputs (*Commands/dsmake.py*).
- **Leaderboard:** A permanent leaderboard, update every minute (*DutyStates/Leaderboard.py*). Can be reset, which creates an archive and sets everyone to 0 (*Commands/leaderboard_reset.py*).
- **AA Promotion Shouts:** When an attendance log is approved, a shout is sent mentioning the students who are in the server about being promoted (*Functions/AA_Promotions_Shouts.py*).
- **Discord Logging:** Using the logging module, and log warning or above is sent in a Discord channel.
- **Permissions:** Function (*access_check.py*) that restricts the usage of */leaderboardreset* and */sendfetch*.
- **Commands:** Dice, ping, pending (*Commands/*).

## Repository Structure
Portfolio_Bot/
├── commands/               # Slash commands
│   ├── dice.py             # Random dice roller
│   ├── dsmake.py           # Duty State formatter
│   ├── leaderboard_reset.py# Leaderboard archiver & quota reset
│   ├── pending.py          # User's pending duty state counter
│   ├── ping.py             # Bot latency checker
│   └── sendfetch.py        # Fetch generator for duty states
├── DutyStates/             # Duty states
│   ├── Accept.py           # Acceptance, point calculation and reaction handler
│   ├── Deny.py             # Denial and reaction handler
│   ├── DenyModal.py        # Modal UI for denial reason input
│   ├── Fetch.py            # Retrieves oldest pending duty state
│   ├── Leaderboard.py      # Creates and upkeeps the leaderboard
│   └── Views.py            # Permanent button
├── Events/                 # Message handlers
│   ├── DutyListener.py     # Duty state format validation
│   └── General.py          # 'Furios' event
├── Functions/              # Shouts
│   └── AA_Promotions_Shouts.py # Shouts student promotions
├── access_check.py         # Permission checker
├── config.py               # Loads channel and role IDs
├── database_setup.py       # Database setup
├── discord_logging.py      # Custom Discord logger
├── distributor.py          # Message distributor
├── logs.py                 # File and console logger
└── main.py                 # Bot initialization

## Databases
The bot uses 3 SQLite3 databases to store every information it needs.
1. **duty_states.db:** Contains all pending duty states by message ID.
2. **ds_metadata.db:** Contains user information for */dsmake* command.
3. **leaderboard.db:** Contains user - number pairs for the number of graded duty states, along with the message ID of the leaderboard.

## Running it yourself
1. **Prerequisites:**
   * Python 3.14
   * Git
2. **Clone:**
   * "git clone https://github.com/CodingKnowingSome/Portfolio_Bot"
   * "cd Portfolio_Bot"
3. **Dependencies:**
   * "pip install -r requirements.txt"
4. **.env Setup:**
```
DISCORD_TOKEN=your_bot_token_here
TEST_GUILD_ID=123456789012345678
LOG_CHANNEL_ID=123456789012345678
PING_ROLE_ID=123456789012345678
AA_LOGS_CHANNEL_ID=123456789012345678
GUEST_ROLE_ID=123456789012345678
OVERWATCH_ROLE_ID=123456789012345678
ARCHIVE_CHANNEL_ID=123456789012345678
ADMIN_ROLE_ID=123456789012345678
DSGRADE_CHANNEL_ID=123456789012345678
DS_CHANNEL_ID=123456789012345678
LD_CHANNEL_ID=123456789012345678
PROMOTION_SHOUTS_CHANNEL_ID=123456789012345678
```

5. **Start:**
   * Run "python main.py"

### Commits
Format: {type}: {short desc.}

* feat: new feature
* fix: fix of something
* docs: changes to documents
* refactor: rewriting code, no change in behaviour
* chore: updating dependencies, settings, etc.
