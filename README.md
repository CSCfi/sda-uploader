# SDA Uploader
SDA Uploader is a tool for encrypting and uploading files. Files are encrypted with [Crypt4GH](http://samtools.github.io/hts-specs/crypt4gh.pdf) and uploaded with [SFTP](https://www.ssh.com/ssh/sftp/).

## GUI Demo
[![Demo Video](https://kannu.csc.fi/s/qX4PbXDDgmeBss2/preview)](https://kannu.csc.fi/s/ER4SMQWECZwnqt5)

Click on the picture above to view the GUI demo video

Current features:
- Encryption of file(s)
- Direct uploading of encrypted file(s)
- Upload single files or whole directories
- Filled fields will be saved for later re-use
- Option to save password for session if encrypting and uploading multiple objects
- Supports RSA and Ed25519 keys for SFTP authentication

### GUI Config
Saved fields are kept in `.sda_uploader_config.json` in the user's home directory.

## CLI Demo
[![asciicast](https://asciinema.org/a/367991.svg)](https://asciinema.org/a/367991)

Click on the picture above to view the CLI demo video

Current features:
- One-time encryption keys generated if existing keys are not provided (anonymous uploading)
- Encryption of file(s)
- Direct uploading of encrypted file(s)
- Upload single files or whole directories
- Supports RSA and Ed25519 keys or username+password for SFTP authentication

### CLI Usage
```
$ sdacli 
CSC Sensitive Data Submission SFTP Tool
Parsing arguments
usage: sdacli [-h] [-host HOSTNAME] [-p PORT] [-u USERNAME]
              [-upass USER_PASSWORD] [-i IDENTITY_FILE]
              [-ipass IDENTITY_FILE_PASSWORD] [-o] [-key PRIVATE_KEY]
              [-keypass PRIVATE_KEY_PASSWORD] [-pub PUBLIC_KEY] [-v]
              target

CSC Sensitive Data Submission SFTP Tool.

positional arguments:
  target                Target file or directory to be uploaded.

optional arguments:
  -h, --help            show this help message and exit
  -host HOSTNAME, --hostname HOSTNAME
                        SFTP server hostname.
  -p PORT, --port PORT  SFTP server port number. Defaults to 22.
  -u USERNAME, --username USERNAME
                        SFTP server username.
  -upass USER_PASSWORD, --user_password USER_PASSWORD
                        Password for username. Will be prompted if not set and
                        not using an identity file.
  -i IDENTITY_FILE, --identity_file IDENTITY_FILE
                        RSA private key (identity file) for SFTP
                        authentication.
  -ipass IDENTITY_FILE_PASSWORD, --identity_file_password IDENTITY_FILE_PASSWORD
                        Password for RSA private key. If not set, a password
                        will be prompted.
  -o, --overwrite       Force overwriting of existing files. If this is not
                        set, user confirmation will be asked before uploading.
  -key PRIVATE_KEY, --private_key PRIVATE_KEY
                        Crypt4GH sender private key. Optional: if not given, a
                        one-time encryption key will be used.
  -keypass PRIVATE_KEY_PASSWORD, --private_key_password PRIVATE_KEY_PASSWORD
                        Password for Crypt4GH sender private key. If not set,
                        a password will be prompted if using an existing
                        encryption key.
  -pub PUBLIC_KEY, --public_key PUBLIC_KEY
                        Crypt4GH recipient public key. Required for
                        encryption.
  -v, --version         Display program version.
```

### CLI Example
Minimum required arguments below. `target` takes a file or a directory as argument.
```
sdacli file.txt -host server -u username -pub recipient.pub
```

## Installation

The GUI requires:
- Python 3.6+
- Tkinter

```
git clone https://github.com/CSCfi/sda-uploader
pip install ./sda-uploader

sdagui  # launches graphical tool
sdacli  # launches command line tool
```

## Build Standalone Executable

Standalone executable build requires:
- pyinstaller

The GUI can be built into a standalone executable and distributed to machines that don't have python installed. After running the `pyinstaller` command, the standalone executable file can be found in the `dist/` directory.

```
pip install pyinstaller

pyinstaller --noconsole --onefile sdagui.py
pyinstaller --onefile sdacli.py
```

This has been tested on Linux, Mac and Windows.

To run the executable on Linux and Mac:
```
./sdagui
./sdacli
```

To run the executable on Windows:
- Double click on `sdagui.exe` or `sdacli.exe` or run the following in `cmd`:
```
sdagui.exe
sdacli.exe
```
