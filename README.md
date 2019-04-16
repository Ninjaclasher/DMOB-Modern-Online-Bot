# DMOB: Modern Online Bot
A Discord bot with program judging capabilities by using the [DMOJ](https://github.com/dmoj) judge.

## Installation

First, clone the repository:
```bash
$ git clone https://github.com/Ninjaclasher/DMOB-Modern-Online-Bot
$ cd DMOB-Modern-Online-Bot
```

Next, install the prerequisites
```bash
$ apt update
$ apt install mariadb-server git python3
$ pip install -r requirements.txt
```

As well, create the MySQL database and load the tables:
```bash
$ mysql -u root -p
MariaDB> CREATE DATABASE dmob DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
MariaDB> GRANT ALL PRIVILEGES ON dmob.* to 'dmob'@'localhost' IDENTIFIED BY '<password>';
MariaDB> exit
$ mysql -uroot -p dmob < dmob.sql
```

Finally, create the necessary files and folders:
```
$ mkdir judges
$ mkdir problems
```

## Usage

Edit the `settings.py` file, and fill in any necessary fields. In particular, you should fill in the `DMOBToken` field with a Discord bot token.

To run:
```bash
$ python3 DMOBMain.py
```

To add judges, please follow the instructions from the [DMOJ Judge](https://github.com/DMOJ/judge).
