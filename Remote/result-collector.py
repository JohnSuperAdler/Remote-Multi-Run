##### Result Collector
# Automatically transfer EMMC results to remote server when generated

##### Very first
Author  = 'JohnSuperAdler'
Version = '0.1'

##### Import module
import os
import time
import subprocess
import datetime
import argparse
from configparser import ConfigParser
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

##### Arguement parser: Get machine individual setting
arg_parser = argparse.ArgumentParser() 
arg_parser.add_argument('setting', type=str, default='machine_info.ini', help='Path of setting file of this machine.')
path_machine_info = arg_parser.parse_args().setting

##### Config Parser
machine_info = ConfigParser()
machine_info.read(path_machine_info)
m_name          = machine_info['machine'].get('m_name')
m_memo          = machine_info['machine'].get('m_memo')
dir_output      = machine_info['script_directory'].get('dir_output')
Local_PC_addr   = machine_info['Local_PC_setting'].get('Local_PC_addr')
Local_PC_port   = machine_info['Local_PC_setting'].get('Local_PC_port')
Local_PC_user   = machine_info['Local_PC_setting'].get('Local_PC_user')
Local_PC_dir    = machine_info['Local_PC_setting'].get('Local_PC_dir')
Local_PC_subfol = machine_info['Local_PC_setting'].get('Local_PC_subfol')

##### Other parameter
buffer_time_1 = 60
buffer_time_2 = 60

def time_tag(input_dt, type=1):
    if type == 2:
        tag = input_dt.strftime('%Y/%m/%d %H:%M:%S')
    else:
        tag = input_dt.strftime('%y%m%d_%H%M')
    return tag

class LoggingEventHandlerSE(LoggingEventHandler):
    def on_created(self, event):
        global buffer_dir_li
        current_path = event.src_path
        rel_path = os.path.relpath(current_path, path)
        # Only processes generated folder
        if os.path.isdir(current_path):
            buffer_dir_li.append(current_path)
            print(f'[+] {time_tag(datetime.datetime.now(), type=2)} - New folder created: {rel_path}')

if __name__ == "__main__":
    path = dir_output
    path = os.path.abspath(path)
    event_handler = LoggingEventHandlerSE()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print( f'[*] Result Collector ({Version}) starts monitoring...')
    print( f'[*] Remote machine: {Local_PC_addr}')
    print( f'[*] Remote folder: {os.path.join(Local_PC_dir, Local_PC_subfol)}')
    buffer_dir_li = []
    try:
        while True:
            time.sleep(buffer_time_1)
            if len(buffer_dir_li) != 0:
                temp_dir_li = buffer_dir_li.copy()
                print(f'[+] {time_tag(datetime.datetime.now(), type=2)} - {len(temp_dir_li)} new folder(s) detected:')
                for i in range(len(temp_dir_li)):
                    print(f'    [-] {temp_dir_li[i]}')
                print(f'[+] Buffer time phase: {buffer_time_2} sec')
                time.sleep(buffer_time_2)
                print(f'[+] {time_tag(datetime.datetime.now(), type=2)} - Start process:')
                for j in range(len(temp_dir_li)):
                    print(f'    [-] Folder {temp_dir_li[j]} transfer starts.')
                    subprocess.run(f'scp -r -P {Local_PC_port} "{temp_dir_li[j]}" {Local_PC_user}@{Local_PC_addr}:{os.path.join(Local_PC_dir, Local_PC_subfol)}', shell=True)
                    print(f'    [-] Folder {temp_dir_li[j]} transfer done.')
                    buffer_dir_li.remove(temp_dir_li[j])
                print(f'[+] {len(temp_dir_li)} folder(s) transfer done.')
                if len(buffer_dir_li) != 0:
                    print(f'[+] {len(buffer_dir_li)} folders waiting for next transfer phase')
    except KeyboardInterrupt:
        observer.stop()
    observer.join()