from __future__ import annotations

from discord import Interaction, InputTextStyle
from discord.ui import InputText

from UI.Common import FroggeModal
################################################################################

__all__ = ("VenueNameModal",)

################################################################################
class VenueNameModal(FroggeModal):
    
    def __init__(self, cur_val: str):
        
        super().__init__(title="Edit Venue Name")
        
        self.add_item(
            InputText(
                style=InputTextStyle.multiline,
                label="Instructions",
                placeholder="Enter a new name.",
                value="Enter a new name or edit the currently existing one.",
                required=False
            )
        )
        self.add_item(
            InputText(
                style=InputTextStyle.singleline,
                label="Name",
                placeholder="eg. 'The Lilypad Lounge'",
                value=cur_val,
                max_length=40,
                required=True
            )
        )
        
    async def callback(self, interaction: Interaction):
        self.value = self.children[1].value
        self.complete = True
        
        await interaction.edit()
        self.stop()

################################################################################
