from __future__ import annotations

from typing import List

from discord import Interaction, SelectOption, User
from discord.ui import Select

from UI.Common import FroggeView, CloseMessageButton
################################################################################

__all__ = ("RemoveUserView",)

################################################################################
class RemoveUserView(FroggeView):

    def __init__(self, user: User, options: List[SelectOption]):
        
        super().__init__(user, close_on_complete=True)
        
        self.add_item(RemoveUserSelect(options))
        self.add_item(CloseMessageButton())
        
################################################################################
class RemoveUserSelect(Select):
    
    def __init__(self, options: List[SelectOption]):
                                   
        super().__init__(
            placeholder=(
                "Select the user(s) to remove..."
                if options[0].value != "-1"
                else "You can't remove yourself... Nice try tho!"
            ),
            options=options,
            min_values=1,
            max_values=len(options),
            disabled=options[0].value == "-1",
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        self.view.value = [int(i) for i in self.values]
        self.view.complete = True
        
        await interaction.edit()
        await self.view.stop()  # type: ignore
    
################################################################################
