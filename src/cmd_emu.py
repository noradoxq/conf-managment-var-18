def main():
    vfs_name = "my_vfs"

    while True:
        try:
            user_input = input(f"\n{vfs_name}$ ")

            if not user_input.strip():
                continue

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
                    break

            else:
                print(f"ERROR: Unknown command '{command}'")

        except KeyboardInterrupt:
            print("Exiting program")
            break


if __name__ == "__main__":
    main()