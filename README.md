# Back Bot
### A bot for the best joke of all time

## Make sure you have already set up a discord bot, and provide the API key in a file named `super_secret_key.txt`

## THIS BOT CAN BE RUN THROUGH DOCKER OR LOCALLY!
If Docker is setup and the daemon is running, simply change the
`docker-compose.yml.example` file to contain you bot API token and rename
the file to `docker-compose.yml`. Then, just run:

```shell_session
  $ docker-compose up
```

## Without Docker...

## Dependencies
* Python 3.4.2+
* discord.py
* PyNaCl
* ffmpeg

#### Install discord.py

```shell_session
  $ pip install discord
```

#### Install pynacl

```shell_session
  $ pip install pynacl
```

#### Install ffmpeg

    Good luck!
    Make sure the path environment variable points to the executable folder!

## Run

```shell_session
  $ python back_bot.py
```


The file will be located from the base directory.
