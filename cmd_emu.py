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
                print('\n', "ls", *args)

            elif command == "cd":
                print('\n', "cd", *args)

            elif command == "exit":
                if args:
                    print('\n', "ERROR: 'exit' command does not take any arguments")
                else:
                    print('\n', "Exiting program")
                    break

            else:
                print(f"\nERROR: Unknown command '{command}'")

        except KeyboardInterrupt:
            print('\n', "Exiting program")
            break


if __name__ == "__main__":
    main()