---

# PhantomGate – Multi‑Purpose Remote Administration & Botnet Simulation Framework

**PhantomGate** is a cross‑platform, modular remote administration tool (RAT) and botnet simulation agent developed for **ethical red teaming, security research, and controlled command‑and‑control (C2) demonstrations**. It works in tandem with **SpecterPanel**, a dedicated C2 server, to provide a modern, extensible framework for understanding and simulating advanced C2 operations in secure, lab‑friendly environments.

> **⚠️ IMPORTANT DISCLAIMER**  
> This project is intended **solely for educational purposes and authorized research**. Any unauthorized use, deployment, or distribution is strictly prohibited and may be illegal and unethical. The author assumes **no liability** for misuse. **You are responsible for complying with all applicable laws and regulations.**

---

## 📚 Table of Contents

- [Key Features](#-key-features)
- [Operational Workflow](#-operational-workflow)
- [Architecture & Components](#-architecture--components)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Endpoints (SpecterPanel)](#-api-endpoints-specterpanel)
- [Cross‑Platform Compatibility](#-cross‑platform-compatibility)
- [Safe Mode](#-safe-mode)
- [Related Project](#-related-project)
- [Security & Ethics Notice](#-security--ethics-notice)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## ⚙️ Key Features

- **Dynamic C2 Integration**  
  Connects seamlessly with SpecterPanel or retrieves control parameters from public sources (e.g., Google Drive), enabling flexible agent management.

- **Remote Command Execution**  
  Executes shell commands on remote hosts and securely reports results to the C2 server.

- **Advanced Code Injection**  
  Downloads and executes Python payloads from SpecterPanel, allowing sophisticated red team simulations.

- **Terminal‑Web Bridge**  
  Provides live remote control by linking the local terminal with the web‑based SpecterPanel interface.

- **Botnet Simulation Suite**  
  Supports UDP flood testing, SSH brute‑force attacks, and custom botnet actions – all remotely controlled.

- **Safe Mode**  
  Offers a non‑destructive simulation mode for lab exercises and training scenarios.

- **Persistent SQLite Tracking**  
  Registers agents and maintains persistent state using SQLite for reliable agent management.

- **Cross‑Platform Compatibility**  
  Operates on Windows, Linux, and Android with adaptive system detection.

- **Optional Kivy GUI**  
  Includes a mobile‑style graphical interface (`main.py`) for local management and live agent status monitoring.

- **Encrypted Communication**  
  Uses AES‑EAX encryption for all sensitive data exchanged with the C2 server.

- **Anti‑Analysis / VM Detection**  
  Implements basic virtual machine and container detection to simulate evasion techniques (can be disabled for lab use).

---

## 🕸️ Operational Workflow

1. **Agent Registration**  
   Upon launch, PhantomGate registers with SpecterPanel and stores target metadata locally in an SQLite database.

2. **Dynamic Instruction Polling**  
   Agents poll the C2 (SpecterPanel or a public control page) at configurable intervals for updated parameters, instructions, and payloads.

3. **Task Execution**  
   Received shell commands and Python code are executed on the agent. Output is securely transmitted back to the C2 server.

4. **Botnet Actions**  
   Agents may be instructed to perform UDP flood tests, SSH brute‑force attacks, or other botnet activities. Safe Mode ensures actions are simulated for demonstrations.

5. **Reporting & Output**  
   All command results, code outputs, and task statuses are reported to SpecterPanel via encrypted API calls.

---

## 🏗️ Architecture & Components

| File              | Description                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------|
| `PhantomGate.py`  | Core agent: handles C2 communication, command execution, code injection, and botnet actions. |
| `setting.py`      | Configuration manager: stores API keys, encryption keys, network settings, and paths.        |
| `main.py`         | Optional Kivy‑based GUI for local monitoring and database management.                         |

- **Encryption**: All C2 communications are encrypted using AES‑EAX with a hardcoded key (change in `setting.py` for production).
- **Database**: SQLite file (`db/targetData.db`) stores agent ID, registration status, thread permissions, and botnet state.
- **Threading**: Botnet operations (UDP flood, brute‑force) run in separate threads controlled via permission flags.

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Required packages: `requests`, `paramiko`, `pycryptodome`, `kivy` (optional for GUI)

### Installation Steps
1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/PhantomGate.git
   cd PhantomGate
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
   *(Create a `requirements.txt` if not present: `requests paramiko pycryptodome kivy`)*

3. **Configure the C2 server URL and API token**  
   Edit `setting.py` and update:
   ```python
   self.url = 'http://your-c2-server.com'   # e.g., http://127.0.0.1:5000
   self.API_TOKEN = 'your-api-token-here'
   ```
   > **Note:** The default token is a placeholder. **Change it immediately** for any real deployment.

4. **(Optional) Enable persistence on Windows**  
   Uncomment the call to `add_to_startup()` in `PhantomGate.py` to add the agent to startup.

---

## ⚙️ Configuration

All settings are managed in `setting.py` inside the `Setting` class. Key options:

| Setting                 | Description                                                      |
|-------------------------|------------------------------------------------------------------|
| `ENCRYPTION_KEY`        | 16‑byte AES key (change for production).                        |
| `url`                   | Base URL of the C2 server (SpecterPanel).                       |
| `API_TOKEN`             | Authentication token for API access.                             |
| `PORT`                  | List of ports used for UDP flood.                                |
| `FAKE_HEADERS`          | Raw byte headers to prepend to UDP flood packets.               |
| `BASE_DELAY` / `MAX_DELAY` / `MIN_DELAY` | Timing controls for UDP flood.                     |
| `USER_AGENTS`           | List of user‑agent strings for HTTP requests.                    |
| `MAIN_LOOP_DELAY`       | Polling interval (seconds) for fetching instructions.            |
| `INSTRUCTION`           | Allowed instruction types from C2.                               |
| `BOT_CATEGORY`          | Categories of botnet actions.                                    |
| `BUILT_IN_COMMAND`      | Commands handled internally (e.g., `sys_info`, `bot`, `db_info`). |

---

## 🚀 Usage

### Start the Agent (Headless)
```bash
python PhantomGate.py
```
The agent will:
- Register with the C2 server.
- Begin polling for instructions.
- Execute commands and report results.

### Start the GUI (Optional)
```bash
python main.py
```
The Kivy GUI allows you to:
- Add/remove target names in the local database.
- Monitor agent status.
- Manually trigger cleanup and thread management.

### Built‑in Commands (via C2)
Once connected, you can send commands from SpecterPanel. Examples:

- `ls -la` – List directory contents.
- `sys_info` – Gather system information (OS, hardware, network).
- `bot start <thread_id>` – Start a botnet action (UDP flood, brute‑force) as defined by C2 instructions.
- `bot stop <thread_id>` – Stop a running botnet action.
- `db_info` – Retrieve local database information.

### Code Injection
PhantomGate can fetch and execute Python scripts from the C2 using the `/api/injection/<target>` endpoint. Output is returned via `/api/injection_output_save`.

---

## 🔗 API Endpoints (SpecterPanel)

The agent communicates with SpecterPanel via the following encrypted endpoints (all payloads are AES‑encrypted JSON):

| Endpoint                                | Method | Description                                      |
|-----------------------------------------|--------|--------------------------------------------------|
| `/api/v1.2/register_target`             | POST   | Register a new agent.                            |
| `/api/v1.2/ApiCommand/<target>`         | GET    | Retrieve shell commands for the agent.           |
| `/api/v1.2/Apicommand/save_output`      | POST   | Submit command execution results.                 |
| `/api/v1.2/BotNet/<target>`             | GET    | Fetch botnet instructions (UDP flood, brute force). |
| `/api/v1.2/get_instruction/<target>`    | GET    | Obtain high‑level operational instructions.       |
| `/api/v1.2/injection/<target>`          | GET    | Retrieve Python payloads for remote code execution. |
| `/api/v1.2/injection_output_save`       | POST   | Submit output of executed payloads.               |

> **Note:** The API version (v1.2) and endpoints may change. Refer to the SpecterPanel documentation for the latest.

---

## 💻 Cross‑Platform Compatibility

| OS      | Tested | Notes                                                                 |
|---------|--------|-----------------------------------------------------------------------|
| Windows | ✅     | Full support, including registry persistence.                         |
| Linux   | ✅     | Works on major distributions (Ubuntu, Debian, CentOS).               |
| Android | ✅     | Detects Android via environment variables; requires Termux or similar.|
| macOS   | ⚠️     | Likely works but not officially tested.                               |

---

## 🛡️ Safe Mode

For training and lab environments, PhantomGate includes a **Safe Mode** that simulates destructive actions without actually performing them. To enable Safe Mode, set an environment variable or modify the code:

```python
SAFE_MODE = True   # in PhantomGate.py
```

When Safe Mode is active:
- UDP flood packets are **not sent**; only logging occurs.
- Brute‑force attempts are logged but not executed.
- File transfer and server functions are simulated.

---

## 🔗 Related Project

- **SpecterPanel (C2 Server)**  
  The command‑and‑control server that manages PhantomGate agents.  
  [https://github.com/omerKkemal/oh-tool-v2](https://github.com/omerKkemal/oh-tool-v2)

---

## ⚠️ Security & Ethics Notice

PhantomGate is a **powerful tool** capable of remote command and code execution, network flooding, and credential brute‑forcing.  

- **Intended Use:** Authorized penetration testing, red team exercises, and security education in isolated lab environments.
- **Prohibited Use:** Any unauthorized access to systems, networks, or data without explicit permission.  
- **Legal Compliance:** You must comply with all local, national, and international laws. Unauthorized use may lead to severe criminal and civil penalties.

The author, contributors, and any affiliated entities **do not condone illegal activity** and are **not responsible** for misuse. By using this software, you agree to use it **only for lawful purposes** and accept full responsibility for your actions.

---

## 🤝 Contributing

Contributions that improve the framework, add new lab scenarios, or fix bugs are welcome.  
Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

**For educational and authorized research use only.**  
No license is granted for malicious or unauthorized applications. Redistribution or commercial use without explicit permission is prohibited.

---

## ✍️ Author

**Omer Kemal**  
- C2 Server: [SpecterPanel](https://github.com/omerKkemal/oh-tool-v2)  
- Agent: PhantomGate  

For questions, feedback, or responsible disclosure, please open an issue on GitHub.

---
