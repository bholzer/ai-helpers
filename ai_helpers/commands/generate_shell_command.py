import click
import os
import openai
from functools import partial
from textwrap import dedent
import json
import subprocess
from click_aliases import ClickAliasedGroup

openai.api_key = os.getenv("OPENAI_API_KEY")

click.option = partial(click.option, show_default=True)

@click.command('gsc', short_help='Generates a requested shell command')
@click.argument('prompt', type=str)
@click.option('-s', '--shell', default='zsh', help='The shell that the command should be generated for.')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Will show verbose explanation of the command from the model.')
@click.option('-m', '--model', default='gpt-3.5-turbo', help='Which chat model to use')
@click.option('-e', '--execute', is_flag=True, default=False, help='Automatically execute the generated commmand')
@click.option('-t', '--temperature', default=0.0, help='Randomness control. Lower values are more deterministic')
def generate_shell_command(prompt, shell, verbose, model, execute, temperature):
    system_prompt = dedent(f"""\
        You are a helpful assistant who will generate linux commands for {shell}.
        You will {"" if verbose else "not"} show an explanation of the command.\
        The command may be multiple lines if necessary, but short commands are preferred.
        There should be no backticks included. Only the command text should be returned.
    """)

    message_config = [
        { 'role':'system', 'content': system_prompt },
        { 'role':'user', 'content': prompt }
    ]

    res = openai.ChatCompletion.create(
        model=model,
        messages=message_config,
        temperature=temperature,
    )

    choice = res['choices'][0]
    command = choice['message']['content']


    click.echo(command)

    if verbose:
        click.echo()
        click.echo(f"Stop reason: {choice['finish_reason']}")
        click.echo(f"Usage: (prompt: {res['usage']['prompt_tokens']}) (completion: {res['usage']['completion_tokens']}) (total: {res['usage']['total_tokens']})")

    if execute:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            output = process.stdout.readline()
            print(output.strip())
            return_code = process.poll()
            if return_code is not None:
                for output in process.stdout.readlines():
                    print(output.strip())
                break

