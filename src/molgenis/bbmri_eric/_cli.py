import argparse
import logging
import sys
import textwrap
from getpass import getpass
from typing import List, Tuple

from molgenis.bbmri_eric import __version__, bbmri_client
from molgenis.bbmri_eric import nodes as nnodes
from molgenis.bbmri_eric.bbmri_client import BbmriSession
from molgenis.bbmri_eric.eric import Eric
from molgenis.client import MolgenisRequestError

_logger = logging.getLogger(__name__)

_description = textwrap.dedent(
    rf"""
          __       __   __         __
    |\/| /  \ |   / _  |_  |\ | | (_
    |  | \__/ |__ \__) |__ | \| | __)
 __   __        __         __  __     __    __
|__) |__) |\/| |__) |  __ |_  |__) | /     /   |   |
|__) |__) |  | | \  |     |__ | \  | \__   \__ |__ |     v{__version__}

example usage:
  # Stage data from all or some external national nodes to the directory:
  eric stage all
  eric stage nl de be

  # Publish all or some national nodes to the production tables:
  eric publish all
  eric publish nl de be uk
"""
)


def main(args: List[str]):
    """Parses the command line arguments and calls the corresponding actions.

    Args:
      args (List[str]): command line parameters as list of strings
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    session = _create_session(args)
    eric = Eric(session)
    execute_command(args, eric)


def _create_session(args) -> BbmriSession:
    username, password = _get_username_password(args)
    session = bbmri_client.BbmriSession(url=args.target)
    try:
        session.login(username, password)
    except MolgenisRequestError as e:
        print(e.message)
        exit(1)
    return session


def _get_username_password(args) -> Tuple[str, str]:
    if not args.username:
        username = input("Username: ")
    else:
        username = args.username
    password = getpass()
    return username, password


def execute_command(args, eric):
    all_nodes = len(args.nodes) == 1 and args.nodes[0] == "all"
    if args.action == "stage":
        if all_nodes:
            eric.stage_all_external_nodes()
        else:
            eric.stage_external_nodes(nnodes.get_external_nodes(args.nodes))
    elif args.action == "publish":
        if all_nodes:
            eric.publish_all_nodes()
        else:
            eric.publish_nodes(nnodes.get_nodes(args.nodes))


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`"""
    main(sys.argv[1:])


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawTextHelpFormatter,
        description=_description,
    )

    parser.add_argument(
        "action", choices=["stage", "publish"], help="action to perform on the nodes"
    )
    parser.add_argument(
        dest="nodes",
        help="one or more nodes to stage or publish (separated by whitespace) - "
        "use 'all' to select all nodes",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--target",
        "-t",
        help="the URL of the target directory (default: "
        "https://directory.bbmri-eric.eu/)",
        default="https://directory.bbmri-eric.eu/",
    )
    parser.add_argument(
        "--username",
        "-u",
        help="the username to use when connecting to the target (will be prompted if "
        "not provided)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="molgenis-py-bbmri-eric {ver}".format(ver=__version__),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    run()