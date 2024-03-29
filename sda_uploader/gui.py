"""SDA Uploader GUI."""

import os
import sys
import json
import tkinter as tk
from typing import Dict, Union
import paramiko

from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
from functools import partial
from platform import system
from os import chmod
from stat import S_IRWXU

from crypt4gh.keys import get_public_key
from nacl.public import PrivateKey

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
        # This prevents pyinstaller --noconsole from referencing a nonexistent sys.stdout.write
        if system() == "Windows":
            self.old_stdout = sys.stdout
            self.tmp_stdout = open(os.devnull, "w")
            sys.stdout = self.tmp_stdout
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

        self.sftp_key_label = tk.Label(window, text="SSH Key")
        self.sftp_key_label.grid(column=0, row=8, sticky=tk.W)
        self.sftp_key_value = tk.StringVar()
        self.sftp_key_field = tk.Entry(window, width=OS_CONFIG["field_width"], textvariable=self.sftp_key_value)
        self.sftp_key_field.grid(column=0, row=9, sticky=tk.W)
        self.sftp_key_field.config(state="disabled")
        sftp_key_file = data.get("sftp_key_file", None)
        if sftp_key_file and Path(sftp_key_file).is_file():
            self.sftp_key_value.set(sftp_key_file)

        self.activity_label = tk.Label(window, text="Activity Log")
        self.activity_label.grid(column=0, row=11, sticky=tk.W)
        self.activity_field = ScrolledText(window, height=12)
        self.activity_field.grid(column=0, row=12, columnspan=3, sticky=tk.W)
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
            text="Load SSH Key",
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

        self.remember_pass = tk.BooleanVar()
        self.overwrite_files = tk.BooleanVar()
        self.passwords: Dict[str, Union[str, bool]] = {"sftp_password": "", "asked_password": False}
        self.remember_password = tk.Checkbutton(window, text="Save password for this session", variable=self.remember_pass, onvalue=True, offvalue=False)
        self.overwrite_files_option = tk.Checkbutton(
            window, text="Overwrite existing remote files", variable=self.overwrite_files, onvalue=True, offvalue=False
        )
        self.remember_password.grid(column=1, row=10, sticky=tk.E)
        self.overwrite_files_option.grid(column=1, row=11, sticky=tk.E)

    def print_redirect(self, message: str) -> None:
        """Print to activity log widget instead of console."""
        self.activity_field.config(state="normal")
        self.activity_field.insert(tk.END, message, None)  # type: ignore
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

    def _do_upload(self, private_key: bytes) -> None:
        # Ask for RSA key password
        sftp_password: str = str(self.passwords["sftp_password"])
        if not self.passwords["asked_password"]:
            _prompted_password = askstring("SFTP Passphrase", "Passphrase for SSH KEY or SFTP Username.\nLeave empty if using unencrypted SSH Key.", show="*")
            if _prompted_password is None:
                # This if-clause is for closing the prompt without proceeding with the upload workflow
                return
            sftp_password = str(_prompted_password)  # must cast to string, because initial type allows None values
            if self.remember_pass.get():
                # password is stored only for this session, in case the user wants to upload again
                self.passwords["sftp_password"] = sftp_password
            self.passwords["asked_password"] = True
        # Test SFTP connection
        sftp_username = self.sftp_username_value.get()
        sftp_hostname, sftp_port = "", 22
        try:
            sftp_server = self.sftp_server_value.get().split(":")
            sftp_hostname = sftp_server[0]
            sftp_port = int(sftp_server[1])
        except (ValueError, IndexError):
            sftp_hostname = self.sftp_server_value.get()
        sftp_auth = self.test_sftp_connection(
            username=sftp_username,
            hostname=sftp_hostname,
            port=sftp_port,
            sftp_key=self.sftp_key_value.get(),
            sftp_pass=sftp_password,
        )
        # Encrypt and upload
        if private_key and sftp_auth:
            sftp = _sftp_client(
                username=sftp_username,
                hostname=sftp_hostname,
                port=sftp_port,
                sftp_auth=sftp_auth,
            )
            if sftp:
                # This code block will always execute and is only here to satisfy mypy tests
                public_key = get_public_key(self.their_key_value.get())
                self.sftp_upload(
                    sftp=sftp,
                    target=self.file_value.get(),
                    private_key=private_key,
                    public_key=public_key,
                    overwrite=self.overwrite_files.get(),
                )
        else:
            print("Could not form SFTP connection.")
            self.passwords["asked_password"] = False  # resetting prompt in case password was wrong

    def _start_process(self) -> None:
        if self.their_key_value.get() and self.file_value.get() and self.sftp_username_value.get() and self.sftp_server_value.get():
            # Generate random encryption key
            temp_private_key = bytes(PrivateKey.generate())
            # Encrypt and upload
            self._do_upload(temp_private_key)
        else:
            print("All fields must be filled")

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
    ) -> Union[paramiko.PKey, str, None]:
        """Test SFTP connection and determine key type before uploading."""
        _sftp_auth = _sftp_connection(username=username, hostname=hostname, port=port, sftp_key=sftp_key, sftp_pass=sftp_pass)
        self.write_config()  # save fields
        return _sftp_auth

    def sftp_upload(
        self,
        sftp: paramiko.SFTPClient,
        target: str = "",
        private_key: Union[bytes, Path] = b"",
        public_key: Union[str, Path] = "",
        overwrite: bool = False,
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
                overwrite=overwrite,
                client="gui",
            )

        if Path(target).is_dir():
            _sftp_upload_directory(
                sftp=sftp,
                directory=target,
                private_key=private_key,
                public_key=public_key,
                overwrite=overwrite,
                client="gui",
            )

        # Close SFTP connection
        print("Disconnecting SFTP.")
        sftp.close()
        print("SFTP has been disconnected.")

    def cleanup(self) -> None:
        """Restore the sys.stdout on Windows."""
        if system() == "Windows":
            sys.stdout = self.old_stdout
            self.tmp_stdout.close()
