"""Module for handling SFTP operations."""

import paramiko
import os
from .encrypt import encrypt_file, verify_crypt4gh_header
from pathlib import Path
from typing import Union, Optional


def _sftp_connection(username: str = "", hostname: str = "", port: int = 22, sftp_key: str = "", sftp_pass: str = "") -> Union[paramiko.PKey, str, None]:
    """Test SFTP connection and determine key type before uploading."""
    print("Testing connection to SFTP server.")

    # Test if key is RSA
    transport = paramiko.Transport((hostname, int(port)))
    paramiko_key: paramiko.PKey
    try:
        print("Testing if SSH key is of type RSA")
        paramiko_key = paramiko.rsakey.RSAKey.from_private_key_file(sftp_key, password=sftp_pass)
        transport.connect(
            username=username,
            pkey=paramiko_key,
        )
        print("SFTP test connection: OK")
        return paramiko_key
    except Exception as e:
        print(f"SFTP Error: {e}")
    finally:
        transport.close()
    # Test if key is ed25519
    try:
        print("Testing if SSH key is of type Ed25519")
        paramiko_key = paramiko.ed25519key.Ed25519Key(filename=sftp_key, password=sftp_pass)
        transport.connect(
            username=username,
            pkey=paramiko_key,
        )
        print("SFTP test connection: OK")
        return paramiko_key
    except Exception as e:
        print(f"SFTP Error: {e}")
    finally:
        transport.close()
    # Test if username+password authentication is used
    try:
        print("Testing if SFTP login passes with username and password")
        transport.connect(
            username=username,
            password=sftp_pass,
        )
        print("SFTP test connection: OK")
        return sftp_pass
    except Exception as e:
        print(f"SFTP Error: {e}")
    finally:
        transport.close()
    return None


def _sftp_upload_file(
    sftp: paramiko.SFTPClient,
    source: str = "",
    destination: str = "",
    private_key: Union[bytes, Path] = b"",
    public_key: Union[str, Path] = "",
) -> None:
    """Upload a single file."""
    verified = verify_crypt4gh_header(source)
    destination = destination.replace(os.sep, "/")  # sftp inbox used to auto-convert \ to / but doesn't anymore
    if verified:
        print(f"File {source} was recognised as a Crypt4GH file, and will be uploaded.")
        print(f"Uploading {source}")
        sftp.put(str(source), str(destination))
        print(f"{source} has been uploaded to {destination}.c4gh")
    else:
        # Encrypt before uploading
        print(f"File {source} was not recognised as a Crypt4GH file, and must be encrypted before uploading.")
        encrypt_file(file=source, private_key_file=private_key, recipient_public_key=public_key)
        print(f"Uploading {source}.c4gh to {destination}.c4gh")
        sftp.put(f"{source}.c4gh", f"{destination}.c4gh")
        print(f"{source}.c4gh has been uploaded to {destination}.c4gh")
        print(f"Removing auto-encrypted file {source}.c4gh")
        os.remove(f"{source}.c4gh")
        print(f"{source}.c4gh removed")


def _sftp_upload_directory(
    sftp: paramiko.SFTPClient,
    directory: str = "",
    private_key: Union[bytes, Path] = b"",
    public_key: Union[str, Path] = "",
) -> None:
    """Upload directory."""
    for item in os.walk(directory):
        # determine relative directory structure from absolute path
        # example /home/user/target -> target
        # example /home/user/target/subfolder -> target/subfolder
        # example C:\Users\user\target\subfolder -> target/subfolder
        relative_structure = f"{Path(directory).name}{item[0].removeprefix(directory)}".replace(os.sep, "/")
        # first create destination directory structure
        mkdir_p(sftp, relative_structure)
        # then upload each file per directory
        for sub_item in item[2]:
            _sftp_upload_file(
                sftp=sftp,
                source=str(Path(item[0]).joinpath(sub_item)),
                destination=f"/{str(Path(relative_structure).joinpath(sub_item))}",
                private_key=private_key,
                public_key=public_key,
            )


def mkdir_p(sftp: paramiko.SFTPClient, directory: str) -> None:
    """Create remote SFTP directory, emulates `mkdir -p`.

    Author: https://stackoverflow.com/users/2845044/gabhijit
    Source: https://stackoverflow.com/a/20422692/8166034
    """
    directories = []

    while len(directory) > 1:
        directories.append(directory)
        directory, _ = os.path.split(directory)

    if len(directory) == 1 and not directory.startswith("/"):
        directories.append(directory)

    while len(directories):
        directory = directories.pop()
        try:
            sftp.stat(directory)
        except Exception:
            sftp.mkdir(directory)


def _sftp_client(
    username: str = "",
    hostname: str = "",
    port: int = 22,
    sftp_auth: Optional[Union[paramiko.PKey, str]] = None,
) -> Optional[paramiko.SFTPClient]:
    """SFTP client."""
    sftp_key = None
    sftp_pass = None
    if isinstance(sftp_auth, str):
        sftp_pass = sftp_auth
    if isinstance(sftp_auth, paramiko.PKey):
        sftp_key = sftp_auth
    try:
        print(f"Connecting to {hostname} as {username}.")
        transport = paramiko.Transport((hostname, int(port)))
        transport.connect(username=username, password=sftp_pass, pkey=sftp_key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("SFTP connected, ready to upload files.")
        return sftp
    except paramiko.BadHostKeyException as e:
        print(f"SFTP error: {e}")
        raise Exception("BadHostKeyException on " + hostname)
    except paramiko.AuthenticationException as e:
        print(f"SFTP authentication failed, error: {e}")
        raise Exception("AuthenticationException on " + hostname)
    except paramiko.SSHException as e:
        print(f"Could not connect to {hostname}, error: {e}")
        raise Exception("SSHException on " + hostname)
    except Exception as e:
        print(f"SFTP Error: {e}")

    return None
