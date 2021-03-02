"""Module for handling SFTP operations."""

import paramiko
import os
from .encrypt import encrypt_file, verify_crypt4gh_header
from pathlib import Path
from typing import Union, Optional


def _sftp_connection(
    username: str = "", hostname: str = "", port: int = 22, sftp_key: str = "", sftp_pass: str = ""
) -> Union[paramiko.PKey, paramiko.RSAKey, paramiko.ed25519key.Ed25519Key, str, bool]:
    """Test SFTP connection and determine key type before uploading."""
    print("Testing connection to SFTP server.")
    print(f'SFTP testing timeout is: {os.environ.get("SFTP_TIMEOUT", 5)}. This can be change this with environment variable $SFTP_TIMEOUT')
    # Test if key is RSA
    client = paramiko.SSHClient()
    try:
        print("Testing if SFTP key is of type RSA")
        paramiko_key = paramiko.RSAKey.from_private_key_file(sftp_key, password=sftp_pass)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname,
            allow_agent=False,
            look_for_keys=False,
            port=port,
            timeout=int(os.environ.get("SFTP_TIMEOUT", 5)),
            username=username,
            pkey=paramiko_key,
        )
        print("SFTP test connection: OK")
        return paramiko_key
    except Exception as e:
        print(f"SFTP Error: {e}")
    finally:
        client.close()
    # Test if key is ed25519
    try:
        print("Testing if SFTP key is of type Ed25519")
        paramiko_key = paramiko.ed25519key.Ed25519Key(filename=sftp_key, password=sftp_pass)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname,
            allow_agent=False,
            look_for_keys=False,
            port=port,
            timeout=int(os.environ.get("SFTP_TIMEOUT", 5)),
            username=username,
            pkey=paramiko_key,
        )
        print("SFTP test connection: OK")
        return paramiko_key
    except Exception as e:
        print(f"SFTP Error: {e}")
    finally:
        client.close()
    # Authenticating with password, if key is not set
    try:
        print("Testing if SFTP auth scheme is username+password")
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname,
            allow_agent=False,
            look_for_keys=False,
            port=port,
            timeout=int(os.environ.get("SFTP_TIMEOUT", 5)),
            username=username,
            password=sftp_pass,
        )
        print("SFTP test connection: OK")
        return sftp_pass
    except Exception as e:
        print(f"SFTP Error: {e}")
    finally:
        client.close()
    return False  # neither keys or password worked


def _sftp_upload_file(
    sftp: paramiko.SFTPClient,
    source: Union[str, Path] = "",
    destination: Union[str, Path] = "",
    private_key: Union[str, Path] = "",
    public_key: Union[str, Path] = "",
) -> None:
    """Upload a single file."""
    verified = verify_crypt4gh_header(source)
    if verified:
        print(f"File {source} was recognised as a Crypt4GH file, and will be uploaded.")
        print(f"Uploading {source}")
        sftp.put(str(source), str(destination))
        print(f"{source} has been uploaded.")
    else:
        # Encrypt before uploading
        print(f"File {source} was not recognised as a Crypt4GH file, and must be encrypted before uploading.")
        encrypt_file(file=source, private_key_file=private_key, recipient_public_key=public_key)
        print(f"Uploading {source}.c4gh")
        sftp.put(f"{source}.c4gh", f"{destination}.c4gh")
        print(f"{source}.c4gh has been uploaded.")
        print(f"Removing auto-encrypted file {source}.c4gh")
        os.remove(f"{source}.c4gh")
        print(f"{source}.c4gh removed")


def _sftp_upload_directory(
    sftp: paramiko.SFTPClient,
    directory: Union[str, Path] = "",
    private_key: Union[str, Path] = "",
    public_key: Union[str, Path] = "",
) -> None:
    """Upload directory."""
    sftp_dir: Union[str, Path] = ""
    for item in os.walk(directory):
        sftp_dir = Path(sftp_dir).joinpath(Path(item[0]).name)
        try:
            sftp.mkdir(str(sftp_dir))
            print(f"Directory {sftp_dir} created.")
        except OSError:
            print(f"Skipping directory {sftp_dir} creation, as it already exists.")
        for sub_item in item[2]:
            _sftp_upload_file(
                sftp=sftp,
                source=str(Path(item[0]).joinpath(sub_item)),
                destination=f"/{str(Path(sftp_dir).joinpath(sub_item))}",
                private_key=private_key,
                public_key=public_key,
            )


def _sftp_client(
    username: str = "",
    hostname: str = "",
    port: int = 22,
    sftp_auth: Union[paramiko.PKey, paramiko.RSAKey, paramiko.ed25519key.Ed25519Key, str, bool] = "",
) -> Optional[paramiko.SFTPClient]:
    """SFTP client."""
    try:
        print(f"Connecting to {hostname} as {username}.")
        transport = paramiko.Transport((hostname, int(port)))
        if type(sftp_auth) in [paramiko.rsakey.RSAKey, paramiko.ed25519key.Ed25519Key]:
            # If SFTP key is set, authenticate with that
            transport.connect(username=username, pkey=sftp_auth)
        else:
            # If key is not set, authenticate with password
            transport.connect(username=username, password=sftp_auth)
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
