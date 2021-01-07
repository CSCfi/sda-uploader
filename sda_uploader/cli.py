"""SDA Uploader CLI."""

import sys
import secrets
import getpass
import argparse

from pathlib import Path
from functools import partial

from typing import Sequence, Tuple, Union

from crypt4gh.keys import c4gh, get_private_key, get_public_key

from .sftp import _sftp_connection, _sftp_upload_file, _sftp_upload_directory, _sftp_client
from . import cli_version


def mock_callback(password: str) -> str:
    """Mock callback to return password."""
    return password


def generate_one_time_key() -> Tuple:
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


def load_encryption_keys(private_key_file: Union[str, Path] = "", private_key_password: str = None, public_key_file: Union[str, Path] = "") -> Tuple:
    """Load encryption keys."""
    private_key = ""
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
            sys.exit(f"Incorrect password for {private_key}. This is likely a bug.")  # generated password, should not fail
    public_key = get_public_key(public_key_file)
    return private_key, public_key


def process_arguments(args: argparse.Namespace) -> argparse.Namespace:
    """Process command line arguments."""
    print("Processing arguments.")

    # Check that target exists
    if Path(args.target).is_file() or Path(args.target).is_dir():
        pass
    else:
        sys.exit(f"Could not find upload target {args.target}")

    # Check that public key is set and exists
    if args.public_key is None:
        sys.exit("Program aborted: Encryption requires recipient public key.")
    if not Path(args.public_key).is_file():
        sys.exit(f"Program aborted: Could not find file {args.public_key}")

    # Check for SFTP arguments
    if args.hostname is None:
        sys.exit("Program aborted: SFTP server hostname must not be empty.")
    if args.username is None:
        sys.exit("Program aborted: SFTP server username must not be empty.")
    if args.identity_file:
        if not Path(args.identity_file).is_file():
            sys.exit(f"Program aborted: Could not find file {args.identity_file}")
        if args.identity_file_password is None:
            args.identity_file_password = getpass.getpass(f"Password for {args.identity_file}: ")
    else:
        if args.user_password is None:
            args.user_password = getpass.getpass(f"Password for {args.username}: ")

    # Check for encryption arguments
    # Private key is optional for encryption, if it's not set, a one-time key will be used
    if args.private_key:
        if Path(args.private_key).is_file():
            if args.private_key_password is None:
                args.private_key_password = getpass.getpass(f"Password for {args.private_key}: ")
        else:
            sys.exit(f"Program aborted: Could not find file {args.private_key}")

    # User confirmation before uploading
    if not args.overwrite:
        user_confirmation = str(input("Existing files and directories will be overwritten, do you want to continue? [y/N] ") or "n").lower()  # nosec
        if not user_confirmation == "y":
            sys.exit("Program aborted.")

    return args


def parse_arguments(arguments: Union[Sequence, None]) -> argparse.Namespace:
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
    parser.add_argument("-pub", "--public_key", default=None, help="Crypt4GH recipient public key. Required for encryption.")
    parser.add_argument("-v", "--version", action="version", version=cli_version, help="Display program version.")
    if len(sys.argv) <= 1:
        # If no command line arguments were given, print help text
        parser.print_help()
        sys.exit(0)
    return parser.parse_args(arguments)


def main(arguments: Sequence = None) -> None:
    """Start program."""
    print("CSC Sensitive Data Submission SFTP Tool")

    # Get command line arguments
    cli_args = parse_arguments(arguments)

    # Process arguments, an error is raised on bad arguments, if no errors, will pass silently
    cli_args = process_arguments(cli_args)

    # Determine authentication type and test connection
    sftp_auth = _sftp_connection(
        username=cli_args.username,
        hostname=cli_args.hostname,
        port=cli_args.port,
        sftp_key=cli_args.identity_file,
        sftp_pass=cli_args.identity_file_password or cli_args.user_password,
    )

    if not sftp_auth:
        sys.exit("SFTP authentication failed.")

    # Get SFTP client
    sftp_client = _sftp_client(username=cli_args.username, hostname=cli_args.hostname, port=cli_args.port, sftp_auth=sftp_auth)

    # Load Crypt4GH key-files
    private_key, public_key = load_encryption_keys(
        private_key_file=cli_args.private_key,
        private_key_password=cli_args.private_key_password,
        public_key_file=cli_args.public_key,
    )

    # Do the upload process
    # If target is a file, handle single file upload case
    if Path(cli_args.target).is_file():
        _sftp_upload_file(
            sftp=sftp_client,
            source=cli_args.target,
            destination=Path(cli_args.target).name,
            private_key=private_key,
            public_key=public_key,
        )

    # If target is a directory, handle directory upload case
    if Path(cli_args.target).is_dir():
        _sftp_upload_directory(sftp=sftp_client, directory=cli_args.target, private_key=private_key, public_key=public_key)

    print("Program finished.")


if __name__ == "__main__":
    main()
