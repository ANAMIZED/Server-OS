"""python -m server_os.mcp — Glama stdio entry."""

from server_os.mcp.server import mcp


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
