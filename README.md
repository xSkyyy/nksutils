# NKSUTILS
This is my main project at the moment, aside from Nekosu itself. 
So far the features are fairly limited and are implemented in far from ideal ways but I am using this project as a way to learn my way around Python better and be able to build bigger and better stuff in the future.
## Setup and installation
Setup and installation is **NOT RECOMMENDED**, however, it is fairly simple.
These instructions are written for Ubuntu 18.04LTS with Python3.9

1. Create an application at [Discord's developer site](https://discord.com/developers) and take note of the token
2. Clone the repository and navigate to the directory: `git clone https://github.com/xskyyy/nksutils && cd nksutils`
3. Install the required python modules: `pip3 install -r requirements.txt`
4. Rename and modify the config file: `mv config.sample.py config.py` then `nano config.py`
5. You should now be ready to start the bot, run `python3.9 main.py` to start.
## Support
No support will be provided for using this bot as it was never intended for public use. 
Use only at your own risk.

## Compatibility
Realistically, this isn't a very good solution for Discord -> osu! server communication, however: if you would like to run this bot it should be compatible with every server running the **RealistikOsu** fork of Ripple. Due to database differences it is unlikely to work properly on standard ripple instances. 
