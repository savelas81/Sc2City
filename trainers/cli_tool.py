import os
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

if __name__ == "__main__":
    # Get the absolute path of the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Add the relative path for the bot script to sys.path
    main_bot_path = os.path.abspath(os.path.join(dir_path, "..", "sc2city"))
    sys.path.append(main_bot_path)

from burny_build_order import burny_build_order
from map_editor import MapType, map_editor
from sc2city.utils import BuildTypes


@dataclass
class Args:
    trainer: str
    url: str = None
    build_type: str = None
    name: str = None
    type: str = None


if __name__ == "__main__":
    parser = ArgumentParser(description="CLI tool for Trainers")
    subparsers = parser.add_subparsers(dest="trainer")

    burny_build_order_parser = subparsers.add_parser(
        "burny_build_order",
        description="Download build orders from Burny's build planner and converts it into bot strategies",
    )
    burny_build_order_parser.add_argument(
        "-u", "--url", type=str, required=True, help="URL for the Burny build order"
    )
    burny_build_order_parser.add_argument(
        "-b",
        "--build_type",
        type=str,
        choices=[bt.name for bt in BuildTypes],
        required=True,
        help="Type for the build order",
    )

    map_editor_parser = subparsers.add_parser(
        "map_editor",
        description="Get building placements from pre made maps in the sc2 editor using the configured map pins",
    )
    map_editor_parser.add_argument(
        "-n", "--name", type=str, required=True, help="Name for the map"
    )
    map_editor_parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[bt.name for bt in MapType],
        required=True,
        help="Type of map used (single or both sides)",
    )
    map_editor_parser.add_argument(
        "-b",
        "--build_type",
        type=str,
        choices=[bt.name for bt in BuildTypes],
        required=True,
        help="Type for the build order",
    )

    args_namespace: Namespace = parser.parse_args()
    args: Args = Args(**vars(args_namespace))

    if args.trainer == "burny_build_order":
        burny_build_order(url=args.url, build_type=BuildTypes[args.build_type])
    elif args.trainer == "map_editor":
        map_editor(
            map_name=args.name,
            map_type=MapType[args.type],
            build_type=BuildTypes[args.build_type],
        )
    else:
        raise ValueError(f"Invalid trainer: {args.trainer}")
