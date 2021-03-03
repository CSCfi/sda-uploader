"""SDA Uploader GUI."""

import sys
import json
import getpass
import secrets
import tkinter as tk
from typing import Dict, Tuple, Union
import paramiko

from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
from functools import partial
from platform import system
from os import chmod
from stat import S_IRWXU

from crypt4gh.keys import c4gh, get_private_key, get_public_key

from .sftp import _sftp_connection, _sftp_upload_file, _sftp_upload_directory, _sftp_client
from pathlib import Path

OS_CONFIG = {"field_width": 40, "config_button_width": 25}
if system() == "Linux":
    # use default config
    pass
elif system() == "Darwin":
    # use default config
    pass
elif system() == "Windows":
    OS_CONFIG["field_width"] = 70
    OS_CONFIG["config_button_width"] = 30
else:
    # unknown OS, use default config
    pass


class GUI:
    """Graphical User Interface."""

    def __init__(self, window: tk.Tk) -> None:
        """Initialise window."""
        self.window = window
        self.window.resizable(False, False)
        self.window.title("CSC Sensitive Data Submission Tool")
        # print to activity log instead of console
        sys.stdout.write = self.print_redirect  # type:ignore

        # Load previous values from config file
        self.config_file = Path(Path.home()).joinpath(".sda_uploader_config.json")
        data = self.read_config(self.config_file)

        # 1st column FIELDS AND LABELS

        self.their_key_label = tk.Label(window, text="Recipient Public Key")
        self.their_key_label.grid(column=0, row=0, sticky=tk.W)
        self.their_key_value = tk.StringVar()
        self.their_key_field = tk.Entry(window, width=OS_CONFIG["field_width"], textvariable=self.their_key_value)
        self.their_key_field.grid(column=0, row=1, sticky=tk.W)
        self.their_key_field.config(state="disabled")
        public_key_file = data.get("public_key_file", None)
        if public_key_file and Path(public_key_file).is_file():
            self.their_key_value.set(public_key_file)

        self.file_label = tk.Label(window, text="File or Directory to Upload")
        self.file_label.grid(column=0, row=2, sticky=tk.W)
        self.file_value = tk.StringVar()
        self.file_field = tk.Entry(window, width=OS_CONFIG["field_width"], textvariable=self.file_value)
        self.file_field.grid(column=0, row=3, sticky=tk.W)
        self.file_field.config(state="disabled")

        self.sftp_username_label = tk.Label(window, text="SFTP Username")
        self.sftp_username_label.grid(column=0, row=4, sticky=tk.W)
        self.sftp_username_value = tk.StringVar()
        placeholder_sftp_username_value = "user@institution.org"
        self.sftp_username_value.set(placeholder_sftp_username_value)
        self.sftp_username_field = tk.Entry(window, width=OS_CONFIG["field_width"], textvariable=self.sftp_username_value)
        self.sftp_username_field.grid(column=0, row=5, sticky=tk.W)
        sftp_username = data.get("sftp_username", None)
        if sftp_username and len(sftp_username) > 0:
            self.sftp_username_value.set(sftp_username)

        self.sftp_server_label = tk.Label(window, text="SFTP Server")
        self.sftp_server_label.grid(column=0, row=6, sticky=tk.W)
        self.sftp_server_value = tk.StringVar()
        placeholder_sftp_server_value = "server.org:22"
        self.sftp_server_value.set(placeholder_sftp_server_value)
        self.sftp_server_field = tk.Entry(window, width=OS_CONFIG["field_width"], textvariable=self.sftp_server_value)
        self.sftp_server_field.grid(column=0, row=7, sticky=tk.W)
        sftp_server_credentials = data.get("sftp_server", None)
        if sftp_server_credentials and len(sftp_server_credentials) > 0:
            self.sftp_server_value.set(sftp_server_credentials)

        self.sftp_key_label = tk.Label(window, text="SFTP Key")
        self.sftp_key_label.grid(column=0, row=8, sticky=tk.W)
        self.sftp_key_value = tk.StringVar()
        self.sftp_key_field = tk.Entry(window, width=OS_CONFIG["field_width"], textvariable=self.sftp_key_value)
        self.sftp_key_field.grid(column=0, row=9, sticky=tk.W)
        self.sftp_key_field.config(state="disabled")
        sftp_key_file = data.get("sftp_key_file", None)
        if sftp_key_file and Path(sftp_key_file).is_file():
            self.sftp_key_value.set(sftp_key_file)

        self.activity_label = tk.Label(window, text="Activity Log")
        self.activity_label.grid(column=0, row=10, sticky=tk.W)
        self.activity_field = ScrolledText(window, height=12)
        self.activity_field.grid(column=0, row=11, columnspan=3, sticky=tk.W)
        self.activity_field.config(state="disabled")

        # 2nd column BUTTONS

        self.load_their_key_button = tk.Button(
            window,
            text="Load Recipient Public Key",
            width=OS_CONFIG["config_button_width"],
            command=partial(self.open_file, "public"),
        )
        self.load_their_key_button.grid(column=1, row=0, sticky=tk.E, columnspan=2)

        self.select_file_button = tk.Button(
            window,
            text="Select File to Upload",
            width=OS_CONFIG["config_button_width"],
            command=partial(self.open_file, "file"),
        )
        self.select_file_button.grid(column=1, row=1, sticky=tk.E, columnspan=2)

        self.select_directory_button = tk.Button(
            window,
            text="Select Directory to Upload",
            width=OS_CONFIG["config_button_width"],
            command=partial(self.open_file, "directory"),
        )
        self.select_directory_button.grid(column=1, row=2, sticky=tk.E, columnspan=2)

        self.load_sftp_key_button = tk.Button(
            window,
            text="Load SFTP Key",
            width=OS_CONFIG["config_button_width"],
            command=partial(self.open_file, "sftp_key"),
        )
        self.load_sftp_key_button.grid(column=1, row=3, sticky=tk.E, columnspan=2)

        self.encrypt_button = tk.Button(
            window,
            text="Encrypt and Upload File(s)",
            width=OS_CONFIG["config_button_width"],
            height=3,
            command=partial(self._start_process),
        )
        self.encrypt_button.grid(column=1, row=7, sticky=tk.E, columnspan=2, rowspan=3)

        self.remember_pass = tk.IntVar()
        self.passwords = {"sftp_key": ""}
        self.remember_password = tk.Checkbutton(window, text="Save password for this session", variable=self.remember_pass, onvalue=1, offvalue=0)
        self.remember_password.grid(column=1, row=10, sticky=tk.E)

    def print_redirect(self, message: str) -> None:
        """Print to activity log widget instead of console."""
        self.activity_field.config(state="normal")
        self.activity_field.insert(tk.END, message, None)
        self.activity_field.see(tk.END)
        self.activity_field.config(state="disabled")
        self.window.update()

    def open_file(self, action: str) -> None:
        """Open file and return result according to type."""
        if action == "public":
            public_key_path = askopenfilename()
            self.their_key_value.set(public_key_path)
        elif action == "file":
            file_path = askopenfilename()
            self.file_value.set(file_path)
            if len(file_path) > 0:
                self.select_directory_button.config(state="disabled")
            else:
                self.select_directory_button.config(state="normal")
        elif action == "directory":
            file_path = askdirectory()
            self.file_value.set(file_path)
            if len(file_path) > 0:
                self.select_file_button.config(state="disabled")
            else:
                self.select_file_button.config(state="normal")
        elif action == "sftp_key":
            file_path = askopenfilename()
            self.sftp_key_value.set(file_path)
        else:
            print(f"Unknown action: {action}")

    def _do_upload(self, private_key: str, password: str) -> None:
        try:
            private_key = get_private_key(private_key, partial(self.mock_callback, password))
        except Exception:
            print("Incorrect private key passphrase")
            return
        # Ask for RSA key password
        sftp_password = self.passwords["sftp_key"]
        while len(sftp_password) == 0:
            sftp_password = askstring("SFTP Passphrase", "Passphrase for SFTP KEY", show="*")
            if self.remember_pass.get():
                self.passwords["sftp_key"] = sftp_password
            # This if-clause is for preventing error messages
            if sftp_password is None:
                return
        # Test SFTP connection
        sftp_username = self.sftp_username_value.get()
        sftp_hostname, sftp_port = "", 22
        try:
            sftp_server = self.sftp_server_value.get().split(":")
            sftp_hostname = sftp_server[0]
            sftp_port = int(sftp_server[1])
        except (ValueError, IndexError):
            sftp_hostname = self.sftp_server_value.get()
        sftp_key = self.test_sftp_connection(
            username=sftp_username,
            hostname=sftp_hostname,
            port=sftp_port,
            sftp_key=self.sftp_key_value.get(),
            sftp_pass=sftp_password,
        )
        # Encrypt and upload
        if private_key and sftp_key:
            sftp = _sftp_client(
                username=sftp_username,
                hostname=sftp_hostname,
                port=sftp_port,
                sftp_auth=sftp_key,
            )
            if sftp:
                # This code block will always execute and is only here to satisfy mypy tests
                public_key = get_public_key(self.their_key_value.get())
                self.sftp_upload(sftp=sftp, target=self.file_value.get(), private_key=private_key, public_key=public_key)
        else:
            print("Could not form SFTP connection.")

    def _start_process(self) -> None:
        if self.their_key_value.get() and self.file_value.get() and self.sftp_username_value.get() and self.sftp_server_value.get():
            # Generate random encryption key
            temp_private_key, temp_public_key, temp_password = self._generate_one_time_key()
            # Encrypt and upload
            self._do_upload(temp_private_key, temp_password)
            # Remove temp keys
            self._remove_file(temp_private_key)
            self._remove_file(temp_public_key)
        else:
            print("All fields must be filled")

    def _remove_file(self, filepath: str) -> None:
        """Remove temp files."""
        try:
            Path(filepath).unlink()
            print(f"Removed temp file {filepath}")
        except FileNotFoundError:
            print(f"Temp file {filepath} not found")
            pass

    def _generate_one_time_key(self) -> Tuple:
        """Generate one time Crypt4GH encryption key."""
        random_password = secrets.token_hex(16)
        private_key_file = f"{getpass.getuser()}_temporary_crypt4gh.key"
        public_key_file = f"{getpass.getuser()}_temporary_crypt4gh.pub"
        # Remove existing temp keys if they exist
        self._remove_file(private_key_file)
        self._remove_file(public_key_file)
        c4gh.generate(private_key_file, public_key_file, callback=partial(self.mock_callback, random_password))
        print("One-time use encryption key generated")
        return private_key_file, public_key_file, random_password

    def mock_callback(self, password: str) -> str:
        """Mock callback to return password."""
        return password

    def write_config(self) -> None:
        """Save field values for re-runs."""
        data = {
            "public_key_file": self.their_key_value.get(),
            "sftp_username": self.sftp_username_value.get(),
            "sftp_server": self.sftp_server_value.get(),
            "sftp_key_file": self.sftp_key_value.get(),
        }
        with open(self.config_file, "w") as f:
            f.write(json.dumps(data))
        # Set file to be readable and writable
        chmod(self.config_file, S_IRWXU)

    def read_config(self, path: Union[str, Path]) -> Dict[str, str]:
        """Read field values from previous run if they exist."""
        data = {}
        if Path(path).is_file():
            with open(path, "r") as f:
                data = json.loads(f.read())
        return data

    def test_sftp_connection(
        self, username: str = "", hostname: str = "", port: int = 22, sftp_key: str = "", sftp_pass: str = ""
    ) -> Union[paramiko.PKey, None]:
        """Test SFTP connection and determine key type before uploading."""
        _key = _sftp_connection(username=username, hostname=hostname, port=port, sftp_key=sftp_key, sftp_pass=sftp_pass)
        self.write_config()  # save fields
        return _key

    def sftp_upload(
        self,
        sftp: paramiko.SFTPClient,
        target: Union[str, Path] = "",
        private_key: Union[str, Path] = "",
        public_key: Union[str, Path] = "",
    ) -> None:
        """Upload file or directory."""
        print("Starting upload process.")

        if Path(target).is_file():
            _sftp_upload_file(
                sftp=sftp,
                source=target,
                destination=Path(target).name,
                private_key=private_key,
                public_key=public_key,
            )

        if Path(target).is_dir():
            _sftp_upload_directory(sftp=sftp, directory=target, private_key=private_key, public_key=public_key)

        # Close SFTP connection
        print("Disconnecting SFTP.")
        sftp.close()
        print("SFTP has been disconnected.")
