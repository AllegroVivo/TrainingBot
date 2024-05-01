from __future__ import annotations
from typing import List, Optional
from typing import TYPE_CHECKING
from discord import SelectOption

from ._Enum import FroggeEnum
if TYPE_CHECKING:
    from Utilities import DataCenter
################################################################################
class GameWorld(FroggeEnum):

    Adamantoise = 1
    Alpha = 2
    Balmung = 3
    Behemoth = 4
    Bismarck = 5
    Brynhildr = 6
    Cactuar = 7
    Cerberus = 8
    Coeurl = 9
    Diabolos = 10
    Excalibur = 11
    Exodus = 12
    Faerie = 13
    Famfrit = 14
    Gilgamesh = 15
    Goblin = 16
    Halicarnassus = 17
    Hyperion = 18
    Jenova = 19
    Lamia = 20
    Leviathan = 21
    Lich = 22
    Louisoix = 23
    Maduin = 24
    Malboro = 25
    Marilith = 26
    Mateus = 27
    Midgardsormr = 28
    Moogle = 29
    Odin = 30
    Omega = 31
    Phantom = 32
    Phoenix = 33
    Ragnarok = 34
    Raiden = 35
    Ravana = 36
    Sagittarius = 37
    Sargatanas = 38
    Sephirot = 39
    Seraph = 40
    Shiva = 41
    Siren = 42
    Sophia = 43
    Spriggan = 44
    Twintania = 45
    Ultros = 46
    Zalera = 47
    Zodiark = 48
    Zurvan = 49

################################################################################
    @classmethod
    def from_xiv(cls, xiv_name: Optional[str]) -> Optional["GameWorld"]:
        
        if xiv_name is None:
            return
        
        for world in cls:
            if world.proper_name == xiv_name:
                return world
            
        raise ValueError(f"Invalid XIV world name: {xiv_name}")
    
################################################################################
    @classmethod
    def from_string(cls, world_name: str) -> Optional["GameWorld"]:
        
        for world in cls:
            if world_name.lower() == world.proper_name.lower():
                return world
    
################################################################################
    @staticmethod
    def select_options_by_dc(dc: FroggeEnum) -> List[SelectOption]:
        
        if dc.value == 1:
            world_list = [
                GameWorld.Adamantoise,
                GameWorld.Cactuar,
                GameWorld.Faerie,
                GameWorld.Gilgamesh,
                GameWorld.Jenova,
                GameWorld.Midgardsormr,
                GameWorld.Sargatanas,
                GameWorld.Siren,
            ]
        elif dc.value == 2:
            world_list = [
                GameWorld.Balmung,
                GameWorld.Brynhildr,
                GameWorld.Coeurl,
                GameWorld.Diabolos,
                GameWorld.Goblin,
                GameWorld.Malboro,
                GameWorld.Mateus,
                GameWorld.Zalera,
            ]
        elif dc.value == 3:
            world_list = [
                GameWorld.Halicarnassus,
                GameWorld.Maduin,
                GameWorld.Marilith,
                GameWorld.Seraph,
            ]
        elif dc.value == 4:
            world_list = [
                GameWorld.Behemoth,
                GameWorld.Excalibur,
                GameWorld.Exodus,
                GameWorld.Famfrit,
                GameWorld.Hyperion,
                GameWorld.Lamia,
                GameWorld.Leviathan,
                GameWorld.Ultros,
            ]
        elif dc.value == 5:
            world_list = [
                GameWorld.Alpha,
                GameWorld.Lich,
                GameWorld.Odin,
                GameWorld.Phoenix,
                GameWorld.Raiden,
                GameWorld.Shiva,
                GameWorld.Twintania,
                GameWorld.Zodiark,
            ]
        elif dc.value == 6:
            world_list = [
                GameWorld.Cerberus,
                GameWorld.Louisoix,
                GameWorld.Moogle,
                GameWorld.Omega,
                GameWorld.Phantom,
                GameWorld.Ragnarok,
                GameWorld.Sagittarius,
                GameWorld.Spriggan,
            ]
        else:
            world_list = [
                GameWorld.Bismarck,
                GameWorld.Ravana,
                GameWorld.Sephirot,
                GameWorld.Sophia,
                GameWorld.Zurvan,
            ]
            
        return [world.select_option for world in world_list]
    
################################################################################
