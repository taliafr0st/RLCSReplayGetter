An automatic RLCS replay fetcher using the Ballchasing API.

Available under [CC-BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt).
* I'm not a lawyer, but this basically means you need to give me credit if you use any part of this script, and you may only use it for non-commercial purposes. Any derivative works, whether for personal or commercial use, must be published under this license, or a compatible one.

# Setup

## Requirements
* Python 3.11
* pip
* Run command `pip install -r requirements.txt` from the root directory of the repo.

## File Creation
Create a file called `auth.txt` in the root directory of the repo and paste your [Ballchasing auth key](https://ballchasing.com/upload) into it.

# Details
The script will make a GET request to the Ballchasing API every 15 seconds, collecting the last 60 seconds of replays uploaded to the [RLCS ballchasing account](https://ballchasing.com/?uploader=76561199225615730).

In order to avoid duplicate outputs replays are indexed by the two team names in game, and by the game number (the RLCS replays have a set format allowing me to determine this.

More validation is performed to account for RLCS admin human errors. **Please do not harass me or other RLCS admins if they don't use the exact right replay name format for this script, they're working hard enough as it is and are certainly not obliged to keep this script running on any licensees behalfs.**

## Outputs
* Terminal
    * The full parsed replay information - the replay upload time (UTC), region, series ID, game number, both teams, the series score according to the script, the game score and the overtime information. In the event of a replay parsing error, the error is outputted to the terminal with the replay title.
* The Timeline `timeline.txt`
    * Minimised replay information for public consumption - the replay upload time (UTC), region, both teams, the series score according to the script, the game score and the overtime information.
* The JSON Dump `series.json`
    * Base level information for use in other applications - the series start time (UTC), region, both teams, the game scores and the overtime information.
