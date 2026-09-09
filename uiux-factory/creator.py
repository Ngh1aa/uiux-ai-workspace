import argparse
import json
from pathlib import Path

from core.runtime.creator_mode import RuntimeCreator


ROOT = Path(__file__).resolve().parent


def print_json(payload) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="UIUX Factory runtime creator")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("inventory", help="Inspect runtime plugins and presets")

    preview = sub.add_parser("preview", help="Resolve a preset without starting a Factory run")
    preview.add_argument("preset")

    validate = sub.add_parser("validate", help="Validate one runtime preset composition")
    validate.add_argument("preset")

    copy = sub.add_parser("copy", help="Copy an existing preset into the writable user preset root")
    copy.add_argument("source")
    copy.add_argument("new_id")
    copy.add_argument("--name")
    copy.add_argument("--description")

    delete = sub.add_parser("delete", help="Delete a user-authored preset; shipped presets are immutable")
    delete.add_argument("preset")

    args = parser.parse_args()
    creator = RuntimeCreator(ROOT)

    if args.command == "inventory":
        print_json(creator.inventory())
    elif args.command == "preview":
        print_json(creator.preview(args.preset))
    elif args.command == "validate":
        print_json(creator.validate(args.preset))
    elif args.command == "copy":
        print_json(
            creator.copy_preset(
                args.source,
                args.new_id,
                name=args.name,
                description=args.description,
            )
        )
    elif args.command == "delete":
        creator.delete_preset(args.preset)
        print_json({"deleted": args.preset})


if __name__ == "__main__":
    main()
