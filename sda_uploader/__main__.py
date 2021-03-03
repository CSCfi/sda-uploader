"""SDA GUI Uploader Main Module."""

from .gui import GUI
import tkinter as tk


def main() -> None:
    """Run Program."""
    root = tk.Tk()
    GUI(root)
    print("To begin file upload:\n")
    print("1. Load your recipient's public key")
    print("2. Select a file or a directory for upload (not both)")
    print("3. Write SFTP username, server and port to SFTP Credentials")
    print("4. Load your SFTP identity key")
    print("5. Click [Encrypt and Upload File(s)] to upload selected file or directory")
    print("6. Password for SFTP authentication will be prompted\n")
    root.mainloop()


if __name__ == "__main__":
    main()
