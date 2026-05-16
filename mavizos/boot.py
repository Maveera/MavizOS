"""Boot MavizOS: python -m mavizos.boot"""

from mavizos.os.shell.main import boot_and_shell


def main() -> None:
    boot_and_shell()


if __name__ == "__main__":
    main()
