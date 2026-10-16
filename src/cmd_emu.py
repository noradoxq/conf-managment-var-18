import argparse

from vfs import VFS


def execute_command(user_input, vfs):
    if not user_input.strip():
        return False

    parts = user_input.split()
    command = parts[0]
    args = parts[1:]

    try:
        if command == "ls":
            print("ls", *args)
        
        elif command == "cd":
            print("cd", *args)

        elif command == "pwd":
            print(vfs.pwd())

        elif command == "vfs-save":
            handle_vfs_save(args, vfs)

        elif command == "exit":
            if args:
                print("ERROR: 'exit' command does not take any arguments!")
            else:
                print("Exiting program")
                return True

        else:
            print(f"ERROR: Unknown command '{command}'")

    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")

    return False


def handle_ls(args, vfs):
    long_format = "-l" in args
    paths = [arg for arg in args if arg != "-l"]

    if len(paths) > 1:
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
    if len(args) > 1:
        print("ERROR: 'cd' accepts at most one path!")
        return

    path = args[0] if args else "/"
    vfs.change_dir(path)
    print(f"Current directory: {vfs.pwd()}")


def handle_vfs_save(args, vfs):
    if len(args) != 1:
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