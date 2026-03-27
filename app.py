#!/usr/bin/env python3
"""
Kali Control Hub - V2
Hub desktop tkinter pour vérifier, installer et lancer des outils sur Kali Linux.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ModuleNotFoundError:
    print(
        "[ERROR] tkinter est introuvable. Installez le paquet système python3-tk puis relancez Kali Control Hub.",
        file=sys.stderr,
    )
    sys.exit(1)


@dataclass(frozen=True)
class CLIHelp:
    """Aide courte affichee dans le terminal pour un outil CLI."""

    title: str
    description: str
    examples: Tuple[str, ...]


@dataclass(frozen=True)
class Tool:
    """Définition d'un outil géré par le hub."""

    name: str
    check_cmd: str
    launch_cmd: str
    install_cmd: str
    category: str
    tool_type: str  # "gui" ou "cli"
    cli_mode: str = "terminal"
    cli_help: Optional[CLIHelp] = None
    special_install_handler: Optional[str] = None


NMAP_HELP = CLIHelp(
    title="Aide rapide Nmap",
    description="Nmap sert a scanner des hotes et des services reseau.",
    examples=(
        "nmap 127.0.0.1",
        "nmap -A 192.168.1.1",
        "nmap -sV 192.168.1.10",
    ),
)

GIT_HELP = CLIHelp(
    title="Aide rapide Git",
    description="Git sert a versionner le code et suivre les changements.",
    examples=(
        "git status",
        "git init",
        "git clone <url>",
        "git pull",
        "git add .",
        "git commit -m \"message\"",
    ),
)

PYTHON_HELP = CLIHelp(
    title="Aide rapide Python 3",
    description="Python3 permet d'executer des scripts et outils Python.",
    examples=(
        "python3",
        "python3 script.py",
        "python3 -m venv venv",
    ),
)

NODE_HELP = CLIHelp(
    title="Aide rapide Node.js",
    description="Node.js permet d'executer du JavaScript cote systeme.",
    examples=(
        "node",
        "node app.js",
        "npm install",
    ),
)

CODEX_HELP = CLIHelp(
    title="Aide rapide Codex CLI",
    description="Codex CLI aide a analyser et modifier du code en terminal.",
    examples=(
        "codex",
        "codex \"explique ce depot\"",
        "/model",
        "/fast",
    ),
)


TOOLS: List[Tool] = [
    # SYSTEM
    Tool(
        name="fastfetch",
        check_cmd="which fastfetch",
        launch_cmd="fastfetch",
        install_cmd="sudo apt install fastfetch -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="htop",
        check_cmd="which htop",
        launch_cmd="htop",
        install_cmd="sudo apt install htop -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="btop",
        check_cmd="which btop",
        launch_cmd="btop",
        install_cmd="sudo apt install btop -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="curl",
        check_cmd="which curl",
        launch_cmd="curl",
        install_cmd="sudo apt install curl -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="wget",
        check_cmd="which wget",
        launch_cmd="wget",
        install_cmd="sudo apt install wget -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="unzip",
        check_cmd="which unzip",
        launch_cmd="unzip",
        install_cmd="sudo apt install unzip -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="zip",
        check_cmd="which zip",
        launch_cmd="zip",
        install_cmd="sudo apt install zip -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="jq",
        check_cmd="which jq",
        launch_cmd="jq",
        install_cmd="sudo apt install jq -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="tree",
        check_cmd="which tree",
        launch_cmd="tree",
        install_cmd="sudo apt install tree -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="net-tools",
        check_cmd="which ifconfig",
        launch_cmd="ifconfig",
        install_cmd="sudo apt install net-tools -y",
        category="system",
        tool_type="cli",
        cli_mode="terminal",
    ),
    # DEV
    Tool(
        name="git",
        check_cmd="which git",
        launch_cmd="git",
        install_cmd="sudo apt install git -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
        cli_help=GIT_HELP,
    ),
    Tool(
        name="python3",
        check_cmd="which python3",
        launch_cmd="python3",
        install_cmd="sudo apt install python3 -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
        cli_help=PYTHON_HELP,
    ),
    Tool(
        name="nodejs",
        check_cmd="which node",
        launch_cmd="node",
        install_cmd="sudo apt install nodejs npm -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
        cli_help=NODE_HELP,
    ),
    Tool(
        name="codex",
        check_cmd="which codex",
        launch_cmd="codex",
        install_cmd="sudo npm install -g @openai/codex",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
        cli_help=CODEX_HELP,
    ),
    Tool(
        name="pipx",
        check_cmd="which pipx",
        launch_cmd="pipx",
        install_cmd="sudo apt install pipx -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="micro",
        check_cmd="which micro",
        launch_cmd="micro",
        install_cmd="sudo apt install micro -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="vim",
        check_cmd="which vim",
        launch_cmd="vim",
        install_cmd="sudo apt install vim -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="tmux",
        check_cmd="which tmux",
        launch_cmd="tmux",
        install_cmd="sudo apt install tmux -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="docker.io",
        check_cmd="which docker",
        launch_cmd="docker",
        install_cmd="sudo apt install docker.io -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="docker-compose-plugin",
        check_cmd="docker compose version >/dev/null 2>&1",
        launch_cmd="docker compose version",
        install_cmd="sudo apt install docker-compose-plugin -y",
        category="dev",
        tool_type="cli",
        cli_mode="terminal",
    ),
    # CYBER
    Tool(
        name="nmap",
        check_cmd="which nmap",
        launch_cmd="nmap",
        install_cmd="sudo apt install nmap -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
        cli_help=NMAP_HELP,
    ),
    Tool(
        name="wireshark",
        check_cmd="which wireshark",
        launch_cmd="wireshark",
        install_cmd="sudo apt install wireshark -y",
        category="cyber",
        tool_type="gui",
    ),
    Tool(
        name="torbrowser-launcher",
        check_cmd="which torbrowser-launcher",
        launch_cmd="torbrowser-launcher",
        install_cmd="sudo apt install torbrowser-launcher -y",
        category="cyber",
        tool_type="gui",
    ),
    Tool(
        name="tcpdump",
        check_cmd="which tcpdump",
        launch_cmd="tcpdump",
        install_cmd="sudo apt install tcpdump -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="whois",
        check_cmd="which whois",
        launch_cmd="whois",
        install_cmd="sudo apt install whois -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="dnsutils",
        check_cmd="which dig",
        launch_cmd="dig",
        install_cmd="sudo apt install dnsutils -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="traceroute",
        check_cmd="which traceroute",
        launch_cmd="traceroute",
        install_cmd="sudo apt install traceroute -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="nikto",
        check_cmd="which nikto",
        launch_cmd="nikto",
        install_cmd="sudo apt install nikto -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="gobuster",
        check_cmd="which gobuster",
        launch_cmd="gobuster",
        install_cmd="sudo apt install gobuster -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    Tool(
        name="ffuf",
        check_cmd="which ffuf",
        launch_cmd="ffuf",
        install_cmd="sudo apt install ffuf -y",
        category="cyber",
        tool_type="cli",
        cli_mode="terminal",
    ),
    # APPS
    Tool(
        name="firefox",
        check_cmd="which firefox",
        launch_cmd="firefox",
        install_cmd="sudo apt install firefox-esr -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="vlc",
        check_cmd="which vlc",
        launch_cmd="vlc",
        install_cmd="sudo apt install vlc -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="spotify",
        check_cmd="flatpak list | grep -i com.spotify.Client",
        launch_cmd="flatpak run com.spotify.Client",
        install_cmd="flatpak install flathub com.spotify.Client -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="proton-pass",
        check_cmd="which proton-pass || flatpak list | grep -i me.proton.Pass",
        launch_cmd="proton-pass || flatpak run me.proton.Pass",
        install_cmd="",
        category="apps",
        tool_type="gui",
        special_install_handler="proton_pass",
    ),
    Tool(
        name="proton-vpn",
        check_cmd="which protonvpn",
        launch_cmd="protonvpn",
        install_cmd="",
        category="apps",
        tool_type="cli",
        special_install_handler="proton_vpn",
    ),
    Tool(
        name="thunderbird",
        check_cmd="which thunderbird",
        launch_cmd="thunderbird",
        install_cmd="sudo apt install thunderbird -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="libreoffice",
        check_cmd="which libreoffice",
        launch_cmd="libreoffice",
        install_cmd="sudo apt install libreoffice -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="gimp",
        check_cmd="which gimp",
        launch_cmd="gimp",
        install_cmd="sudo apt install gimp -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="obs-studio",
        check_cmd="which obs",
        launch_cmd="obs",
        install_cmd="sudo apt install obs-studio -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="qbittorrent",
        check_cmd="which qbittorrent",
        launch_cmd="qbittorrent",
        install_cmd="sudo apt install qbittorrent -y",
        category="apps",
        tool_type="gui",
    ),
    Tool(
        name="keepassxc",
        check_cmd="which keepassxc",
        launch_cmd="keepassxc",
        install_cmd="sudo apt install keepassxc -y",
        category="apps",
        tool_type="gui",
    ),
]


class ToolManager:
    """Logique système: vérification, installation, lancement."""

    def __init__(self, tools: List[Tool]):
        self.tools = tools

    @staticmethod
    def build_command(base_cmd: str, extra_args: str = "") -> str:
        args = extra_args.strip()
        return f"{base_cmd} {args}".strip() if args else base_cmd

    @staticmethod
    def _run_command(command: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
        )

    @staticmethod
    def _run_command_stream(
        command: str,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> int:
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )

        if process.stdout:
            for line in process.stdout:
                clean = line.rstrip()
                if clean and on_output:
                    on_output(clean)

        return process.wait()

    def is_installed(self, tool: Tool) -> bool:
        try:
            result = self._run_command(tool.check_cmd)
            return result.returncode == 0
        except Exception:
            return False

    def install_tool(
        self,
        tool: Tool,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> bool:
        try:
            return_code = self._run_command_stream(tool.install_cmd, on_output=on_output)
            return return_code == 0
        except Exception as exc:
            if on_output:
                on_output(f"Erreur pendant l'installation: {exc}")
            return False

    def run_cli_command(
        self,
        command: str,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> int:
        try:
            return self._run_command_stream(command, on_output=on_output)
        except Exception as exc:
            if on_output:
                on_output(f"Erreur pendant l'exécution CLI: {exc}")
            return -1

    @staticmethod
    def launch_detached(command: str) -> bool:
        try:
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except Exception:
            return False

    def launch_tool(self, tool: Tool, extra_args: str = "") -> bool:
        """Compatibilité V1: utilisé ici pour les outils GUI."""
        command = self.build_command(tool.launch_cmd, extra_args)
        return self.launch_detached(command)

    @staticmethod
    def _build_terminal_payload(command: Optional[str] = None) -> str:
        if command:
            return (
                f"{command}; echo; "
                "echo '[Kali Control Hub] Commande terminée.'; "
                "exec bash"
            )
        return "exec bash"

    def get_terminal_command(self, command: Optional[str] = None) -> Optional[List[str]]:
        payload = self._build_terminal_payload(command)
        candidates: List[List[str]] = [
            ["xfce4-terminal", "--command", f"bash -lc {shlex.quote(payload)}"],
            ["x-terminal-emulator", "-e", "bash", "-lc", payload],
            ["exo-open", "--launch", "TerminalEmulator", "bash", "-lc", payload],
        ]

        for terminal_cmd in candidates:
            if shutil.which(terminal_cmd[0]):
                return terminal_cmd
        return None

    def open_cli_in_terminal(self, command: Optional[str] = None) -> bool:
        terminal_cmd = self.get_terminal_command(command)
        if not terminal_cmd:
            return False
        try:
            subprocess.Popen(
                terminal_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        except Exception:
            return False

    def open_terminal(self, command: Optional[str] = None) -> bool:
        """Compatibilité API existante côté UI."""
        return self.open_cli_in_terminal(command)


@dataclass
class ToolRow:
    """Widgets associés à un outil pour mise à jour rapide."""

    status_label: ttk.Label
    install_button: ttk.Button
    launch_button: ttk.Button
    args_var: Optional[tk.StringVar] = None


class App(tk.Tk):
    """UI principale Kali Control Hub."""

    def __init__(self, manager: ToolManager):
        super().__init__()
        self.manager = manager
        self.title("Kali Control Hub")
        self.geometry("1100x760")
        self.minsize(960, 620)

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "row": "#1f2937",
            "text": "#e5e7eb",
            "muted": "#94a3b8",
            "button": "#334155",
            "button_active": "#475569",
            "input_bg": "#0b1220",
            "installed": "#22c55e",
            "missing": "#f97316",
            "pending": "#fbbf24",
            "console_bg": "#030712",
            "console_fg": "#d1d5db",
        }

        self.configure(bg=self.colors["bg"])

        self._rows: Dict[Tool, ToolRow] = {}
        self._tools_by_category = self._group_tools_by_category(self.manager.tools)
        self.console_text: Optional[tk.Text] = None

        self._build_style()
        self._build_ui()
        self.log("Kali Control Hub prêt.", "ok")
        self.refresh_all_statuses()

    @staticmethod
    def _group_tools_by_category(tools: List[Tool]) -> Dict[str, List[Tool]]:
        categories: Dict[str, List[Tool]] = {}
        for tool in tools:
            categories.setdefault(tool.category, []).append(tool)
        return categories

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("App.TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["panel"])
        style.configure("Row.TFrame", background=self.colors["row"])

        style.configure("TLabel", background=self.colors["panel"], foreground=self.colors["text"])
        style.configure("Title.TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("Title.TLabel", font=("TkDefaultFont", 13, "bold"))
        style.configure(
            "CategoryHeader.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("TkDefaultFont", 10, "bold"),
        )
        style.configure(
            "CategoryHeaderCenter.TLabel",
            background=self.colors["panel"],
            foreground=self.colors["muted"],
            font=("TkDefaultFont", 10, "bold"),
            anchor="center",
        )
        style.configure("Row.TLabel", background=self.colors["row"], foreground=self.colors["text"])
        style.configure("RowMuted.TLabel", background=self.colors["row"], foreground=self.colors["muted"])

        style.configure(
            "TButton",
            background=self.colors["button"],
            foreground=self.colors["text"],
            borderwidth=0,
            padding=(10, 6),
            focuscolor=self.colors["button"],
        )
        style.map(
            "TButton",
            background=[
                ("active", self.colors["button_active"]),
                ("disabled", "#1e293b"),
            ],
            foreground=[("disabled", "#64748b")],
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors["input_bg"],
            foreground=self.colors["text"],
            borderwidth=0,
        )

        style.configure(
            "Hub.TNotebook",
            background=self.colors["panel"],
            borderwidth=0,
            relief="flat",
            tabmargins=(0, 0, 0, 0),
            padding=0,
            highlightthickness=0,
            lightcolor=self.colors["panel"],
            darkcolor=self.colors["panel"],
            bordercolor=self.colors["panel"],
        )
        style.configure(
            "Hub.TNotebook.Tab",
            background="#1f2937",
            foreground=self.colors["muted"],
            padding=(18, 9),
            borderwidth=0,
            relief="flat",
            focuscolor=self.colors["panel"],
            lightcolor="#1f2937",
            darkcolor="#1f2937",
            bordercolor="#1f2937",
            highlightthickness=0,
        )
        style.map(
            "Hub.TNotebook.Tab",
            background=[
                ("selected", "#334155"),
                ("active", "#1f2937"),
                ("!selected", "#1f2937"),
            ],
            foreground=[
                ("selected", "#f8fafc"),
                ("active", self.colors["muted"]),
                ("!selected", self.colors["muted"]),
            ],
            padding=[
                ("selected", (18, 9)),
                ("active", (18, 9)),
                ("!selected", (18, 9)),
            ],
            expand=[
                ("selected", (0, 0, 0, 0)),
                ("active", (0, 0, 0, 0)),
                ("!selected", (0, 0, 0, 0)),
            ],
            lightcolor=[
                ("selected", "#334155"),
                ("active", "#1f2937"),
                ("!selected", "#1f2937"),
            ],
            darkcolor=[
                ("selected", "#334155"),
                ("active", "#1f2937"),
                ("!selected", "#1f2937"),
            ],
            bordercolor=[
                ("selected", "#334155"),
                ("active", "#1f2937"),
                ("!selected", "#1f2937"),
            ],
        )
        # Supprime explicitement l'element de focus du tab pour eviter le contour noir.
        style.layout(
            "Hub.TNotebook.Tab",
            [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [("Notebook.label", {"sticky": ""})],
                                },
                            )
                        ],
                    },
                )
            ],
        )

        style.configure(
            "Dark.Vertical.TScrollbar",
            background="#334155",
            troughcolor="#111827",
            arrowcolor="#cbd5e1",
            bordercolor="#111827",
            lightcolor="#111827",
            darkcolor="#111827",
            gripcount=0,
            relief="flat",
        )
        style.map(
            "Dark.Vertical.TScrollbar",
            background=[("active", "#475569"), ("pressed", "#64748b")],
            arrowcolor=[("disabled", "#475569")],
        )

        style.configure("StatusInstalled.TLabel", background=self.colors["row"], foreground=self.colors["installed"])
        style.configure("StatusMissing.TLabel", background=self.colors["row"], foreground=self.colors["missing"])
        style.configure("StatusPending.TLabel", background=self.colors["row"], foreground=self.colors["pending"])
        style.configure("StatusInstalled.TLabel", anchor="center")
        style.configure("StatusMissing.TLabel", anchor="center")
        style.configure("StatusPending.TLabel", anchor="center")

    def _build_ui(self) -> None:
        root = ttk.Frame(self, style="App.TFrame", padding=10)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)

        top_bar = ttk.Frame(root, style="App.TFrame")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_bar.columnconfigure(0, weight=1)

        title = ttk.Label(top_bar, text="Kali Control Hub", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")

        actions = ttk.Frame(top_bar, style="App.TFrame")
        actions.grid(row=0, column=1, sticky="e")

        refresh_btn = ttk.Button(actions, text="Refresh", command=self.refresh_all_statuses, takefocus=False)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 6))

        clear_btn = ttk.Button(actions, text="Effacer la console", command=self.clear_console, takefocus=False)
        clear_btn.pack(side=tk.LEFT, padx=(0, 6))

        terminal_btn = ttk.Button(actions, text="Ouvrir un terminal", command=self.open_terminal, takefocus=False)
        terminal_btn.pack(side=tk.LEFT)

        content = ttk.Frame(root, style="App.TFrame")
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=3)
        content.rowconfigure(1, weight=2)

        notebook_wrap = ttk.Frame(content, style="Card.TFrame", padding=6)
        notebook_wrap.grid(row=0, column=0, sticky="nsew")
        notebook_wrap.columnconfigure(0, weight=1)
        notebook_wrap.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(
            notebook_wrap,
            style="Hub.TNotebook",
            takefocus=False,
            padding=0,
        )
        notebook.pack(fill=tk.BOTH, expand=True)

        for category, tools in sorted(self._tools_by_category.items()):
            tab = ttk.Frame(notebook, style="Card.TFrame")
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
            notebook.add(tab, text=category.upper())
            self._build_category_tab(tab, tools)

        self._build_console(content)

    def _build_console(self, parent: ttk.Frame) -> None:
        console_wrap = ttk.Frame(parent, style="Card.TFrame", padding=8)
        console_wrap.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        console_wrap.columnconfigure(0, weight=1)
        console_wrap.rowconfigure(1, weight=1)

        header = ttk.Label(console_wrap, text="Console intégrée", style="CategoryHeader.TLabel")
        header.grid(row=0, column=0, sticky="w", pady=(0, 6))

        text_frame = ttk.Frame(console_wrap, style="Card.TFrame")
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.console_text = tk.Text(
            text_frame,
            height=12,
            bg=self.colors["console_bg"],
            fg=self.colors["console_fg"],
            insertbackground=self.colors["console_fg"],
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.WORD,
            font=("TkFixedFont", 10),
            state=tk.DISABLED,
            highlightthickness=0,
            takefocus=0,
        )
        self.console_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self.console_text.yview,
            style="Dark.Vertical.TScrollbar",
            takefocus=False,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.console_text.configure(yscrollcommand=scrollbar.set)

        self.console_text.tag_configure("INFO", foreground="#60a5fa")
        self.console_text.tag_configure("OK", foreground="#22c55e")
        self.console_text.tag_configure("ERREUR", foreground="#ef4444")
        self.console_text.tag_configure("CMD", foreground="#22d3ee")

    def _build_category_tab(self, parent: ttk.Frame, tools: List[Tool]) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            parent,
            highlightthickness=0,
            bg=self.colors["panel"],
            bd=0,
            takefocus=0,
        )
        scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=canvas.yview,
            style="Dark.Vertical.TScrollbar",
            takefocus=False,
        )
        scrollable = ttk.Frame(canvas, style="Card.TFrame", padding=8)
        scrollable.columnconfigure(0, weight=1)

        window_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_scrollable_configure(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        scrollable.bind("<Configure>", on_scrollable_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        def on_mousewheel(event: tk.Event) -> str:
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
                return "break"
            if getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")
                return "break"
            if getattr(event, "delta", 0):
                direction = -1 if event.delta > 0 else 1
                canvas.yview_scroll(direction, "units")
                return "break"
            return "break"

        def bind_mousewheel_recursive(widget: tk.Widget) -> None:
            widget.bind("<MouseWheel>", on_mousewheel, add="+")
            widget.bind("<Button-4>", on_mousewheel, add="+")
            widget.bind("<Button-5>", on_mousewheel, add="+")
            for child in widget.winfo_children():
                bind_mousewheel_recursive(child)

        table = ttk.Frame(scrollable, style="Card.TFrame")
        table.grid(row=0, column=0, sticky="ew")
        table.columnconfigure(0, weight=32, minsize=210, uniform="tools_cols")
        table.columnconfigure(1, weight=16, minsize=130, uniform="tools_cols")
        table.columnconfigure(2, weight=32, minsize=240, uniform="tools_cols")
        table.columnconfigure(3, weight=20, minsize=210, uniform="tools_cols")

        ttk.Label(table, text="Outil", style="CategoryHeader.TLabel").grid(
            row=0, column=0, sticky="ew", padx=(10, 8), pady=(2, 8)
        )
        ttk.Label(table, text="Statut", style="CategoryHeaderCenter.TLabel").grid(
            row=0, column=1, sticky="ew", padx=8, pady=(2, 8)
        )
        ttk.Label(table, text="Arguments CLI (optionnel)", style="CategoryHeader.TLabel").grid(
            row=0, column=2, sticky="ew", padx=8, pady=(2, 8)
        )
        ttk.Label(table, text="Actions", style="CategoryHeaderCenter.TLabel").grid(
            row=0, column=3, sticky="ew", padx=(8, 10), pady=(2, 8)
        )

        for index, tool in enumerate(tools, start=1):
            row_frame = ttk.Frame(table, style="Row.TFrame", padding=(8, 6))
            row_frame.grid(
                row=index,
                column=0,
                columnspan=4,
                sticky="ew",
                padx=2,
                pady=2,
            )
            row_frame.columnconfigure(0, weight=32, minsize=210, uniform="row_cols")
            row_frame.columnconfigure(1, weight=16, minsize=130, uniform="row_cols")
            row_frame.columnconfigure(2, weight=32, minsize=240, uniform="row_cols")
            row_frame.columnconfigure(3, weight=20, minsize=210, uniform="row_cols")
            row_frame.rowconfigure(0, minsize=34)

            ttk.Label(row_frame, text=tool.name, style="Row.TLabel").grid(
                row=0, column=0, sticky="w", padx=(6, 8), pady=2
            )

            status_label = ttk.Label(
                row_frame,
                text="Vérification...",
                style="StatusPending.TLabel",
                anchor="center",
                justify="center",
            )
            status_label.grid(row=0, column=1, sticky="ew", padx=8, pady=2)

            args_var: Optional[tk.StringVar] = None
            if tool.tool_type == "cli":
                args_var = tk.StringVar()
                args_entry = ttk.Entry(row_frame, textvariable=args_var, takefocus=True)
                args_entry.grid(row=0, column=2, sticky="ew", padx=8, pady=2, ipady=2)
            else:
                ttk.Label(row_frame, text="-", style="RowMuted.TLabel").grid(
                    row=0, column=2, sticky="w", padx=8, pady=2
                )

            action_frame = ttk.Frame(row_frame, style="Row.TFrame")
            action_frame.grid(row=0, column=3, sticky="e", padx=(8, 6), pady=2)

            install_btn = ttk.Button(
                action_frame,
                text="Installer",
                command=lambda t=tool: self.install_tool(t),
                takefocus=False,
            )
            install_btn.pack(side=tk.LEFT, padx=(0, 6))

            launch_btn = ttk.Button(
                action_frame,
                text="Lancer",
                command=lambda t=tool: self.launch_tool(t),
                takefocus=False,
            )
            launch_btn.pack(side=tk.LEFT)

            self._rows[tool] = ToolRow(
                status_label=status_label,
                install_button=install_btn,
                launch_button=launch_btn,
                args_var=args_var,
            )

        bind_mousewheel_recursive(canvas)
        bind_mousewheel_recursive(scrollable)

    def log(self, message: str, level: str = "info") -> None:
        clean = message.strip()
        if not clean:
            return
        self.after(0, self._append_log, clean, level.lower())

    def _append_log(self, message: str, level: str) -> None:
        if not self.console_text:
            return

        tag = "INFO"
        prefix = "[INFO]"
        if level == "ok":
            tag = "OK"
            prefix = "[OK]"
        elif level in {"error", "erreur"}:
            tag = "ERREUR"
            prefix = "[ERREUR]"
        elif level == "cmd":
            tag = "CMD"
            prefix = "[CMD]"

        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"{timestamp} {prefix} {message}\n"

        self.console_text.configure(state=tk.NORMAL)
        self.console_text.insert(tk.END, line, tag)
        self.console_text.configure(state=tk.DISABLED)
        self.console_text.see(tk.END)

    def clear_console(self) -> None:
        if not self.console_text:
            return
        self.console_text.configure(state=tk.NORMAL)
        self.console_text.delete("1.0", tk.END)
        self.console_text.configure(state=tk.DISABLED)
        self.log("Console effacée.", "info")

    def _set_tool_status(self, tool: Tool, installed: bool) -> None:
        row = self._rows[tool]
        if installed:
            row.status_label.configure(text="Installé", style="StatusInstalled.TLabel")
            row.launch_button.configure(state=tk.NORMAL)
            row.install_button.configure(state=tk.DISABLED)
        else:
            row.status_label.configure(text="Non installé", style="StatusMissing.TLabel")
            row.launch_button.configure(state=tk.DISABLED)
            row.install_button.configure(state=tk.NORMAL)

    def refresh_all_statuses(self) -> None:
        self.log("Rafraîchissement global des statuts...", "info")

        def worker() -> None:
            for tool in self.manager.tools:
                installed = self.manager.is_installed(tool)
                self.after(0, self._set_tool_status, tool, installed)
            self.log("Statuts mis à jour.", "ok")

        threading.Thread(target=worker, daemon=True).start()

    def refresh_single_status(self, tool: Tool) -> None:
        def worker() -> None:
            installed = self.manager.is_installed(tool)
            self.after(0, self._set_tool_status, tool, installed)

        threading.Thread(target=worker, daemon=True).start()

    def _install_tool_with_handler(
        self,
        tool: Tool,
        on_output: Callable[[str], None],
    ) -> bool:
        if tool.special_install_handler == "proton_pass":
            return self._install_proton_pass(on_output)
        if tool.special_install_handler == "proton_vpn":
            return self._install_proton_vpn(on_output)
        if not tool.install_cmd.strip():
            on_output("Aucune commande d'installation definie pour cet outil.")
            return False
        return self.manager.install_tool(tool, on_output=on_output)

    def _install_proton_pass(self, on_output: Callable[[str], None]) -> bool:
        on_output("Installation guidee Proton Pass.")
        on_output("Tentative 1/2: installation APT directe (proton-pass).")
        if self.manager.run_cli_command("sudo apt install proton-pass -y", on_output=on_output) == 0:
            return True

        on_output("Tentative 2/2: installation Flatpak (Flathub me.proton.Pass).")
        flatpak_cmd = (
            "if ! command -v flatpak >/dev/null 2>&1; then "
            "sudo apt install flatpak -y; "
            "fi && "
            "flatpak remote-add --if-not-exists flathub "
            "https://flathub.org/repo/flathub.flatpakrepo && "
            "flatpak install flathub me.proton.Pass -y"
        )
        if self.manager.run_cli_command(flatpak_cmd, on_output=on_output) == 0:
            return True

        on_output("Installation automatique de Proton Pass echouee.")
        on_output("Guide manuel conseille:")
        on_output("  1) Installer Flatpak: sudo apt install flatpak -y")
        on_output("  2) Ajouter Flathub: flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
        on_output("  3) Installer: flatpak install flathub me.proton.Pass -y")
        on_output("  4) Lancer: flatpak run me.proton.Pass")
        return False

    def _install_proton_vpn(self, on_output: Callable[[str], None]) -> bool:
        self.log("Installation Proton VPN CLI: demarrage.", "info")
        on_output("Installation guidee Proton VPN (priorite au CLI).")

        # Etape 1: garantir wget avant telechargement du paquet de depot.
        self.log("Proton VPN: verification de wget...", "info")
        on_output("Etape 1/6: verification de wget.")
        if self.manager.run_cli_command("which wget >/dev/null 2>&1") != 0:
            self.log("wget absent, installation automatique.", "info")
            on_output("wget absent, installation de wget via apt.")
            if self.manager.run_cli_command("sudo apt install wget -y", on_output=on_output) != 0:
                self.log("Echec de l'installation de wget.", "error")
                on_output("ERREUR: impossible d'installer wget.")
                return False
            self.log("wget installe.", "ok")
        else:
            on_output("wget deja installe.")

        deb_url = (
            "https://repo.protonvpn.com/debian/dists/stable/main/binary-all/"
            "protonvpn-stable-release_1.0.8_all.deb"
        )
        deb_path = "/tmp/protonvpn-stable-release_1.0.8_all.deb"
        steps = [
            (
                "Etape 2/6: telechargement du paquet de depot Proton VPN.",
                f"wget -O {deb_path} {deb_url}",
            ),
            (
                "Etape 3/6: installation du paquet de depot Proton VPN.",
                f"sudo dpkg -i {deb_path}",
            ),
            ("Etape 4/6: mise a jour des index APT.", "sudo apt update"),
            ("Etape 5/6: installation du CLI Proton VPN.", "sudo apt install proton-vpn-cli -y"),
        ]

        for step_label, step_cmd in steps:
            self.log(step_label, "info")
            on_output(step_label)
            if self.manager.run_cli_command(step_cmd, on_output=on_output) != 0:
                self.log(f"Echec: {step_label}", "error")
                on_output("Guide manuel conseille:")
                on_output(f"  1) wget {deb_url}")
                on_output("  2) sudo dpkg -i ./protonvpn-stable-release_1.0.8_all.deb")
                on_output("  3) sudo apt update")
                on_output("  4) sudo apt install proton-vpn-cli -y")
                on_output("  5) Lancer: protonvpn")
                on_output("Fallback GUI optionnel: sudo apt install proton-vpn-gnome-desktop -y")
                return False

        self.log("Etape 6/6: verification de protonvpn.", "info")
        on_output("Etape 6/6: verification de protonvpn.")
        if self.manager.run_cli_command("which protonvpn >/dev/null 2>&1") == 0:
            self.log("Proton VPN CLI installe.", "ok")
            on_output("[OK] protonvpn detecte et pret a etre lance.")
            return True

        self.log("Proton VPN CLI non detecte apres installation.", "error")
        on_output("ERREUR: protonvpn n'a pas ete detecte apres l'installation.")
        on_output("Guide manuel conseille:")
        on_output(f"  1) wget {deb_url}")
        on_output("  2) sudo dpkg -i ./protonvpn-stable-release_1.0.8_all.deb")
        on_output("  3) sudo apt update")
        on_output("  4) sudo apt install proton-vpn-cli -y")
        on_output("  5) Lancer: protonvpn")
        on_output("Fallback GUI optionnel: sudo apt install proton-vpn-gnome-desktop -y")
        return False

    def install_tool(self, tool: Tool) -> None:
        row = self._rows[tool]
        row.install_button.configure(state=tk.DISABLED)
        row.launch_button.configure(state=tk.DISABLED)
        row.status_label.configure(text="Installation...", style="StatusPending.TLabel")
        self.log(f"Installation de {tool.name}...", "info")

        def on_output(line: str) -> None:
            self.log(line, "cmd")

        def worker() -> None:
            ok = self._install_tool_with_handler(tool, on_output=on_output)
            self.after(0, self.refresh_single_status, tool)
            if ok:
                self.log(f"{tool.name} a été installé avec succès.", "ok")
            else:
                self.log(f"Échec de l'installation de {tool.name}.", "error")
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erreur d'installation",
                        f"Échec de l'installation de '{tool.name}'. "
                        "Consulte la console intégrée.",
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()

    def launch_tool(self, tool: Tool) -> None:
        installed = self.manager.is_installed(tool)
        if not installed:
            self._set_tool_status(tool, False)
            self.log(f"Impossible de lancer {tool.name}: outil non installé.", "error")
            messagebox.showwarning(
                "Outil non installé",
                f"'{tool.name}' n'est pas installé. Installe-le avant de lancer.",
            )
            return

        row = self._rows[tool]
        extra_args = row.args_var.get().strip() if row.args_var else ""

        if tool.tool_type == "gui":
            command = self.manager.build_command(tool.launch_cmd, extra_args)
            self.log(f"Lancement de {tool.name}...", "info")
            ok = self.manager.launch_tool(tool, extra_args=extra_args)
            if ok:
                self.log(f"{tool.name} est lancé.", "ok")
            else:
                self._notify_launch_error(tool.name)
            return

        command = self._resolve_cli_command(tool, extra_args)
        if not extra_args and tool.cli_help is not None:
            self.log(f"{tool.name} sans arguments: affichage d'une aide rapide.", "info")

        self.log(f"Lancement CLI dans un terminal: {command}", "info")
        ok = self.manager.open_terminal(command)
        if ok:
            self.log(f"{tool.name} ouvert dans un terminal.", "ok")
        else:
            self.log(
                "Impossible d'ouvrir un terminal (xfce4-terminal, x-terminal-emulator, exo-open).",
                "error",
            )
            messagebox.showerror(
                "Terminal introuvable",
                "Aucun terminal disponible. Essayés: xfce4-terminal, x-terminal-emulator, "
                "exo-open --launch TerminalEmulator.",
            )

    def _resolve_cli_command(self, tool: Tool, extra_args: str) -> str:
        args = extra_args.strip()
        if args:
            if tool.name == "nodejs" and (args.startswith("npm ") or args == "npm"):
                return args
            return self.manager.build_command(tool.launch_cmd, args)

        help_command = self._build_cli_help_command(tool)
        if help_command:
            return help_command
        return tool.launch_cmd

    def _build_cli_help_command(self, tool: Tool) -> Optional[str]:
        if tool.cli_help is None:
            return None
        return self._format_cli_help_script(
            title=tool.cli_help.title,
            description=tool.cli_help.description,
            examples=list(tool.cli_help.examples),
            tool_name=tool.name,
        )

    @staticmethod
    def _format_cli_help_script(
        title: str,
        description: str,
        examples: List[str],
        tool_name: str,
    ) -> str:
        lines = [
            f"=== {title} (Kali Control Hub) ===",
            description,
            "",
            "Exemples utiles :",
            *[f"  {example}" for example in examples],
            "",
            f"Astuce: ajoute des arguments pour '{tool_name}' dans l'application puis clique sur Lancer.",
        ]
        quoted_lines = " ".join(shlex.quote(line) for line in lines)
        return f"clear; printf '%s\\n' {quoted_lines}; echo"

    def _notify_launch_error(self, tool_name: str) -> None:
        self.log(f"Impossible de lancer {tool_name}.", "error")
        messagebox.showerror(
            "Erreur de lancement",
            f"Échec du lancement de '{tool_name}'. Consulte la console intégrée.",
        )

    def open_terminal(self) -> None:
        self.log("Ouverture d'un terminal...", "info")
        ok = self.manager.open_terminal()
        if ok:
            self.log("Terminal ouvert.", "ok")
        else:
            self.log(
                "Terminal introuvable (xfce4-terminal, x-terminal-emulator, exo-open).",
                "error",
            )
            messagebox.showerror(
                "Terminal introuvable",
                "Aucun terminal disponible. Essayés: xfce4-terminal, x-terminal-emulator, "
                "exo-open --launch TerminalEmulator.",
            )


def main() -> None:
    manager = ToolManager(TOOLS)
    app = App(manager)
    app.mainloop()


if __name__ == "__main__":
    main()
