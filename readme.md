# !rememberme

!rememberme is a bot created to help people remember stuff to do, being notificated from a Telegram message without needing to install external app.

# How to use it

## Step 1 - Install Python and MongoDB

You'll need a local installation of Python in the server you want to run this software, and a installation of MongoDB for manage the database

## Step 2 - Install Python Requirements

To install the requirements run this code on root folder:

### On Windows
``` bash
pip install -r requirements.txt  
```
### On Linux
```bash
pip3 install -r requirements.txt  
```

## Step 3 - Set the Environ

Before starting the bot you need to set some os environ.

### MongoDB Connection environ

__rememberme_mongoip__            = IP of MongoDB Database

__rememberme_mongouser__          = User of MongoDB Database

__rememberme_mongopass__          = Password of MongoDB Database

__rememberme_mongoauthsource__    = Authsource of MongoDB Database

__rememberme_mongodb__            = DB of app in MongoDB Database

### Language environ

__rememberme_language__ = Set this variable using the name of dict object in "language.json" file. (for example _IT_ or _EN_) 

### Botfather Token environ

__rememberme_botfather_token__ = Set this variable using the token gived you from BotFather bot. To get your token follow [this](https://core.telegram.org/bots#3-how-do-i-create-a-bot) guide  or use the [BotFather bot itself!](https://t.me/botfather) 


## Step 4 - Start it!
Once you installed all the requirements and set all variables, you can start the bot just with:

### On Windows
``` bash
python main.py  
```
### On Linux
```bash
python3 main.py  
```


# Language update

If you desire you can update the language too (i would be grateful if you do), just add a new "object" to the language.json file with the translation of the language you desire.

I would be very greatful if you help me adding more languages!
