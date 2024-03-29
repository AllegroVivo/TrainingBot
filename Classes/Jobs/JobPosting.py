from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, Type, TypeVar, Any, Dict

import pytz
from discord import User, Interaction, Embed, EmbedField, Message, NotFound

from Assets import BotEmojis
from UI.Training import WeekdaySelectView, TimeSelectView
from UI.Common import ConfirmCancelView
from UI.Jobs import (
    JobDescriptionModal,
    PositionSelectView,
    JobPostingStatusView,
    SalaryFrequencySelectView,
    SalaryModal,
    JobPostingTypeView,
)
from Utilities import (
    Utilities as U, 
    JobPostingType,
    Weekday,
    RateType,
    PostingNotCompleteError
)
from .JobHours import JobHours
from .PayRate import PayRate

if TYPE_CHECKING:
    from Classes import JobsManager, Position, Venue, TrainingBot
################################################################################

__all__ = ("JobPosting",)

JP = TypeVar("JP", bound="JobPosting")

################################################################################
class JobPosting:
    
    __slots__ = (
        "_id",
        "_mgr",
        "_venue",
        "_user",
        "_type",
        "_position",
        "_salary",
        "_start",
        "_end",
        "_description",
        "_post_msg"
    )
    
################################################################################
    def __init__(self, mgr: JobsManager, **kwargs) -> None:
        
        self._mgr: JobsManager = mgr
        
        self._id: str = kwargs.pop("_id")
        self._venue: Venue = kwargs.pop("venue")
        self._user: User = kwargs.pop("user")
        
        self._description: Optional[str] = kwargs.pop("description", None)
        self._type: Optional[JobPostingType] = kwargs.pop("type", None)
        self._position: Optional[Position] = kwargs.pop("position", None)
        self._post_msg: Optional[Message] = kwargs.pop("post_msg", None)
        
        self._salary: PayRate = kwargs.pop("salary", None) or PayRate(self)
        self._start: Optional[datetime] = kwargs.pop("start", None)
        self._end: Optional[datetime] = kwargs.pop("end", None)
        
################################################################################
    @classmethod
    def new(cls: Type[JP], mgr: JobsManager, venue: Venue, user: User) -> JP:
        
        new_id = mgr.bot.database.insert.job_posting(mgr.guild_id, venue.id, user.id)
        return cls(mgr, _id=new_id, venue=venue, user=user)
    
################################################################################
    @classmethod
    async def load(cls: Type[JP], mgr: JobsManager, record: Dict[str, Any]) -> JP:
        
        data = record["data"]
        
        self: JP = cls.__new__(cls)
        
        self._mgr = mgr
        
        self._id = data[0]
        self._venue = mgr.guild.venue_manager[data[2]]
        self._user = await mgr.bot.get_or_fetch_user(data[3])
        
        self._description = data[6]
        self._type = JobPostingType(data[4]) if data[4] else None
        self._position = mgr.guild.position_manager.get_position(data[5]) if data[5] else None

        self._post_msg = None
        if data[10] is not None:
            url_parts = data[10].split("/")
            channel = await mgr.bot.get_or_fetch_channel(int(url_parts[-2]))
            if channel is not None:
                try:
                    self._post_msg = await channel.fetch_message(int(url_parts[-1]))  # type: ignore
                except:
                    pass

        self._salary = PayRate(self, data[7], RateType(data[8]) if data[8] else None, data[9])
        self._start = data[11]
        self._end = data[12]
        
        return self
    
################################################################################
    @property
    def bot(self) -> TrainingBot:
        
        return self._mgr.bot
    
################################################################################
    @property
    def guild_id(self) -> int:
        
        return self._mgr.guild_id
    
################################################################################
    @property
    def id(self) -> str:
        
        return self._id
    
################################################################################
    @property
    def post_type(self) -> Optional[JobPostingType]:
        
        return self._type
    
    @post_type.setter
    def post_type(self, value: JobPostingType) -> None:
        
        self._type = value
        self.update()
        
################################################################################
    @property
    def description(self) -> Optional[str]:
        
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        
        self._description = value
        self.update()
        
################################################################################
    @property
    def position(self) -> Optional[Position]:
        
        return self._position
    
    @position.setter
    def position(self, value: Position) -> None:
        
        self._position = value
        self.update()
    
################################################################################    
    @property
    def post_message(self) -> Optional[Message]:
        
        return self._post_msg
    
    @post_message.setter
    def post_message(self, value: Optional[Message]) -> None:
        
        self._post_msg = value
        self.update()
        
################################################################################
    @property
    def salary(self) -> Optional[int]:
        
        return self._salary.amount
    
################################################################################    
    @property
    def frequency(self) -> Optional[RateType]:
        
        return self._salary.frequency
    
################################################################################    
    @property
    def pay_details(self) -> Optional[str]:
        
        return self._salary.details
    
################################################################################
    @property
    def start_time(self) -> Optional[datetime]:
        
        return self._start
    
    @start_time.setter
    def start_time(self, value: datetime) -> None:
        
        self._start = value
        self.update()
        
################################################################################
    @property
    def end_time(self) -> Optional[datetime]:
        
        return self._end
    
    @end_time.setter
    def end_time(self, value: datetime) -> None:
        
        self._end = value
        self.update()
        
################################################################################
    @property
    def complete(self) -> bool:
        
        return all(
            [self._type, self._position, self._salary, self._description]
        )
    
################################################################################
    def update(self) -> None:

        self.bot.database.update.job_posting(self)
        
################################################################################
    async def delete(self) -> None:
        
        if self.post_message is not None:
            try:
                await self.post_message.delete()
            except:
                pass
        
        # Oh no, being naughty and accessing a private attribute!
        self._mgr._postings.remove(self)
        self.bot.database.delete.job_posting(self)
        
################################################################################
    async def menu(self, interaction: Interaction) -> None:
        
        embed = self.status()
        view = JobPostingStatusView(interaction.user, self)
        
        await interaction.respond(embed=embed, view=view)
        await view.wait()
    
################################################################################
    def status(self) -> Embed:

        description = (
            "__**Venue Name:**__\n"
            f"`{self._venue.name}`\n\n"
            
            "__**Venue Contact:**__\n"
            f"`{self._user.name}`\n\n"

            "__**Job Description:**__\n"
            f"{self._description or '`No description provided.`'}\n\n"
            
            f"{U.draw_line(extra=30)}\n"
        )
        
        if self.post_message is None:
            description += "__**Posting URL:**__\n`Not Posted`\n\n"
        else:
            description += (
                "__**Posting URL:**__\n"
                f"{BotEmojis.ArrowRight}{BotEmojis.ArrowRight}{BotEmojis.ArrowRight} "
                f"[Click here to view the posting]({self.post_message.jump_url}) "
                f"{BotEmojis.ArrowLeft}{BotEmojis.ArrowLeft}{BotEmojis.ArrowLeft}\n\n"
            )
            
        description += f"{U.draw_line(extra=30)}\n"
        
        return U.make_embed(
            title=f"Job Posting Status",
            description=description,
            fields=[
                self._position_field(),
                self._salary_field(),
                self._post_type_field(),
                self._hours_field(),
                self._total_time_field(),
            ],
            footer_text=f"Posting ID: {self._id}",
        )
    
################################################################################
    def compile(self) -> Embed:

        description = (
            "__**Venue Contact:**__\n"
            f"`{self._user.name}`\n\n"

            "__**Job Description:**__\n"
            f"{self._description or '`No description provided.`'}\n"

            f"{U.draw_line(extra=30)}\n"
        )
        
        return U.make_embed(
            title=f"`{self.position.name}` needed at `{self._venue.name}`",
            description=description,
            fields=[
                self._position_field(),
                self._salary_field(),
                self._post_type_field(),
                self._hours_field(),
            ],
            footer_text=f"Posting ID: {self._id}",
        )
    
################################################################################
    def _post_type_field(self) -> EmbedField:
        
        return EmbedField(
            name="__Job Type__",
            value=f"{self._type.proper_name if self._type is not None else  '`Not set.`'}",
            inline=False
        )
    
################################################################################
    def _position_field(self) -> EmbedField:
        
        return EmbedField(
            name="__Position__",
            value=f"{self._position.name if self._position is not None else '`Not set.`'}",
            inline=True
        )
    
################################################################################
    def _salary_field(self) -> EmbedField:
        
        return EmbedField(
            name="__Salary__",
            value=self._salary.format(),
            inline=True
        )
    
################################################################################
    def _hours_field(self) -> EmbedField:
        
        start_ts = (
            U.format_dt(self.start_time, "F") if self.start_time is not None
            else "`Not Set`"
        )
        end_ts = (
            U.format_dt(self.end_time, "F") if self.end_time is not None
            else "`Not Set`"
        )
        
        return EmbedField(
            name="__Start Time__",
            value=(
                f"{start_ts}\n\n"
                
                f"__**End Time:**__\n"
                f"{end_ts}"
            ),
            inline=True
        )
    
################################################################################
    def _total_time_field(self) -> EmbedField:
        
        if self.start_time is not None and self.end_time is not None:
            delta = self.end_time - self.start_time
            hours = delta.total_seconds() / 3600
            field_value = f"`{hours:.2f} hours`"
        else:
            field_value = "`Invalid time range`"
        
        return EmbedField(
            name="__Total Time__",
            value=field_value,
            inline=True
        )
    
################################################################################
    async def set_description(self, interaction: Interaction) -> None:
        
        modal = JobDescriptionModal(self.description)
        
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        self.description = modal.value
    
################################################################################
    async def set_position(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="Set Job Posting Position",
            description="Please select a position for this job posting.",
        )
        view = PositionSelectView(
            interaction.user, self._mgr.guild.position_manager.select_options()
        )
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.position = self._mgr.guild.position_manager.get_position(view.value)
    
################################################################################
    async def set_salary(self, interaction: Interaction) -> None:
        
        explanation = U.make_embed(
            title="Set Job Posting Salary",
            description=(
                "__**READ THIS CAREFULLY**__\n\n"
            
                "Please provide the salary for this job posting.\n\n"
                "For the purposes of data collection and display, the salary will be "
                "collected as three different values in this order:\n\n"
                
                "1. The frequency at which the salary is paid.\n"
                "2. The amount of the salary.\n"
                "3. Any additional details about the salary.\n\n"
            )
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=explanation, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        freq_prompt = U.make_embed(
            title="Set Salary Frequency",
            description="Please select the frequency at which the salary is paid.",
        )
        view = SalaryFrequencySelectView(interaction.user)
        
        await interaction.respond(embed=freq_prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        frequency, inter = view.value
        
        modal = SalaryModal(self.salary, self.pay_details)
        
        await inter.response.send_modal(modal)
        await modal.wait()
        
        if not modal.complete:
            return
        
        rate, details, inter = modal.value
        
        self._salary = PayRate(self, rate, frequency, details)
        self.update()
    
################################################################################
    async def set_posting_type(self, interaction: Interaction) -> None:
        
        prompt = U.make_embed(
            title="Set Job Posting Type",
            description="Please select a type for this job posting.",
        )
        view = JobPostingTypeView(interaction.user)
        
        await interaction.respond(embed=prompt, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        self.post_type = view.value
    
################################################################################
    async def set_schedule(self, interaction: Interaction) -> None:

        prompt = U.make_embed(
            title="Set Job Posting Schedule",
            description=(
                "You'll now be given an opportunity to enter the start and end "
                "times for this job posting.\n\n"
                
                "You can begin this process by selecting the timezone that will "
                "correspond to your entries from the selector below."
            ),
        )
        
################################################################################
    async def create_post(self, interaction: Interaction) -> None:
        
        if not self.complete:
            error = PostingNotCompleteError()
            await interaction.respond(embed=error, ephemeral=True)
            return
        
        if self.post_message is not None:
            if await self._update_posting():
                confirm = U.make_embed(
                    title="Job Posting Updated",
                    description="The job posting has been updated."
                )
                await interaction.respond(embed=confirm, ephemeral=True)
                return
            
        confirm = U.make_embed(
            title="Post Job Listing",
            description="Are you sure you want to post this job listing?"
        )
        view = ConfirmCancelView(interaction.user)
        
        await interaction.respond(embed=confirm, view=view)
        await view.wait()
        
        if not view.complete or view.value is False:
            return
        
        channel = (
            self._mgr.temporary_jobs_channel
            if self.post_type == JobPostingType.Temporary
            else self._mgr.permanent_jobs_channel
        )
        
        try:
            self.post_message = await channel.send(embed=self.compile())
        except:
            error = U.make_embed(
                title="Posting Error",
                description="There was an error posting the job listing."
            )
            await interaction.respond(embed=error, ephemeral=True)
            return
        else:
            self.update()
            
        confirm = U.make_embed(
            title="Job Posting Created",
            description="The job posting has been created."
        )
        
        await interaction.respond(embed=confirm, ephemeral=True)
    
################################################################################
    async def _update_posting(self) -> bool:
        
        try:
            await self._post_msg.edit(embed=self.status())
        except:
            self.post_message = None
            return False
        else:
            return True
            
################################################################################
