import os
from pathlib import Path
from dotenv import load_dotenv
from colorama import Back, Fore,Style

# In Power Shell set the FLASK_ENV by using: $Env:FLASK_ENV = "development"
# Check if it was set correctly by issuing: echo $Env:FLASK_ENV

current_env = os.getenv('FLASK_ENV', 'production')
dotenv_path = Path('.') / ('.env.debug' if current_env == 'development' else '.env.production')
print(f'Loading .ENV file from {dotenv_path}')
load_dotenv(dotenv_path=dotenv_path)

if os.getenv('FLASK_ENV') == 'development':
    print(f'{Fore.WHITE + Back.YELLOW}We are in DEBUG mode{Style.RESET_ALL}')

else:
    print(f'{Fore.WHITE + Back.RED}CAREFUL We are in PRODUCTION mode{Style.RESET_ALL}')

RIOT_TOKEN = os.getenv("RIOT_TOKEN", False)
MAIL_PASSWD = os.getenv("MAIL_PASSWD", False)
