"""MCP server command for Ecosystems CLI."""

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option("--host", default="localhost", help="Host to bind the MCP server to. Default is localhost.")
@click.option("--port", default=None, type=int, help="Port to bind the MCP server to (for HTTP transport). Default is unset.")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport protocol to use (stdio for standard I/O, http for HTTP server). Default is stdio.",
)
def mcp(host, port, transport):
    """Start an MCP (Model Context Protocol) server providing Ecosystems CLI functionality.

    This server exposes all Ecosystems CLI commands as MCP tools that can be used
    by AI assistants and other MCP clients.

    Examples:

        Start MCP server with stdio transport (default):
        $ ecosystems mcp

        Start MCP server with HTTP transport:
        $ ecosystems mcp --transport http --port 8080
    """
    from ecosystems_cli.mcp_server import run_mcp_server

    if transport == "stdio":
        console.print(
            Panel(
                "[bold green]Starting MCP server with stdio transport...[/bold green]\n"
                "The server is now ready to accept connections via standard I/O.",
                title="Ecosystems MCP Server",
                border_style="green",
            )
        )
        run_mcp_server()
    else:
        # HTTP transport would require additional implementation
        console.print(
            Panel(
                "[bold yellow]HTTP transport is not yet implemented.[/bold yellow]\n" "Please use stdio transport for now.",
                title="Not Implemented",
                border_style="yellow",
            )
        )
        raise click.ClickException("HTTP transport not yet implemented")
