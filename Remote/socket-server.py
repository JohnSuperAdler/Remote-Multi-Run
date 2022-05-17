##### Very first
Author  = 'JohnSuperAdler'
Version = '0.1'

##### Module import
import os
import sys
import socket
import argparse
import subprocess
from configparser import ConfigParser
import datetime

##### Arguement parser: Get machine individual setting
arg_parser = argparse.ArgumentParser() 
arg_parser.add_argument('setting', type=str, default='machine_info.ini', help='Path of setting file of this machine.')
path_machine_info = arg_parser.parse_args().setting

##### Config Parser
machine_info = ConfigParser()
machine_info.read(path_machine_info)
m_name      = machine_info['machine'].get('m_name')
m_memo      = machine_info['machine'].get('m_memo')
s_addr      = machine_info['socket_setting'].get('s_addr')
s_port      = machine_info['socket_setting'].getint('s_port')
s_buffer    = machine_info['socket_setting'].getint('s_buffer')
s_encode    = machine_info['socket_setting'].get('s_encode')
s_SBshell   = machine_info['socket_setting'].get('s_SBshell')
dir_exe     = machine_info['script_directory'].get('dir_exe')
dir_setting = machine_info['script_directory'].get('dir_setting')
dir_output  = machine_info['script_directory'].get('dir_output')

##### loop shell script seed
sh_seed = 'for i in {1..*REP-loop*}; do\n  *REP-cmd*\ndone'

##### Socket start up
print( '[*] Socket server generation starts.')
s = socket.socket()
s.bind(('', s_port))
s.listen(5)
print(f'[*] Socket generated on {s_addr}:{s_port}')

##### Socket action
# For keeping listening, apply while loop.
while True:
    ##### Connection
    c_socket, c_addr = s.accept()
    print(f'[+] New connection received, from {c_addr}')    
    
    ##### Preceding messege from client
    print(f'[+] Preceding messege')
    c_msg_1_b = b''
    while True:
        byte_recv = c_socket.recv(s_buffer)
        c_msg_1_b += byte_recv
        if c_msg_1_b.count(b'\x00') == 8:
            print('    [-] Messege receive complete.')
            break
    c_msg_1_li = list(map(lambda x: x.decode(s_encode), c_msg_1_b.split(b'\x00')))
    print(f'    [-] Messege: {c_msg_1_li}')
    # Giving variable name
    fn_py, fn_cfg, process, loop, copyscript_indi, copyconfig_indi, fsize_py, fsize_cfg, _ = c_msg_1_li
    # Echo to client
    s_echo_1 = f'Preceding messeege received. {c_msg_1_li}'
    c_socket.send(s_echo_1.encode(s_encode))

    ##### Preparation for file transfering
    fsize_py  = int(fsize_py)
    fsize_cfg = int(fsize_cfg)
    dst_path_py  = os.path.join(dir_exe, fn_py)
    dst_path_cfg = os.path.join(dir_setting, fn_cfg)
    if copyscript_indi == '1':
        copyscript = True
    elif copyscript_indi == '0':
        copyscript = False
    else:
        sys.exit('! Copyscript boolean setting failed.')
    if copyconfig_indi == '1':
        copyconfig = True
    elif copyconfig_indi == '0':
        copyconfig = False
    else:
        sys.exit('! Copyconfig boolean setting failed.')

    ##### Script file
    print(f'[+] Receiving script file')
    print(f'    [-] Copy script file: {copyscript}')
    if copyscript:
        c_msg_2_b = b''
        while len(c_msg_2_b) < fsize_py:
            byte_recv = c_socket.recv(s_buffer)
            c_msg_2_b += byte_recv
        print(f'    [-] Script file copy success, size of script = {len(c_msg_2_b)}B')
        with open(dst_path_py, 'wb') as f:
            f.write(c_msg_2_b)
        print(f'    [-] File saved to {dst_path_py}')
        s_echo_2 = f'Script file received. {len(c_msg_2_b)}B'
    else:
        byte_recv = c_socket.recv(s_buffer)
        s_echo_2 = f'Script file transfer skipped.'
    # Echo to client
    c_socket.send(s_echo_2.encode(s_encode))

    ##### Config file
    print(f'[+] Receiving config file')
    print(f'    [-] Copy config file: {copyconfig}')
    if copyconfig:
        c_msg_3_b = b''
        while len(c_msg_3_b) < fsize_cfg:
            byte_recv = c_socket.recv(s_buffer)
            c_msg_3_b += byte_recv
        print(f'    [-] Config file copy success, size of file = {len(c_msg_3_b)}B')
        with open(dst_path_cfg, 'wb') as f:
            f.write(c_msg_3_b)
        print(f'    [-] File saved to {dst_path_cfg}')
        s_echo_3 = f'Config file received. {len(c_msg_3_b)}B'
    else:
        byte_recv = c_socket.recv(s_buffer)
        s_echo_3 = f'Config file transfer skipped.'
    # Echo to client
    c_socket.send(s_echo_3.encode(s_encode))

    ##### Intermission
    print(f'[+] Socket messege receiving and file transfer from {c_addr} done.')

    ##### Script branching on Local machine
    # Flag
    byte_recv = c_socket.recv(s_buffer)
    # Generate loop shell script
    py_cmd = f'python \'{dst_path_py}\' --config \'{dst_path_cfg}\' --machine \'{path_machine_info}\''
    sh_cont = sh_seed.replace('*REP-loop*', f'{loop}').replace('*REP-cmd*', py_cmd)
    timetag = datetime.datetime.now().strftime('%y%m%d_%H%M')
    path_sh = os.path.join(dir_exe, f'ScriptBrancher_{timetag}.sh')
    with open(path_sh, 'w') as f: f.write(sh_cont)
    # Generate script brancher command
    cmd = f'bash \'{s_SBshell}\' {process} "bash \'{path_sh}\'"'
    subprocess.run(cmd, shell=True)
    print(f'[+] [{timetag}] Start running script. Command = {cmd}')
    # Echo to client
    s_echo_4 = f'Start running script. [{timetag}]'
    c_socket.send(s_echo_4.encode(s_encode))

    #####
    print(f'\n[*] Socket keep listening as {s_addr}:{s_port}\n')