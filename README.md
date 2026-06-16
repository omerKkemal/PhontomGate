# PhantomGate – yet another RAT for "educational purposes" (wink wink)

<p align="center">
  <img src="https://img.shields.io/badge/PHANTOMGATE-MULTI--PURPOSE%20RAT-10b981?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e" alt="PhantomGate">
</p>

Yeah, it's a remote admin tool. And yes, it can be used as a botnet client.  
But before you get any funny ideas (like actually using it on real people), read the warning below.

---

## ⚠️ Don't be an idiot (seriously)

This is for **educational use, authorised red teams, and your own lab only**.  
If you run this on someone's machine without permission, you're breaking the law.  
I'm not your lawyer, and I'm not responsible for your stupidity.

You've been warned. Twice now. Read it again if you need to.

---

## So what does it do? (as if you couldn't guess)

PhantomGate is the agent side of the SpecterPanel C2.  
It runs on Windows, Linux, and even Android (Termux – because why not), and talks to the C2 server using AES‑256 encryption.

You can:
- Execute shell commands remotely (groundbreaking)
- Inject Python code on the fly (so hacker)
- Simulate botnet behaviour (UDP floods, SSH brute force – in safe mode if you're not a complete moron)
- Gather system info (because you're nosy)
- Run as a background service or with a Kivy GUI (for the button-pushers)

It's not magic – it's just Python. Calm down.

---

## How it talks to the C2 (because you probably don't care)

```mermaid
graph LR
    A[SpecterPanel C2] -->|AES-256 Encrypted API| B[PhantomGate Agent]
    B --> C[Remote Command Execution]
    B --> D[Code Injection]
    B --> E[Botnet Simulation]
    B --> F[System Information Gathering]
    
    style A fill:#4f46e5,stroke:#fff,stroke-width:2px,color:#fff
    style B fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff
```

Agent polls the server every few seconds, gets instructions, runs them, sends back the output.  
Nothing fancy. It's not AI. It's not blockchain. It's just sockets.

---

## Main features (or "things it does")

| Module | What it actually does |
|--------|----------------------|
| C2 integration | Connects to SpecterPanel – no need to reinvent the wheel (again) |
| Remote shell | Run any command on the target, get output back (revolutionary) |
| Code injection | Download and execute Python payloads from the C2 (because why not) |
| Botnet simulation | UDP flood, SSH brute‑force (simulated unless you disable safe mode – don't be stupid) |
| Safe mode | No real damage – just logs what *would* happen (for the responsible adults) |
| SQLite tracking | Keeps state locally so you don't lose history (you're welcome) |
| Cross‑platform | Windows, Linux, Android – same code, same bugs |
| Kivy GUI | Optional pretty interface for people who don't like terminals |

---

## Architecture (the messy diagram that nobody asked for)

```
                ┌────────────────────────────────────────────────────────┐
                │                   PHANTOMGATE AGENT                    │
                ├────────────────────────────────────────────────────────┤
                │  ┌─────────────────┐      ┌─────────────────────────┐  │
                │  │  C2 Comms       │      │  Command Engine         │  │
                │  │  • Polling      │      │  • Shell execution      │  │
                │  │  • AES encrypt  │◄────►│  • Built‑ins            │  │
                │  │  • Register     │      │  • Output handling      │  │
                │  └─────────────────┘      └─────────────────────────┘  │
                │           ▲                            ▲               │
                │           └──────────┬─────────────────┘               │
                │                      ▼                                 │
                │  ┌─────────────────┐      ┌─────────────────────────┐  │
                │  │  Code Injection │      │  Botnet Engine          │  │
                │  │  • Payload fetch│      │  • UDP flood            │  │
                │  │  • Dynamic exec │      │  • SSH brute            │  │
                │  │  • Output report│      │  • Thread mgmt          │  │
                │  └─────────────────┘      └─────────────────────────┘  │
                │                      │                                 │
                │                   ┌──┴──┐                              │
                │                   │ DB  │                              │
                │                   └─────┘                              │
                │                      │                                 │
                │         ┌────────────┴─────────────┐                   │
                │         │ Headless mode │ GUI mode │                   │
                │         └───────────────┴──────────┘                   │
                └────────────────────────────────────────────────────────┘
                                               │
                                        AES‑256
                                           │
                                    ┌──────▼──────┐
                                    │ SpecterPanel│
                                    └─────────────┘
```

Yes, I know the diagram is a bit extra. It's still useful. Stop complaining.

---

## Getting it running (without setting your computer on fire)

```bash
git clone https://github.com/omerKkemal/PhantomGate.git
cd PhantomGate

python3 -m venv venv
source venv/bin/activate   # or .\venv\Scripts\activate on Windows

pip install -r requirements.txt

# Edit setting.py – set your C2 URL and API token
nano setting.py

# Run headless
python PhantomGate.py

# Or with GUI
python main.py
```

### Quick install scripts (if you're lazy)

- Linux/macOS: `chmod +x install.sh && ./install.sh`
- Windows: just double‑click `install.bat` (like a real pro)

---

## Configuration – setting.py explained (read it or cry later)

You only need to touch a few things. Here's the important stuff:

```python
class Setting:
    def __init__(self):
        # CHANGE THIS – 16 bytes, keep it secret. Seriously.
        self.ENCRYPTION_KEY = b'your-16-byte-key-here'
        
        # Where's your SpecterPanel? (don't use localhost for real ops, genius)
        self.url = 'http://127.0.0.1:5000'
        # API token from SpecterPanel settings (get it yourself)
        self.API_TOKEN = 'your-api-token-here'
        
        # UDP flood targets (ports) – because you'll totally use this
        self.PORT = [80, 443, 8080, 22, 3389, 53, 123]
        
        # How often to poll the C2 (seconds) – don't set it too low, idiot
        self.MAIN_LOOP_DELAY = 5
        
        # Safe mode – set to True if you don't want to break things
        # self.SAFE_MODE = True   # uncomment this, you coward
```

Most of the other knobs you can leave alone unless you're tweaking performance – which you probably shouldn't.

---

## How to use it (finally)

### Headless (background agent)

```bash
python PhantomGate.py
# or as a daemon on Linux:
nohup python PhantomGate.py &
# because you're too cool for tmux
```

### GUI mode

```bash
python main.py
```

From the GUI you can:
- Add / remove targets in the local DB (wow)
- Watch command history (thrilling)
- Start / stop botnet threads (like a real hacker)
- Browse the SQLite database (because you're a "data analyst" now)

### Commands you can send from the C2 (the part you'll actually use)

| Command | What it does (badly) | Example |
|---------|----------------------|---------|
| `sys_info` | Gather OS, hardware, IP (stalking 101) | `sys_info` |
| `db_info` | Show local DB stats (how exciting) | `db_info` |
| `bot start udp` | Start UDP flood (task id `udp_1`) – don't say I didn't warn you | `bot start udp_1` |
| `bot start brut` | Start SSH brute‑force (so original) | `bot start brut_1` |
| `bot stop <id>` | Stop a thread (because you changed your mind) | `bot stop udp_1` |
| `shell <cmd>` | Run any shell command (the actual useful one) | `shell ls -la` |
| `code exec <name>` | Run an injected payload (for the script kiddies) | `code exec keylogger` |

---

## API endpoints (for the nerds)

The agent calls these on the SpecterPanel server. All traffic is encrypted with AES‑256‑EAX.  
If you send plaintext, the server will ignore you. As it should.

| Endpoint | Method | When |
|----------|--------|------|
| `/api/v1.2/register_target` | POST | Once at start |
| `/api/v1.2/ApiCommand/<target>` | GET | Every poll |
| `/api/v1.2/Apicommand/save_output` | POST | After each command |
| `/api/v1.2/BotNet/<target>` | GET | Every poll |
| `/api/v1.2/get_instruction/<target>` | GET | Every poll |
| `/api/v1.2/injection/<target>` | GET | When a payload is requested |
| `/api/v1.2/injection_output_save` | POST | After injection |

The encrypted wrapper looks like this (because you need a visual):

```json
{
    "nonce": "base64...",
    "ciphertext": "base64...",
    "tag": "base64..."
}
```

Read it. Learn it. Love it.

---

## Safe mode – for the responsible adults

Enable safe mode, and the agent will log what it *would* do without actually doing it.  
It's like a "dry run" for people who don't want to go to jail.

### How to enable

```bash
# environment variable (if you hate editing files)
export PHANTOMGATE_SAFE_MODE=1
python PhantomGate.py

# or command line (for the fancy people)
python PhantomGate.py --safe-mode

# or just set SAFE_MODE = True in the code (if you're not scared)
```

### What changes (because you'll ask anyway)

| Action | Normal mode | Safe mode |
|--------|-------------|-----------|
| UDP flood | Actually sends packets (bad) | Logs "would send X packets" (good) |
| SSH brute | Real login attempts (illegal) | Simulates attempts, no network (legal) |
| File writes | Creates/modifies files (risky) | Logs the operation (safe) |
| Registry changes | Writes to registry (oops) | Read‑only, logs changes (whew) |
| Persistence | Installs startup entries (annoying) | Logs what would be installed (polite) |

Example safe mode log (so you can sleep at night):

```
[SAFE MODE] UDP flood prevented: would send 1000 packets to 192.168.1.100:80
[SAFE MODE] File write prevented: would create C:\temp\output.txt
```

Use it in labs. Don't be a hero. Nobody likes a hero.

---

## Where does it run? (spoiler: almost everywhere)

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 10/11, Server | ✅ Full | cmd, PowerShell, registry persistence (the usual) |
| Linux (Ubuntu, Debian, CentOS) | ✅ Full | bash, crontab, daemon mode (so stealthy) |
| Android (Termux) | ✅ Full | Limited shell, but hey, it works |

The agent auto‑detects the OS and adjusts accordingly.  
Because even I don't want to maintain three separate codebases.

---

## Related project – SpecterPanel C2 (the other half)

This agent is meant to work with **SpecterPanel**, the web‑based C2 server.

- **SpecterPanel** repo: [https://github.com/omerKkemal/oh-tool-v2](https://github.com/omerKkemal/oh-tool-v2)
- It gives you a dashboard, web terminal, code injection UI, and botnet manager.

Together they make a decent C2 stack for red team practice.  
Or for pretending you're a real hacker. Your call.

---

## One more legal thing (because the lawyers made me)

You are allowed to use PhantomGate **only** for:

- Authorised penetration tests (with written permission – yes, actually)
- Red team exercises in a controlled environment (not your grandma's PC)
- Security research in an isolated lab (not the office network)
- Learning how C2 frameworks work (because you're here to learn, right?)

You are **not allowed** to:

- Use it on any system you don't own or have explicit permission to test (obviously)
- Use it for criminal activity (really?)
- Distribute modified versions for malicious purposes (don't be that guy)

I've done my part by warning you. The rest is on you.  
Don't make me come over there.

---

## Contributing (you're not going to anyway)

Found a bug? Want to add a cool feature? Go ahead.

1. Fork the repo (you know how)
2. Create a branch (`git checkout -b feature/awesome`)
3. Commit your changes (try to make them work)
4. Push and open a PR (I'll probably merge it)

Please don't send PRs that remove the safe mode or add truly destructive features – that's not what this project is for.  
This is for learning, not for being a jerk.

---

## License

**Educational and authorised research use only** – no commercial license implied.

Copyright © 2024 Omer Kemal.  
No warranty, no liability. If you break it, you keep both pieces.  
If you break the law, you keep the consequences too.

---

## Author

**Omer Kemal** – security researcher who codes at 3am and regrets it at 9am.

- C2 server: [SpecterPanel](https://github.com/omerKkemal/oh-tool-v2)
- Agent: [PhantomGate](https://github.com/omerKkemal/PhontomGate)

Questions? Open an issue. Rude comments? Go touch grass.  
Actually, just go outside. It's nice out there.

---

<p align="center">
  <sub>© 2024 PhantomGate – for learning, not for being a jerk. Seriously. Don't be a jerk.</sub>
</p>
