import requests
import json
import subprocess
import sys
from rich.console import Console
from rich.prompt import Confirm

console = Console()

class Agent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-exp:free" # Using a free model as requested

    def execute(self, instruction: str):
        """
        Interprets the instruction and executes it.
        """
        # 1. Get the plan/code from LLM
        response = self._get_llm_response(instruction)
        
        # 2. Parse the response
        try:
            content = response['choices'][0]['message']['content']
            # Simple parsing for now - assuming the LLM returns a python script block or shell command
            # We'll ask the LLM to return JSON with 'type' and 'content'
            data = self._parse_content(content)
        except (KeyError, json.JSONDecodeError) as e:
            console.print(f"[red]Failed to parse agent response:[/red] {content}")
            return

        # 3. Confirm and Execute
        if data['type'] == 'python':
            console.print("[yellow]The agent proposes to run the following Python code:[/yellow]")
            console.print(data['content'], style="dim")
            if Confirm.ask("Run this code?"):
                self._run_python(data['content'])
            else:
                console.print("[red]Aborted.[/red]")
        elif data['type'] == 'shell':
            console.print("[yellow]The agent proposes to run the following Shell command:[/yellow]")
            console.print(data['content'], style="dim")
            if Confirm.ask("Run this command?"):
                self._run_shell(data['content'])
            else:
                console.print("[red]Aborted.[/red]")
        else:
            console.print(f"[red]Unknown action type: {data['type']}[/red]")

    def _get_llm_response(self, instruction: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "LocalRobot"
        }
        
        system_prompt = """
You are a helpful system automation agent for Windows.
Your goal is to translate natural language instructions into executable Python code or Shell (PowerShell/CMD) commands.
Return ONLY a JSON object with the following structure:
{
  "type": "python" | "shell",
  "content": "The code or command string"
}
If 'python', provide a complete, valid Python script that performs the task. Use standard libraries (os, shutil, glob, pathlib) where possible.
If 'shell', provide a single line PowerShell command.
Do not include markdown formatting like ```json ... ```. Just the raw JSON string.
        """

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction}
            ]
        }
        
        resp = requests.post(self.api_url, headers=headers, json=data)
        if resp.status_code != 200:
            raise Exception(f"API Error {resp.status_code}: {resp.text}")
            
        return resp.json()

    def _parse_content(self, content):
        # Clean up potential markdown code blocks if the model ignores the "no markdown" rule
        clean = content.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return json.loads(clean.strip())

    def _run_python(self, code):
        try:
            exec(code, {'os': os, 'sys': sys, 'subprocess': subprocess, 'print': print})
        except Exception as e:
            console.print(f"[red]Execution error:[/red] {e}")

    def _run_shell(self, cmd):
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Command failed:[/red] {e}")
