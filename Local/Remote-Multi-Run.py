##### Module import
import argparse
import os
import socket

##### Common settings
buffer_size = 4096 # send 4096 bytes each time step
c_encode = 'utf-8' # encode of text

##### Arguement default value
default_process = 1
default_loop = 10
default_port  = 7788
# Depend on machine
default_addr  = '192.168.1.1'

##### Arguement parser
arg_parser = argparse.ArgumentParser() 
arg_parser.add_argument('script', type=str, help='python script file.')
arg_parser.add_argument('config', type=str, help='config file.')
arg_parser.add_argument('-r', '--process', type=int, default=default_process, help='number of seperated processes (panels).')
arg_parser.add_argument('-l', '--loop', type=int, default=default_loop, help='number of loops in each panel.')
arg_parser.add_argument('-a', '--addr', type=str, default=default_addr, help='address of remote machine.') 
arg_parser.add_argument('-p', '--port', type=int, default=default_port, help='listening port of remote machine.')
arg_parser.add_argument('-cs', '--copyscript', action='store_true', help='would copy script file from local if applied.')
arg_parser.add_argument('-cc', '--copyconfig', action='store_true', help='would copy config file from local if applied.')

##### Arguement data
raw_path_py  = arg_parser.parse_args().script
raw_path_cfg = arg_parser.parse_args().config
num_process  = arg_parser.parse_args().process
num_loop     = arg_parser.parse_args().loop
s_address    = arg_parser.parse_args().addr
s_port       = arg_parser.parse_args().port
copyscript   = arg_parser.parse_args().copyscript
copyconfig   = arg_parser.parse_args().copyconfig
# Extra
fn_py     = os.path.basename(raw_path_py)
fn_cfg    = os.path.basename(raw_path_cfg)
fsize_py  = os.path.getsize(raw_path_py) if copyscript else 0
fsize_cfg = os.path.getsize(raw_path_cfg) if copyconfig else 0
copyscript_indi = 1 if copyscript else 0
copyconfig_indi = 1 if copyconfig else 0

##### Socket
print( '[*] Socket generation starts.')
c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c_socket.connect((s_address, s_port))
print(f'[+] Socket connected {s_address}:{s_port}')

##### Preceding messege
# Prepare messege
print(f'[+] Preceding messege')
c_msg_1 = f'{fn_py}\x00{fn_cfg}\x00{num_process}\x00{num_loop}\x00{copyscript_indi}\x00{copyconfig_indi}\x00{fsize_py}\x00{fsize_cfg}\x00'
print(f'    [-] Messege: {c_msg_1}')
c_msg_1_b = c_msg_1.encode(c_encode)
# Send messege
c_socket.sendall(c_msg_1_b)
print( '    [-] Messege send.')
# Receive echo from server
s_echo_1 = c_socket.recv(buffer_size).decode(c_encode)
print(f'    [-] Server echo: {s_echo_1}')

##### Script file
print(f'[+] Sending script file')
# Judge if send script file and determine messege content
print(f'    [-] Copy script: {copyscript}')
if copyscript:
    c_msg_2_b = open(raw_path_py, "rb").read()
else:
    c_msg_2_b = b'empty\x00'
# Send messege
c_socket.sendall(c_msg_2_b)
print( '    [-] Messege send.')
# Receive echo from server
s_echo_2 = c_socket.recv(buffer_size).decode(c_encode)
print(f'    [-] Server echo: {s_echo_2}')

##### Config file
print(f'[+] Sending config file')
# Judge if send script file and determine messege content
print(f'    [-] Copy config: {copyconfig}')
if copyconfig:
    c_msg_3_b = open(raw_path_cfg, "rb").read()
else:
    c_msg_3_b = b'empty\x00'
# Send messege
c_socket.sendall(c_msg_3_b)
print( '    [-] Messege send.')
# Receive echo from server
s_echo_3 = c_socket.recv(buffer_size).decode(c_encode)
print(f'    [-] Server echo: {s_echo_3}')

##### Flag for start script branching on server side
print(f'[+] Script brancher')
c_msg_4_b = b'Now you can start script branching.'
c_socket.sendall(c_msg_4_b)
# Receive echo from server
s_echo_4 = c_socket.recv(buffer_size).decode(c_encode)
print(f'    [-] Server echo: {s_echo_4}')

##### Endgame
c_socket.close()
print('[*] Socket done.')