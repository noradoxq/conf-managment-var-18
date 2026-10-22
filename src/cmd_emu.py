import argparse
import os

from vfs import VFS

DEFAULT_HEAD_LINES = 10

MAX_PATHS = 1
MAX_ARGUMENTS = 1
REV_ARGUMENTS = 1
HEAD_ARGUMENTS = 1
HEAD_N_ARGUMENTS = 3
CP_ARGUMENTS = 2
VFS_SAVE_ARGUMENTS = 1

MIN_LINE_COUNT = 0

def execute_command(user_input, vfs):
    if not user_input.strip():
        return False
    parts = user_input.split()
    command = parts[0]
    args = parts[1:]
    handlers = {
        "ls": lambda: handle_ls(args, vfs),
        "cd": lambda: handle_cd(args, vfs),
        "pwd": lambda: print(vfs.pwd()),
        "vfs-save": lambda: handle_vfs_save(args, vfs),
        "rev": lambda: handle_rev(args, vfs),
        "head": lambda: handle_head(args, vfs),
        "clear": lambda: handle_clear(args),
        "exit": lambda: handle_exit(args),
    }
    try:
        handler = handlers.get(command)
        if handler is None:
            print(f"ERROR: Unknown command '{command}'")
            return False
        result = handler()
        return result is True
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return False


def handle_exit(args):
    if args:
        print("ERROR: 'exit' command does not take any arguments!")
        return False

    print("Exiting program")
    return True



def handle_ls(args, vfs):
    long_format = "-l" in args
    paths = [arg for arg in args if arg != "-l"]

    if len(paths) > MAX_PATHS:
        print("ERROR: 'ls' accepts at most one path!")
        return

    path = paths[0] if paths else "."
    entries = vfs.list_dir(path)

    if long_format:
        for entry in entries:
            print(entry)
    else:
        print(*entries)


def handle_cd(args, vfs):
    if len(args) > MAX_PATHS:
        print("ERROR: 'cd' accepts at most one path!")
        return

    path = args[0] if args else "/"
    vfs.change_dir(path)
    print(f"Current directory: {vfs.pwd()}")

def handle_rev(args, vfs):
    if len(args) != REV_ARGUMENTS:
        print("ERROR: Usage: rev <file>")
        return

    content = vfs.read_file(args[0]).decode("utf-8")

    for line in content.splitlines():
        print(line[::-1])


def handle_head(args, vfs):
    line_count = DEFAULT_HEAD_LINES

    if not args:
        print("ERROR: Usage: head [-n count] <file>")
        return

    if args[0] == "-n":
        if len(args) != HEAD_N_ARGUMENTS:
            print("ERROR: Usage: head -n <count> <file>")
            return

        try:
            line_count = int(args[1])
        except ValueError:
            print("ERROR: Line count must be an integer")
            return

        if line_count < 0:
            print("ERROR: Line count cannot be negative")
            return

        file_path = args[2]
    else:
        if len(args) != HEAD_ARGUMENTS:
            print("ERROR: Usage: head [-n count] <file>")
            return

        file_path = args[0]

    content = vfs.read_file(file_path).decode("utf-8")
    lines = content.splitlines()

    for line in lines[:line_count]:
        print(line)


def handle_clear(args):
    if args:
        print("ERROR: 'clear' does not take arguments!")
        return

    os.system("cls" if os.name == "nt" else "clear")


def handle_vfs_save(args, vfs):
    if len(args) != VFS_SAVE_ARGUMENTS:
        print("ERROR: Usage: vfs-save <path>")
        return

    vfs.save(args[0])
    print(f"VFS saved to '{args[0]}'")


def execute_script(script_path, vfs_name, vfs):
    try:
        with open(script_path, "r", encoding="utf-8") as script:
            for line in script:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                print(f"{vfs_name}$ {line}")

                if execute_command(line, vfs):
                    return True

    except (OSError, UnicodeError) as error:
        print(f"ERROR: Cannot read startup script: {error}")

    return False


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="VFS emulator"
    )

    parser.add_argument(
        "--vfs",
        required=True,
        help="Path to physical VFS location"
    )

    parser.add_argument(
        "--script",
        required=True,
        help="Path to startup script"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    vfs_name = "my_vfs"

    print("=== Emulator parameters ===")
    print(f"VFS path:    {args.vfs}")
    print(f"Script path: {args.script}")
    print("===========================")

    try:
        vfs = VFS(args.vfs)
    except (OSError, ValueError) as error:
        print(f"ERROR: Cannot load VFS: {error}")
        return

    if execute_script(args.script, vfs_name, vfs):
        return

    while True:
        try:
            user_input = input(f"\n{vfs_name}$ ")

            if execute_command(user_input, vfs):
                break

        except (KeyboardInterrupt, EOFError):
            print("\nExiting program")
            break


if __name__ == "__main__":
    main()