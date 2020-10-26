"""SDA Uploader CLI."""

import sys
import secrets
import getpass
import argparse

from pathlib import Path
from functools import partial

from crypt4gh.keys import c4gh, get_private_key, get_public_key

from .sftp import _sftp_connection, _sftp_upload_file, _sftp_upload_directory, _sftp_client
from . import __version__


def mock_callback(password):
    """Mock callback to return password."""
    return password


def generate_one_time_key():
    """Generate one time Crypt4GH encryption key."""
    random_password = secrets.token_hex(16)
    private_key_file = f"{getpass.getuser()}_temporary_crypt4gh.key"
    public_key_file = f"{getpass.getuser()}_temporary_crypt4gh.pub"
    # Remove existing temp keys if they exist
    try:
        Path(private_key_file).unlink()
        Path(public_key_file).unlink()
    except FileNotFoundError:
        # No existing temp keys were found
        pass
    c4gh.generate(private_key_file, public_key_file, callback=partial(mock_callback, random_password))
    print("One-time use encryption key generated.")
    return private_key_file, public_key_file, random_password


def load_encryption_keys(private_key_file=None, private_key_password=None, public_key_file=None):
    """Load encryption keys."""
    if private_key_file:
        # If using user's own crypt4gh private key
        try:
            private_key = get_private_key(private_key_file, partial(mock_callback, private_key_password))
        except Exception:
            sys.exit(f"Incorrect password for {private_key_file}")
    else:
        # If using generated one-time encryption key
        temp_private_key, temp_public_key, temp_private_key_password = generate_one_time_key()
        try:
            private_key = get_private_key(temp_private_key, partial(mock_callback, temp_private_key_password))
            try:
                # Remove temp keys
                Path(temp_private_key).unlink()
                Path(temp_public_key).unlink()
            except FileNotFoundError:
                # No existing temp keys were found, which is kinda weird
                pass
        except Exception:
            sys.exit(
                f"Incorrect password for {private_key}. This is likely a bug."
            )  # generated password, should not fail
    public_key = get_public_key(public_key_file)
    return private_key, public_key


def process_arguments(a):
    """Process command line arguments."""
    print("Processing arguments.")

    # Check that target exists
    if Path(a.target).is_file() or Path(a.target).is_dir():
        pass
    else:
        sys.exit(f"Could not find upload target {a.target}")

    # Check that public key is set and exists
    if a.public_key is None:
        sys.exit("Program aborted: Encryption requires recipient public key.")
    if not Path(a.public_key).is_file():
        sys.exit(f"Program aborted: Could not find file {a.public_key}")

    # Check for SFTP arguments
    if a.hostname is None:
        sys.exit("Program aborted: SFTP server hostname must not be empty.")
    if a.username is None:
        sys.exit("Program aborted: SFTP server username must not be empty.")
    if a.identity_file:
        if not Path(a.identity_file).is_file():
            sys.exit(f"Program aborted: Could not find file {a.identity_file}")
        if a.identity_file_password is None:
            a.identity_file_password = getpass.getpass(f"Password for {a.identity_file}: ")
    else:
        if a.user_password is None:
            a.user_password = getpass.getpass(f"Password for {a.username}: ")

    # Check for encryption arguments
    # Private key is optional for encryption, if it's not set, a one-time key will be used
    if a.private_key:
        if Path(a.private_key).is_file():
            if a.private_key_password is None:
                a.private_key_password = getpass.getpass(f"Password for {a.private_key}: ")
        else:
            sys.exit(f"Program aborted: Could not find file {a.private_key}")

    # User confirmation before uploading
    if not a.overwrite:
        user_confirmation = str(
            input("Existing files and directories will be overwritten, do you want to continue? [y/N] ") or "n"
        ).lower()
        if not user_confirmation == "y":
            sys.exit("Program aborted.")

    return a


def parse_arguments(arguments):
    """Parse command line arguments and options."""
    print("Parsing arguments")
    parser = argparse.ArgumentParser(description="CSC Sensitive Data Submission SFTP Tool.")
    parser.add_argument("target", help="Target file or directory to be uploaded.")
    parser.add_argument("-host", "--hostname", help="SFTP server hostname.")
    parser.add_argument("-p", "--port", default=22, help="SFTP server port number. Defaults to 22.")
    parser.add_argument("-u", "--username", help="SFTP server username.")
    parser.add_argument(
        "-upass",
        "--user_password",
        help="Password for username. Will be prompted if not set and not using an identity file.",
    )
    parser.add_argument("-i", "--identity_file", help="RSA private key (identity file) for SFTP authentication.")
    parser.add_argument(
        "-ipass",
        "--identity_file_password",
        help="Password for RSA private key. If not set, a password will be prompted.",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="Force overwriting of existing files. If this is not set, user confirmation will be asked before uploading.",
    )
    parser.add_argument(
        "-key",
        "--private_key",
        default=None,
        help="Crypt4GH sender private key. Optional: if not given, a one-time encryption key will be used.",
    )
    parser.add_argument(
        "-keypass",
        "--private_key_password",
        help="Password for Crypt4GH sender private key. If not set, a password will be prompted if using an existing encryption key.",
    )
    parser.add_argument(
        "-pub", "--public_key", default=None, help="Crypt4GH recipient public key. Required for encryption."
    )
    parser.add_argument("-v", "--version", action="version", version=__version__, help="Display program version.")
    if len(sys.argv) <= 1:
        # If no command line arguments were given, print help text
        sys.exit(parser.print_help())
    return parser.parse_args(arguments)


def main(arguments=None):
    """Start program."""
    print("CSC Sensitive Data Submission SFTP Tool")

    # Get command line arguments
    arguments = parse_arguments(arguments)

    # Process arguments, an error is raised on bad arguments, if no errors, will pass silently
    arguments = process_arguments(arguments)

    # Determine authentication type and test connection
    sftp_auth = _sftp_connection(
        username=arguments.username,
        hostname=arguments.hostname,
        port=arguments.port,
        sftp_key=arguments.identity_file,
        sftp_pass=arguments.identity_file_password or arguments.user_password,
    )

    if not sftp_auth:
        sys.exit("SFTP authentication failed.")

    # Get SFTP client
    sftp_client = _sftp_client(
        username=arguments.username, hostname=arguments.hostname, port=arguments.port, sftp_auth=sftp_auth
    )

    # Load Crypt4GH key-files
    private_key, public_key = load_encryption_keys(
        private_key_file=arguments.private_key,
        private_key_password=arguments.private_key_password,
        public_key_file=arguments.public_key,
    )

    # Do the upload process
    # If target is a file, handle single file upload case
    if Path(arguments.target).is_file():
        _sftp_upload_file(
            sftp=sftp_client,
            source=arguments.target,
            destination=Path(arguments.target).name,
            private_key=private_key,
            public_key=public_key,
        )

    # If target is a directory, handle directory upload case
    if Path(arguments.target).is_dir():
        _sftp_upload_directory(
            sftp=sftp_client, directory=arguments.target, private_key=private_key, public_key=public_key
        )

    print("Program finished.")


if __name__ == "__main__":
    main()
