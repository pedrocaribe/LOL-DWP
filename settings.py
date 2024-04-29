import os
from pathlib import Path
from dotenv import load_dotenv
from colorama import Back, Fore,Style

# In Power Shell set the FLASK_ENV by using: $Env:FLASK_ENV = "development"
# Check if it was set correctly by issuing: echo $Env:FLASK_ENV

env_path = Path('.') / ('.env.debug' if os.getenv('FLASK_ENV') == 'development' else '.env')
load_dotenv(dotenv_path=env_path)

from settings_files._global import *

if os.getenv('FLASK_ENV') == 'development':
    print(f'{Fore.WHITE + Back.YELLOW}We are in DEBUG mode{Style.RESET_ALL}')

else:
    print(f'{Fore.WHITE + Back.RED}CAREFUL We are in PRODUCTION mode{Style.RESET_ALL}')