# Luminus Announcement Bot

:bell: Telegram bot for Luminus announcements.

This is a simple python script that [polls](<https://en.wikipedia.org/wiki/Polling_(computer_science)>) Luminus API for any unread Luminus announcements and forwards them to a telegram bot for notification.

## :toolbox: Requirements

- [:speech_balloon: Telegram](https://telegram.org/) account (for receiving notification and creating your telegram bot)
- [:snake: Python 3](https://www.python.org/downloads/) (for running the code)
- [:timer_clock: Cron](https://en.wikipedia.org/wiki/Cron) if you're on Mac or Linux which should be installed by default. Else, you can use other alternatives for scheduling task, eg [launchd](https://medium.com/swlh/how-to-use-launchd-to-run-services-in-macos-b972ed1e352) or [systemd timers](https://wiki.archlinux.org/index.php/Systemd/Timers)

## :hammer_and_wrench: Installation

1. Get your telegram id. You can do this by sending `/start` to this [bot](https://t.me/getmyid_bot).
1. Create a telegram bot. Send `/newbot` to [@BotFather](https://t.me/BotFather) and answer his questions. Note the generated token. Send `/start` to your bot so that it is authorized to message you.
1. Clone or download and unzip the repo.
1. Run `pip install --user -r requirements.txt` to download the dependent packages. As the script will be run with a task scheduler, I think using [virtualenv](https://docs.python.org/3/tutorial/venv.html) will complicate things.
1. Run `python config.py` to save your Luminus username, [password](#Why-do-I-need-to-save-my-Luminus-username-and-password-in-a-file?), Telegram id and bot token into a file locally.
   - This will update the `config.json` file.
1. Schedule to run the script periodically
   - **Windows**
     1. Open Task Scheduler.
     1. Click `Create Task...`.
     1. Give it a name like `Luminus announcement bot task`.
     1. Create a trigger, begin at startup, tick `Repeat task every:` and feel free to change the frequency.
     1. Create an action, set it to start a program, set:  
        Program as path to `pythonw.exe` (eg `"C:\Program Files\Python38\pythonw.exe"`)  
        Argument as path to `main.py` (eg `"C:\Users\<username>\Downloads\luminus-announcement-bot\main.py"`).
   - **Mac or Linux**
     1. Open the terminal, create a crontab by entering `crontab -e`.
     1. Save the cron expression, eg:  
        `0 * * * * /Users/<username>/Downloads/luminus-announcement-bot/main.py`  
        This expression runs [every hour](https://crontab.guru/#0_*_*_*_*). Change the frequency to your liking.

## :zipper_mouth_face: Caveat

Since the script will only be run when the computer is running, you will not receive notifications if the computer is shut down. Ideally, the script should be placed in a trusted server running 24/7. You can try using [sunfire](https://dochub.comp.nus.edu.sg/cf/guides/unix/major_unix_servers) if you have access to it, but I cannot guarantee if it is secure.

## :question: FAQ

### Why do I need to save my Luminus username and password in a file?

Good job for being cautious. Not gonna lie, saving password in a plaintext file is not secure, but it should be fine if you're not sharing your computer. Alternative is to store them as environment variables, but that's similarly insecure. Unfortunately, I have no idea how else to secure this. The Luminus credentials is only sent to Luminus for authentication like how you would login from the browser, so that the script can call the [Luminus API](https://luminus.portal.azure-api.net/docs/services/announcement/operations/GetUnreadAnnouncements).

### Why do I need to create a telegram bot?

The bot serves as a notification mechanism. Since telegram is cross platform, it can trigger notifications on your phone too. That is the only way I can think of to achieve cross platform notification, and it is pretty easy to use since it's just an API call.

I considered sharing one bot I created (ie hardcoding my bot's token into the code), but that would open my bot to potential abuse. Creating a bot with [@BotFather](https://t.me/BotFather) takes less than a minute anyway.

## :compass: What's next

I think this is good enough for now. If there's enough interest, next task might be to automate the installation steps, maybe with [setuptools](https://setuptools.readthedocs.io/en/latest/setuptools.html) or create packages with [one of these](https://stackoverflow.com/a/12059644).

Perhaps can also add a file sync feature but this is a whole other can of worms that I personally don't need.

## :kissing_heart: Acknowledgements

[NUSIVLEBot](https://t.me/NUSIVLEBot) - inspiration  
[pyfluminus](https://github.com/raynoldng/pyfluminus) - I copied over a bunch of code from here
