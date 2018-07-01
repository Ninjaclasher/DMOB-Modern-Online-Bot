# DMOB: Modern Online Bot
A Discord bot with program judging capabilities by using the <a href=https://github.com/dmoj>DMOJ</a> judge.

The bot utilizes the DMOJ Judge. Follow the instructions to install it <a href=https://github.com/dmoj/judge>here</a>.
This bot also requires the Discord api to be installed. Install it with `pip3 install discord`.

`cd`/`dir` inside the cloned DMOB directory.

Create the following folders:
```
contests
deleted_problems
deleted_submissions
judges
players
problems
submissions
```
These will be the locations where all the information will be stored as json files.

Edit the `settings.py` file and fill in the `DMOBToken` field with a Discord bot token. As well, edit the other fields to suit your needs.

Usage Instructions: `python3 DMOBMain.py`
