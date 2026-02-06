import typer
import os
import sys
from dotenv import load_dotenv
from agent import Agent
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def setup(api_key: str = typer.Option(..., prompt=True, hide_input=True)):
    """
    Setup the robot with your OpenRouter API key.
    """
    with open(".env", "w") as f:
        f.write(f"OPENROUTER_API_KEY={api_key}\n")
    console.print("[green]API key saved to .env[/green]")

@app.command()
def do(instruction: str):
    """
    Execute a natural language instruction.
    """
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        console.print("[red]API key not found. Run 'robot setup' first.[/red]")
        raise typer.Exit(code=1)

    agent = Agent(api_key=api_key)
    console.print(f"[bold blue]Robot received:[/bold blue] {instruction}")
    
    try:
        agent.execute(instruction)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    app()
