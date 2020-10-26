# SDA Uploader
SDA Uploader is a tool for encrypting and uploading files. Files are encrypted with [Crypt4GH](http://samtools.github.io/hts-specs/crypt4gh.pdf) and uploaded with [SFTP](https://www.ssh.com/ssh/sftp/).

## Demo
[![Demo Video](https://kannu.csc.fi/s/Z5wnNDPFfgR5583/preview)](https://kannu.csc.fi/s/DiD4Bicx8zwd4Gf)

Click on the picture above to view the demo video

Current features:
- Generation of key pair
- Encryption of file(s)
- Direct uploading of encrypted file(s)
- Upload single files or whole directories
- Filled fields will be saved for later re-use
- Option to save password for session if encrypting and uploading multiple objects
- Supports RSA and Ed25519 keys or username+password for SFTP authentication

## Installation

The GUI requires:
- Python 3.6+
- Tkinter

```
git clone https://github.com/CSCfi/sda-uploader
pip install ./sda-uploader

sdagui
```

Saved fields are kept in `.sda_uploader_config.json` in the user's home directory.

## Build Standalone Executable

Standalone executable build requires:
- pyinstaller

The GUI can be built into a standalone executable and distributed to machines that don't have python installed. After running the `pyinstaller` command, the standalone executable file can be found in the `dist/` directory.

```
pip install pyinstaller

pyinstaller --noconsole --onefile sdagui.py
```

This has been tested on Linux, Mac and Windows.

To run the executable on Linux and Mac:
```
./sdagui
```

To run the executable on Windows:
- Double click on `sdagui.exe` or run the following in `cmd`:
```
sdagui.exe
```
