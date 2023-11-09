import argparse
import json


class LowercaseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        lowercase_values = [v.lower() for v in values]
        setattr(namespace, self.dest, lowercase_values)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--moderate", nargs="*", default=[], action=LowercaseAction)
    args = parser.parse_args()

    print(json.dumps(args.moderate, indent=2))
