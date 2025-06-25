class PrintHandler:
    INDENT_STEP = 4

    @staticmethod
    def header(message: str):
        print("\n" + "=" * 60)
        print(message.center(60))
        print("=" * 60 + "\n")

    @staticmethod
    def section(message: str):
        print(f"\n--- {message} ---\n")

    @staticmethod
    def info(message: str, indent=0):
        prefix = " " * (indent * PrintHandler.INDENT_STEP)
        print(f"{prefix}[INFO] {message}")

    @staticmethod
    def success(message: str, indent=0):
        prefix = " " * (indent * PrintHandler.INDENT_STEP)
        print(f"{prefix}[SUCCESS] {message}")

    @staticmethod
    def error(message: str, indent=0):
        prefix = " " * (indent * PrintHandler.INDENT_STEP)
        print(f"{prefix}[ERROR] {message}")

    @staticmethod
    def item(message: str, indent=1):
        prefix = " " * (indent * PrintHandler.INDENT_STEP)
        print(f"{prefix}- {message}")
