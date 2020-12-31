"""SDA GUI Uploader Main Module."""

from .gui import GUI
import tkinter as tk


def main():
    """Run Program."""
    root = tk.Tk()
    GUI(root)
    print("To begin file upload:\n")
    print("1. Generate personal keypair (optional)")
    print("2. Load your private key (optional) or leave empty for random key")
    print("3. Load your recipient's public key")
    print("4. Select a file or a directory for upload (not both)")
    print("5. Write SFTP username, server and port to SFTP Credentials")
    print("6. Load your SFTP identity key (optional) or leave empty to use SFTP password")
    print("7. Click [Encrypt and Upload File(s)] to upload selected file or directory")
    print("8. Password for private key (if set) and SFTP authentication will be prompted\n")
    root.mainloop()


if __name__ == "__main__":
    main()
