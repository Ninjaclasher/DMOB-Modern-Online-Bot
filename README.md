# DMOB: Modern Online Bot
A Discord bot with program judging capabilities by using the <a href=https://github.com/dmoj>DMOJ</a> judge.

The bot utilizes the DMOJ Judge. Follow the instructions to install it <a href=https://github.com/dmoj/judge>here</a>.
This bot also requires the Discord api to be installed. Install it with `pip3 install discord`.

`cd`/`dir` inside the cloned DMOB directory.

Create the following folders:
```
judges
problems
```

Edit the `settings.py` file and fill in the `DMOBToken` field with a Discord bot token. As well, edit the other fields to suit your needs.

You will also need to create a MySQL database:
```
$ mysql -u root -p
mysql> CREATE DATABASE dmob DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
mysql> GRANT ALL PRIVILEGES ON dmob.* to 'dmob'@'localhost' IDENTIFIED BY '<password>';
mysql> exit
```
(UNFINISHED)

Usage Instructions: `python3 DMOBMain.py`
