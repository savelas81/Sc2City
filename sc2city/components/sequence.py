# Imports:

# StarCraft II:
# > Bot AI:
from sc2.bot_ai import BotAI


# Classes:

class Sequence:
    # Initialization:
    def __init__(self, AI: BotAI = None, *args, **kwargs) -> None:
        # Miscellaneous:
        self.AI: BotAI = AI

