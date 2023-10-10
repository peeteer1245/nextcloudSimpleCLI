#!/usr/bin/env python3

import json
import argparse
import nextcloud_client
from pathlib import Path, PurePath

DEFAULT_SETTINGS_FILE = "config.json"


def upload(args: argparse.Namespace, nc: nextcloud_client.Client) -> None:
    """upload files to nextcloud with the chunking api (no size limit)

    :param args: already parsed arguments
    :param nc: a already logged-in nextcloud session
    :returns: None
    """
    if len(args.source_files) == 0:
        print("source files / folders are missing")
        print("see usage (--help) for more information")

    # add trailing slash if it does not exist
    # we only allow uploading into a directory
    destination = args.destination if args.destination[-1:] == "/" else args.destination + "/"

    for file in args.source_files:
        file_path = Path(file)
        if file_path.exists():
            if file_path.is_dir():
                print(f"uploading dir {file} to {destination}")
                try:
                    nc.put_directory(destination, file, chunked=True)
                except nextcloud_client.nextcloud_client.HTTPResponseError as e:
                    if e.status_code == 405:
                        print(f"Could not upload {file}.")
                        print(f"{file} already exists in {destination}.")
                        print("Remove it from Nextcloud or set a different destination.")
                    continue
            else:
                print(f"uploading file {file} to {destination}")
                try:
                    nc.mkdir(destination)
                except nextcloud_client.nextcloud_client.HTTPResponseError as e:
                    # target directory already exists
                    if e.status_code == 409:
                        pass
                nc.put_file(destination, file, chunked=True)
        else:
            print(f"{file_path} does not exist")


def sizeof_fmt(num, suffix=""):
    """stolen from stackoverflow
    https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size/1094933#1094933
    """
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def _print_nc_files(print_human: bool, file_list: list) -> None:
    """prints list of nextcloud files in a similar style to ls

    :param print_human: bool to print file-sizes in human form
    :param file_list: list of :class:`nextcloud_client.FileInfo` objects
    :returns: None
    """

    def _get_file_size(file: nextcloud_client.FileInfo):
        if file.is_dir():
            file_size = int(file.attributes[r"{DAV:}quota-used-bytes"])
        else:
            file_size = int(file.get_size())
        return file_size

    padding = 0
    # first loop to get correct padding dimensions
    for file in file_list:
        file_size = _get_file_size(file)
        if print_human:
            file_size = sizeof_fmt(file_size)

        file_size_string_length = len(str(file_size))
        if file_size_string_length > padding:
            padding = file_size_string_length

    # second loop to acually print
    for file in file_list:
        file_size = _get_file_size(file)
        if print_human:
            file_size = sizeof_fmt(file_size)

        file_path = PurePath(file.path).name
        if file.is_dir():
            file_path += "/"

        last_modified = file.get_last_modified()
        print(f"{file_size:>{padding}} {last_modified} {file_path}")


def list(args: argparse.Namespace, nc: nextcloud_client.Client) -> None:
    """list remote files/folders

    :param args: already parsed arguments
    :param nc: a already logged-in nextcloud session
    :returns: None
    """
    all_destinations = [args.destination] + args.source_files
    for destination in all_destinations:
        if len(all_destinations) > 1:
            print(f"{destination}:")

        try:
            dst_info = nc.file_info(destination)
        except nextcloud_client.nextcloud_client.HTTPResponseError as e:
            if e.status_code == 404:
                print(f"{destination} not found")
            else:
                raise e
            continue

        if dst_info is not None and dst_info.is_dir():
            _print_nc_files(args.human_readable, nc.list(destination))
        elif dst_info is not None:
            _print_nc_files(args.human_readable, [dst_info])


def nextcloud_connect(args: argparse.Namespace) -> nextcloud_client.Client:
    """create a authenticated nextcloud session

    :param args: already parsed arguments
    :returns: a authenticated nextcloud session
    :rtype: :class:`nextcloud_client.Client`
    """

    def _get_default_file_location() -> str:
        script = PurePath(__file__)
        return str(script.parent / DEFAULT_SETTINGS_FILE)

    def _read_config_file(config_file: str) -> list:
        with open(config_file, "r") as f:
            config = json.load(f)
        if "url" in config and "username" in config and "password" in config:
            return (config["url"], config["username"], config["password"])
        else:
            raise KeyError("value missing in config file")

    if args.server is not None and args.user is not None and args.password is not None:
        url = args.server
        username = args.user
        password = args.password
    elif args.config is not None:
        url, username, password = _read_config_file(args.config)
    elif args.config is None and args.server is None:
        url, username, password = _read_config_file(_get_default_file_location())
    else:
        # this should never be reached
        pass

    nc = nextcloud_client.Client(url)
    nc.login(username, password)

    return nc


def parse_args() -> argparse.Namespace:
    """read and parse command line parameters

    :returns: parsed arguments
    :rtype: :class:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("source_files", nargs="*", help="source files / folders")
    parser.add_argument("destination", help="destination folder")

    parser.add_argument(
        "-l", action="store_true", help="list Nextcloud directory contents"
    )
    parser.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="print sizes like 1K 234M 2G etc.",
    )
    parser.add_argument(
        "-c", "--config", help="config file containing login credentials"
    )
    parser.add_argument("-s", "--server", help="url of nextcloud server")
    parser.add_argument("-u", "--user", help="login username")
    parser.add_argument("-p", "--password", help="login password")

    args = parser.parse_args()

    return args


def main() -> None:
    parsed_args = parse_args()

    nc = nextcloud_connect(parsed_args)

    if parsed_args.l == True:
        list(parsed_args, nc)
    else:
        upload(parsed_args, nc)


if __name__ == "__main__":
    main()
