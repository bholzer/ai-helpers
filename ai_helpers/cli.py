import click
from ai_helpers.commands.generate_shell_command import generate_shell_command

@click.group()
def cli():
    pass

cli.add_command(generate_shell_command)

if __name__ == '__main__':
    cli()