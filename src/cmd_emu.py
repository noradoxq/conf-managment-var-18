import argparse


def execute_command(user_input):
    """главная функция с коммандами."""

    if not user_input.strip():
        return False

    parts = user_input.split()
    command = parts[0]
    args = parts[1:]

    if command == "ls":
        print("ls", *args)

    elif command == "cd":
        print("cd", *args)

    elif command == "exit":
        if args:
            print("ERROR: 'exit' command does not take any arguments!")
        else:
            print("Exiting program")
            return True

    else:
        print(f"ERROR: Unknown command '{command}'")

    return False


def execute_script(script_path, vfs_name):
    """выполняет команды из startup.txt"""

    try:
        with open(script_path, "r", encoding="utf-8") as script:
            for line in script:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                print(f"{vfs_name}$ {line}")

                should_exit = execute_command(line)

                if should_exit:
                    break

    except FileNotFoundError:
        print(f"ERROR: Startup script '{script_path}' not found!")
    except OSError as error:
        print(f"ERROR: Cannot read startup script: {error}")


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

    execute_script(args.script, vfs_name)

    while True:
        try:
            user_input = input(f"\n{vfs_name}$ ")

            if not user_input.strip():
                continue

            should_exit = execute_command(user_input)

            if should_exit:
                break

        except KeyboardInterrupt:
            print("\nExiting program")
            break
        except EOFError:
            print("\nExiting program")
            break


if __name__ == "__main__":
    main()