from __future__ import annotations

from typing import TYPE_CHECKING, List

from discord import Interaction, SelectOption, User, ButtonStyle
from discord.ui import Button

from UI.Common import FroggeView, CloseMessageButton
from Utilities import edit_message_helper

if TYPE_CHECKING:
    from Classes import Position, GuildData
################################################################################

__all__ = ("PositionStatusView",)

################################################################################
class PositionStatusView(FroggeView):

    def __init__(self, user: User, position: Position):
        
        super().__init__(user)
        
        self.position = position
        
        button_list = [
            PositionNameButton(),  # PositionRoleButton("Trainer"), PositionRoleButton("Trainee"),
            PositionAddReqButton(), PositionRemoveReqButton(),
            CloseMessageButton()
        ]
        for btn in button_list:
            self.add_item(btn)
            
        self.set_button_style()
        
################################################################################        
    def set_button_style(self) -> None:
        
        if len(self.position.requirements) > 0:
            self.children[2].style = ButtonStyle.danger  # type: ignore
            self.children[2].disabled = False  # type: ignore
        else:
            self.children[2].style = ButtonStyle.secondary  # type: ignore
            self.children[2].disabled = True  # type: ignore
            
################################################################################
class PositionNameButton(Button):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Edit Name",
            disabled=False,
            row=0
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.position.edit_name(interaction)
        await interaction.edit(embed=self.view.position.status(), view=self.view)
        
        # If we change the name of a Position, we'll want the signup message 
        # to update as well to reflect that.
        guild: GuildData = interaction.client[interaction.guild_id]  # type: ignore
        await guild.training_manager.signup_message.update_components()
        
################################################################################
class PositionAddReqButton(Button):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.primary,
            label="Add Requirement",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.position.add_requirement(interaction)
        self.view.set_button_style()
        
        await interaction.edit(embed=self.view.position.status(), view=self.view)
        
################################################################################
class PositionRemoveReqButton(Button):
    
    def __init__(self):
        
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Requirement",
            disabled=False,
            row=1
        )
        
    async def callback(self, interaction: Interaction):
        await self.view.position.remove_requirement(interaction)
        self.view.set_button_style()
        
        await edit_message_helper(
            interaction, embed=self.view.position.status(), view=self.view
        )
        
################################################################################
