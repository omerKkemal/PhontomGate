# PhantomGate — Multi-Purpose Remote Administration & Botnet Simulation Framework

**PhantomGate** is a cross-platform, modular remote administration tool (RAT) and botnet simulation agent, developed specifically for ethical red teaming, security research, and controlled command-and-control (C2) demonstrations. In conjunction with **SpecterPanel** (the C2 server), PhantomGate provides a modern, extensible framework for understanding and simulating advanced C2 and botnet operations in a secure, lab-friendly environment.

> **DISCLAIMER:**  
> This project is intended solely for educational purposes and authorized research. Any unauthorized use, deployment, or distribution is strictly prohibited and may be illegal and unethical.

---

## ⚙️ Key Features

- **Dynamic C2 Integration:**  
  Seamlessly connects with SpecterPanel or retrieves control parameters from public sources (e.g., Google Drive), enabling flexible agent management.

- **Remote Command Execution:**  
  Securely executes shell commands on remote hosts and reports results to the C2 server.

- **Advanced Code Injection:**  
  Downloads and executes Python payloads from SpecterPanel, enabling sophisticated red team simulations.

- **Terminal-Web Bridge:**  
  Provides live remote control by linking the local terminal with the web-based SpecterPanel C2 interface.

- **Botnet Simulation Suite:**  
  Supports UDP flood testing, SSH brute-force attacks, and customizable botnet actions—all controlled remotely.

- **Safe Mode:**  
  Offers a non-destructive simulation mode for lab exercises and training scenarios.

- **Persistent SQLite Tracking:**  
  Registers agents and maintains persistent state using SQLite for reliable agent management.

- **Cross-Platform Compatibility:**  
  Operates on Windows, Linux, and Android, with adaptive system detection.

- **Optional Kivy GUI:**  
  Includes a mobile-style graphical interface for local management and live agent status monitoring.

---

## 🕸️ Operational Workflow

1. **Agent Registration:**  
   Upon launch, PhantomGate registers with SpecterPanel and stores target metadata locally.

2. **Dynamic Instruction Polling:**  
   Agents poll the C2 (SpecterPanel or public control page) for updated parameters, instructions, and payloads.

3. **Task Execution:**  
   Shell commands and injected code are executed on the agent; results are securely transmitted to the C2 server.

4. **Botnet Actions:**  
   Agents may be instructed to perform UDP flood tests, brute-force attacks, or other botnet activities. Safe Mode ensures actions are simulated for demonstrations.

5. **Reporting & Output:**  
   All command results, code outputs, and task statuses are reported to SpecterPanel.

---

## 🔑 API Endpoints (SpecterPanel)

Default C2 API: `http://127.0.0.1:5000` (or via your ngrok tunnel)

**Core endpoints:**

- `/api/registor_target` — Register a new agent
- `/api/ApiCommand/<target>` — Retrieve remote shell commands
- `/api/Apicommand/save_output` — Submit command execution output
- `/api/BotNet/<target>` — Fetch botnet instructions (UDP flood, brute force)
- `/api/get_instraction/<target>` — Obtain high-level operational instructions
- `/api/injection/<target>` — Retrieve Python payloads for remote code execution

---

## 🚀 Getting Started

```bash
python PhantomGate.py
```
- Automatically registers with SpecterPanel
- Begins polling for instructions from the control source or API
- Executes received tasks and reports results securely

---

## 📂 Related Projects

- **SpecterPanel (C2 Server):**  
  [https://github.com/omerKkemal/oh-tool-v2](https://github.com/omerKkemal/oh-tool-v2)

---

## ⚠️ Security & Ethics Notice

PhantomGate is a powerful tool capable of remote command and code execution.  
**Use exclusively for lab environments, ethical hacking education, or authorized penetration testing.**  
The author assumes no responsibility for misuse.  
Unauthorized use may result in serious legal consequences.

---

## 🤝 Contributing

Contributions for enhancements, bug fixes, or new lab scenarios are welcome.  
Please open an issue or submit a pull request to participate.

---

## 📜 License

**For educational and authorized research use only.**  
No license is granted for malicious or unauthorized applications.

---

## ✍️ Author

**Omer Kemal**  
- C2 Server: SpecterPanel  
- Agent: PhantomGate
