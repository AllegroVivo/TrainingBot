from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Any, Tuple, Dict

from discord import Interaction, Embed, EmbedField, SelectOption
from discord.ext.pages import Page

from Assets import BotEmojis, BotImages
from UI.Common import ConfirmCancelView
from Utilities import Utilities as U, NS
from .AdditionalImage import AdditionalImage
from .ProfileSection import ProfileSection
from UI.Profiles import (
    ImageFrogginator,
    AdditionalImageView, 
    AdditionalImageCaptionModal,
    ProfileImageStatusView,
    AdditionalImageSelectView
)

if TYPE_CHECKING:
    from Classes import Profile
################################################################################

__all__ = ("ProfileImages",)

PI = TypeVar("PI", bound="ProfileImages")

################################################################################
class ProfileImages(ProfileSection):
    
    __slots__ = (
        "_thumbnail",
        "_main_image",
        "_additional"
    )

################################################################################
    def __init__(self, parent: Profile, **kwargs) -> None:
        
        super().__init__(parent)

        self._thumbnail: Optional[str] = kwargs.pop("thumbnail", None)
        self._main_image: Optional[str] = kwargs.pop("main_image", None)
        self._additional: List[AdditionalImage] = kwargs.pop("additional", None) or []
        
################################################################################
    @classmethod
    def load(
        cls: Type[PI],
        parent: Profile, 
        data: Tuple[Any, ...],
        additional: List[Tuple[Any, ...]]
    ) -> PI:
        
        self: PI = cls.__new__(cls)
        
        self._parent = parent
        
        self._thumbnail = data[0]
        self._main_image = data[1]
        self._additional = [
            AdditionalImage(parent=self, _id=i[0], url=i[2], caption=i[3])
            for i in additional
        ]

        return self
    
################################################################################
    @property
    def thumbnail(self) -> Optional[str]:
        
        return self._thumbnail
    
################################################################################    
    @thumbnail.setter
    def thumbnail(self, value: Optional[str]) -> None:
        
        self._thumbnail = value
        self.update()
        
################################################################################
    @property
    def main_image(self) -> Optional[str]:
        
        return self._main_image
    
################################################################################
    @main_image.setter
    def main_image(self, value: Optional[str]) -> None:
        
        self._main_image = value
        self.update()
        
################################################################################
    @property
    def additional(self) -> List[AdditionalImage]:
        
        return self._additional

################################################################################
    def update(self) -> None:
        
        self.parent.bot.database.update.profile_images(self)
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = ProfileImageStatusView(interaction.user, self)
        
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()

################################################################################
    def status(self) -> Embed:

        down_arrow = BotEmojis.ArrowDown
        right_arrow = BotEmojis.ArrowRight

        fields: List[EmbedField] = [
            EmbedField(U.draw_line(extra=30), "** **", False),
            self.additional_status(),
            EmbedField(U.draw_line(extra=30), "** **", False),
            EmbedField(
                name="__Main Image__",
                value=f"-{down_arrow}{down_arrow}{down_arrow}-",
                inline=True
            ),
            EmbedField("** **", "** **", True),
            EmbedField(
                name="__Thumbnail__",
                value=f"-{right_arrow}{right_arrow}{right_arrow}-",
                inline=True
            ),
        ]

        return U.make_embed(
            color=self.parent.color,
            title=f"Image Details for `{self.parent.char_name}`",
            description=(
                "The buttons below allow you to remove and image attached to your profile\n"
                "or to view a paginated list of your current additional images.\n\n"

                "***To change your thumbnail and main image assets, or to add an additional image\n"
                "to your profile, use the `/profiles add_image` command.***"
            ),
            thumbnail_url=self._thumbnail or BotImages.ThumbnailMissing,
            image_url=self._main_image or BotImages.MainImageMissing,
            timestamp=False,
            fields=fields
        )

################################################################################
    def additional_status(self) -> EmbedField:

        if not self.additional:
            return EmbedField(
                name="__Additional Images__",
                value=str(NS),
                inline=False
            )

        return self.compile_additional()

################################################################################
    def compile_additional(self) -> Optional[EmbedField]:

        if not self.additional:
            return

        images_text = ""
        for image in self.additional:
            images_text += f"{image.compile()}\n"

        return EmbedField(
            name=f"{BotEmojis.Camera} __Additional Images__ {BotEmojis.Camera}",
            value=images_text,
            inline=False
        )

################################################################################
    async def remove_thumbnail(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            color=self.parent.color,
            title="Confirm Image Removal",
            description=(
                "Confirm that you want to remove the attached image from the "
                "corresponding spot on your profile.\n\n"

                "*(It's gone forever and you'll need to re-upload it again if "
                "you change your mind!)*"
            ),
            thumbnail_url=self.thumbnail,
            timestamp=False
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.response.send_message(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return
        
        self.thumbnail = None
    
################################################################################
    async def remove_main_image(self, interaction: Interaction) -> None:

        confirm = U.make_embed(
            color=self.parent.color,
            title="Confirm Image Removal",
            description=(
                "Confirm that you want to remove the attached image from the "
                "corresponding spot on your profile.\n\n"

                "*(It's gone forever and you'll need to re-upload it again if "
                "you change your mind!)*"
            ),
            image_url=self.main_image,
            timestamp=False
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.response.send_message(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.main_image = None

################################################################################
    def _manage_additional_embed(self, image: Optional[AdditionalImage]) -> Embed:
        
        if image is None:
            image = self.additional[0]
        
        return U.make_embed(
            color=self.parent.color,
            title="Additional Images Management",
            description=(
                "Use the select box below to select an additional image to edit or remove."
            ),
            footer_text=f"Caption: {str(image.caption)}",
            image_url=image.url
        )
        
################################################################################
    async def manage_additional(
        self, 
        interaction: Interaction,
        image: AdditionalImage = None
    ) -> None:
        
        prompt = self._manage_additional_embed(image)
        view = AdditionalImageSelectView(interaction.user, self, image)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        addl_image = self.get_additional(view.value)
        await self.manage_additional(interaction, addl_image)

################################################################################
    def _additional_image_options(self) -> List[SelectOption]:
        
        ret = []
        
        for img in self.additional:
            image_name = img.url.split("/")[-1].split("?")[0]
            if len(image_name) >= 95:
                image_name = f"{image_name[:95]}..."
            
            ret.append(
                SelectOption(
                    label=img.caption or "No Caption Provided",
                    value=img.id,
                    description=image_name
                )
            )
            
        return ret
        
################################################################################
    def get_additional(self, image_id: str) -> Optional[AdditionalImage]:

        for img in self.additional:
            if img.id == image_id:
                return img
            
################################################################################
    async def remove_additional(self, interaction: Interaction, additional: AdditionalImage) -> None:

        confirm = U.make_embed(
            color=self.parent.color,
            title="Confirm Image Removal",
            description=(
                "Confirm that you want to remove the attached image from the "
                "corresponding spot on your profile.\n\n"

                "*(It's gone forever and you'll need to re-upload it again if "
                "you change your mind!)*"
            ),
            image_url=additional.url,
            timestamp=False
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.response.send_message(embed=confirm, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.additional.remove(additional)
        additional.delete()

################################################################################
    def set_thumbnail(self, url: str) -> None:

        self.thumbnail = url
        
################################################################################
    def set_main_image(self, url: str) -> None:

        self.main_image = url
        
################################################################################
    async def add_additional(self, interaction: Interaction, url: str, caption: Optional[str]) -> None:
        
        self.additional.append(
            AdditionalImage.new(parent=self, url=url, caption=caption)
        )

        confirm = U.make_embed(
            color=self.color,
            title="Image Assigned",
            description=(
                f"The additional image has been assigned to your profile.\n"
                "Run the `/staffing profile` command to view the changes!"
            )
        )
        await interaction.respond(embed=confirm, ephemeral=True)
        
################################################################################
    def progress(self) -> str:

        em_thumb = self.progress_emoji(self._thumbnail)
        em_main = self.progress_emoji(self._main_image)
        em_addl = self.progress_emoji(self.additional)

        return (
            f"{U.draw_line(extra=15)}\n"
            "__**Images**__\n"
            f"{em_thumb} -- Thumbnail *(Upper-Right)*\n"
            f"{em_main} -- Main Image *(Bottom-Center)*\n"
            f"{em_addl} -- (`{len(self.additional)}`) -- Additional Images\n"
        )

################################################################################
    def compile(self) -> Tuple[Optional[str], Optional[str], Optional[EmbedField]]:

        return (
            self.thumbnail,
            self.main_image,
            self.compile_additional()
        )

################################################################################
    def _to_dict(self) -> Dict[str, Any]:
        
        return {
            "thumbnail": self.thumbnail,
            "main_image": self.main_image,
            "additional": [i._to_dict() for i in self.additional]
        }
    
################################################################################
