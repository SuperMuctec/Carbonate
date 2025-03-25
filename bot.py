
import pathlib

import discord
from discord.ext import commands


def find_all_modules_in_directory(directory: pathlib.Path) -> list[str]:
    """
    Find all modules in a directory
    
    Params:
        directory (pathlib.Path): Directory to search
    
    Returns:
        list[str]: List of module names (without prefix) what prefix?
    """
    modules = []
    for file_or_dir in directory.iterdir():
        if file_or_dir.is_file() and file_or_dir.name.endswith(".py"):
            modules.append(file_or_dir.stem)
        elif file_or_dir.is_dir() and file_or_dir.name != "__pycache__":
            init_file = file_or_dir / "__init__.py"
            if init_file.is_file():
                modules.append(file_or_dir.stem)
    return modules


class Carbonate(commands.Bot):
    """
    Carbonate's custom bot class
    Loads extensions from an initial list.
    """
    def __init__(self, command_prefix: str = "!", intents: discord.Intents = discord.Intents.all(), initial_extensions: list = None, **options):
        super().__init__(command_prefix, intents=intents, **options)
        self._initial_extensions = initial_extensions
    
    async def setup_hook(self):
        if self._initial_extensions is not None:
            for extension in self._initial_extensions:
                try:
                    await self.load_extension(extension)
                except Exception as e:
                    print(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

