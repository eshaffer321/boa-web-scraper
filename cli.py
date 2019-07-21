#!/usr/bin/env python

import os
import sys
import json
import logging
import threading

from runner import Runner
from knack import CLI
from knack.commands import CLICommandsLoader, CommandGroup
from knack.arguments import ArgumentsContext
from knack.help import CLIHelp

from knack.help_files import helps

cli_name = os.path.basename(__file__)

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

helps['parse run'] = """
    type: command
    short-summary: Start the scraper to run against accounts in accounts.json.
    examples:
        - name: Parse the accounts from acc.txt in a multi-threaded workload.
          text: {cli_name} parser run --threaded=yes --file=acc.txt
""".format(cli_name=cli_name)


def threaded_start(account):
    Runner(account).start()


def parse_handler(file=None, threaded=None, send=None):
    accounts = []

    if os.path.isfile(file):

        logging.info('Found file ' + file)

        with open(file) as json_file:

            data = json.load(json_file)

            if threaded:

                logging.info('Running in multi-threaded mode')

                thread_list = []
                for account in data:
                    thread = threading.Thread(target=threaded_start, args=(account,))
                    thread_list.append(thread)

                for thread_item in thread_list:
                    thread_item.start()

                for thread_item in thread_list:
                    thread_item.join()

            else:

                logging.info('Running in single-threaded mode')

                for account in accounts:
                    Runner(account).start()

    else:
        print('File not found')
        exit(1)

    return 'Finished'


WELCOME_MESSAGE = r"""

  ____              _             __                                _                
 |  _ \            | |           / _|     /\                       (_)               
 | |_) | __ _ _ __ | | __   ___ | |_     /  \   _ __ ___   ___ _ __ _  ___ __ _      
 |  _ < / _` | '_ \| |/ /  / _ \|  _|   / /\ \ | '_ ` _ \ / _ \ '__| |/ __/ _` |     
 | |_) | (_| | | | |   <  | (_) | |    / ____ \| | | | | |  __/ |  | | (_| (_| |     
 |____/ \__,_|_| |_|_|\_\ _\___/|_|   /_/    \_\_| |_| |_|\___|_| _|_|\___\__,_|____ 
 \ \        / / | |      / ____|                                 / ____| |    |_   _|
  \ \  /\  / /__| |__   | (___   ___ _ __ __ _ _ __   ___ _ __  | |    | |      | |  
   \ \/  \/ / _ \ '_ \   \___ \ / __| '__/ _` | '_ \ / _ \ '__| | |    | |      | |  
    \  /\  /  __/ |_) |  ____) | (__| | | (_| | |_) |  __/ |    | |____| |____ _| |_ 
     \/  \/ \___|_.__/  |_____/ \___|_|  \__,_| .__/ \___|_|     \_____|______|_____|
                                              | |                                    
                                              |_|                                    


Easily web scraper bankofamerica.com!
"""


class MyCLIHelp(CLIHelp):

    def __init__(self, cli_ctx=None):
        super(MyCLIHelp, self).__init__(cli_ctx=cli_ctx,
                                        privacy_statement='Only intended for personal use.',
                                        welcome_message=WELCOME_MESSAGE)


class MyCommandsLoader(CLICommandsLoader):

    def load_command_table(self, args):
        with CommandGroup(self, 'parse', '__main__#{}') as g:
            g.command('run', 'parse_handler')
        return super(MyCommandsLoader, self).load_command_table(args)

    def load_arguments(self, command):
        with ArgumentsContext(self, 'parse run') as ac:
            ac.argument('file', type=str, default="accounts.json")
        super(MyCommandsLoader, self).load_arguments(command)


mycli = CLI(cli_name=cli_name,
            config_dir=os.path.expanduser(os.path.join('~', '.{}'.format(cli_name))),
            config_env_var_prefix=cli_name,
            commands_loader_cls=MyCommandsLoader,
            help_cls=MyCLIHelp)
exit_code = mycli.invoke(sys.argv[1:])
sys.exit(exit_code)