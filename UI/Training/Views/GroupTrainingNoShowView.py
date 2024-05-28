from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord import Interaction, SelectOption, User
from discord.ui import Select

from UI.Common import FroggeView, CloseMessageButton
from Utilities import TrainingLevel

if TYPE_CHECKING:
    pass
################################################################################

__all__ = ("GroupTrainingNoShowView",)

################################################################################
class GroupTrainingNoShowView(FroggeView):

    def __init__(self, user: User, trainees: List[SelectOption]):
        
        super().__init__(user, close_on_complete=True)
        
        self.add_item(TraineeSelect(trainees))
        self.add_item(CloseMessageButton())
        
################################################################################
class TraineeSelect(Select):
    
    def __init__(self, options: List[SelectOption]):
        
        if not options:
            options.append(SelectOption(label="None", value="-1"))
                                   
        super().__init__(
            placeholder="Select any No-Show trainees...",
            options=options,
            min_values=1,
            max_values=len(options),
            disabled=True if options[0].value == "-1" else False,
            row=0
        )
        
        self.options = options
        
    async def callback(self, interaction: Interaction):
        self.view.value = self.values
        self.view.complete = True

        await interaction.edit()
        await self.view.stop()  # type: ignore
    
################################################################################
