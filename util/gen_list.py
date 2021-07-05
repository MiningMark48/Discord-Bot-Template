import json
import logging

from discord.ext import commands


log = logging.getLogger("discordbot")

class Generator:
    """
    Generator class for saving all commands to a list.
    """

    def __init__(self, bot):
        """
        :param bot: Discord Bot client
        """

        self.bot = bot
        self.commands = self.bot.commands

    def fetch_list(self):
        """
        Compiles bot commands into a single list containing:
        name, aliases, type, usage, action, and hidden status

        :return: list
        """

        cmds_list = []
        for cmd in self.commands:
            subcommands = ', '.join(c.name for c in cmd.walk_commands()) if isinstance(cmd, commands.Group) else None

            cmd_o = {
                "name": str(cmd.name),
                "aliases": ", ".join(cmd.aliases),
                "type": str(cmd.cog_name),
                "usage": "--",
                "action": str(cmd.help),
                "hidden": cmd.hidden,
                "subcommands": subcommands
            }
            cmds_list.append(cmd_o)

        return sorted(cmds_list, key=lambda i: (i['name'], i['aliases'], i['type'], i['action'], i['usage']))
        # return sorted(cmds_list, key=lambda i: (i['type'], i['name'], i['aliases'], i['action'], i['usage']))

    def gen_list(self):
        """
        Generates a list of all commands to a JSON file (`commands.json`)

        Useful for a data representation of commands for manipulation.
        """

        path = "commands.json"
        with open(path, 'w') as file:
            cmds = self.fetch_list()
            json.dump(cmds, file, indent=4)
            log.info(f"Commands list generated at {path} containing {len(cmds)} commands")

    def gen_md_list(self):
        """
        Generates a list of all commands to a markdown file (`commands.md`)

        Useful for a visual representation of commands.
        """

        log.info("Beginning commands list (MD) generation")

        none_str = '--'

        def clean(string: str):
            return string.replace('|', '').replace('\n', ' ')

        path = "commands.md"
        with open(path, 'w') as file:
            all_cmds = self.fetch_list()
            # Filter out hidden commands
            cmds = list(filter(lambda c: not c['hidden'], all_cmds))

            header = "# Commands\n" \
                     "**Commands Available:** {0}\n" \
                     "| Name    | Description | Category | Aliases | Subcommands |\n" \
                     "|---------|-------------|----------|---------|-------------|"

            header = header.format(len(cmds))

            content = f"{header}\n"
            for cmd in cmds:
                cmd_name = clean(str(cmd['name']))
                cmd_desc = clean(str(cmd['action']))
                cmd_cat = clean(str(cmd['type']))
                cmd_alia = clean(str(cmd['aliases'])) if cmd['aliases'] else none_str
                cmd_sub = clean(', '.join(sorted(cmd['subcommands'].split(', ')))) if cmd['subcommands'] else none_str

                content += f"| {cmd_name} | {cmd_desc} | {cmd_cat} | {cmd_alia} | {cmd_sub} |\n"

            content += f"\n*Plus {(len(all_cmds) - len(cmds))} hidden.*\n\nThis file was automatically generated."

            file.write(content)
            log.info(f"Commands list (MD) generated at `{path}` containing `{len(cmds)}` commands")
