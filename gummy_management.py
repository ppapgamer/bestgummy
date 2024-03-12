import discord
from datetime import datetime
from dataclasses import dataclass
from file_management import *
from misc import *
from typing import Optional, Callable
import math
import random

SLOW_MO_GAMING = 748612584231665664

@dataclass
class Ranking:
    players_scores: dict[int: int] # {user_id: int, count: int}
    guild_id: int
    winner_role_id: int #number one player holds this role 

    def in_ranking(self, user_id: int) -> bool:
        return user_id in self.players_scores
    
    def get_number_one_id(self) -> int:
        if len(self.players_scores) == 0:
            return None
        max_holder_id = max(zip(self.players_scores.values(), self.players_scores.keys()))[1]
        
        return max_holder_id
    
    def get_rank(self, user_id: int) -> int:
        sorted_holder_times = self.get_sorted_holder_times()
        for i, (holder_id, holder_time) in enumerate(sorted_holder_times):
            if holder_id == user_id:
                return i
        return None
    
    def set_value(self, user_id: int, value: int) -> None:
        self.players_scores[user_id] = value

    def get_value(self, user_id: int) -> int:
        if not self.in_ranking(user_id):
            return 0
        return self.players_scores[user_id]

    def set_bigger_value(self, user_id: int, value: int) -> None:
        self.set_value(user_id, max(value, self.get_value(user_id)))
        
    def generate_leaderboard_string(self, bot: discord.Client, score_unit: str, score_value_callback: Callable) -> None:
        sorted_holder_times = self.get_sorted_holder_times()

        s = ""

        for i, (holder_id, holder_time) in enumerate(sorted_holder_times):
            if i >= 10:
                break

            leaderboard_user = bot.get_user(holder_id)
            s += f"{i+1}: {leaderboard_user.name} with a {score_unit} of {score_value_callback(holder_time)}"
            s += "\n"

        return s

    def get_sorted_holder_times(self) -> tuple[int, int]:
        return sorted(self.players_scores.items(), key=lambda x:x[1], reverse=True) 


@dataclass
class GummyChange:
    mentioner_id: int
    mentioned_id: int
    channel_id: int

@dataclass
class Gummy(Ranking):
    holder_id: int
    held_from: datetime
    role_id: int 
    # players_scores: dict[int, int] 
    # guild_id: int
    # holder_times: dict[int, int]

    async def set_gummy_color(self, bot: discord.Client, color: discord.Color) -> None:
        guild = bot.get_guild(self.guild_id)
        role = guild.get_role(self.role_id)
        await role.edit(color=color, reason="GUMMY TENDENCIES")

    async def randomize_gummy_color(self, bot: discord.Client) -> None:
        await self.set_gummy_color(bot=bot, color=random.randint(0, 0xFFFFFF))

    def add_holder_time(self, old_holder_id: int, duration: int):
        if old_holder_id not in self.players_scores:
                self.players_scores[old_holder_id] = 0

        self.players_scores[old_holder_id] += duration

    def get_held_time_seconds(self) -> int:
        return seconds_between(self.held_from, datetime.now())
    
    def get_total_held_time_seconds(self, user_id: int) -> int:
        return self.players_scores[user_id]

    def update_holder(self, new_holder_id: int):
        held_time = self.get_held_time_seconds()
        self.held_from = datetime.now()
        self.add_holder_time(self.holder_id, held_time)
        self.holder_id = new_holder_id

        # print("Updated holder to", new_holder_id, "with a time of", held_time, "seconds")

    async def get_guild_member_data(self, bot: discord.Client):
        guild = await bot.fetch_guild(self.guild_id)
        holder_member = await guild.fetch_member(self.holder_id)
        role = guild.get_role(self.role_id)

        return guild, holder_member, role        
    


    async def generate_gummy_leaderboard_string(self, bot: discord.Client) -> str:
        s = "The bestgummy leaderboards are:\n\n"
        s += self.generate_leaderboard_string(bot=bot, score_unit="time", score_value_callback=second_to_str)
        s += "\n"
        s += self.generate_holder_string(bot=bot)
            
        return s
    
    def generate_holder_string(self, bot: discord.Client) -> str:
        s = ""

        s += f"The current Atlas Inc. Best Gummy holder is {bot.get_user(self.holder_id)}.\n" 
        s += f"They've had it for {second_to_str(self.get_held_time_seconds())}. Great job!!!!!!!! :)"

        return s
    
    def generate_user_hold_time_string(self, user_id) -> str:

        total_hold_time = self.get_total_held_time_seconds(user_id)

        s = f"Your time is {second_to_str(total_hold_time)}... so noob"
        return s 
    


class GummyTracker:

    def __init__(self) -> None:
        self.all_gummies = {} # {channel_id [int], gummy_holder [Gummy]}

    def is_gummy_channel(self, textchannel_id: int) -> bool:
        return textchannel_id in self.all_gummies
    
    def get_gummy(self, textchannel_id: int) -> Optional[bool]:
        if not self.is_gummy_channel(textchannel_id):
            return None
        return self.all_gummies[textchannel_id]

    def set_channel_with_new_gummy(self, textchannel_id: int, member_id: int, gummy_role_id: int, guild_id: int, winner_role_id: int) -> None:
        gummy = Gummy(holder_id=member_id, 
                      held_from=datetime.now(), 
                      role_id=gummy_role_id, 
                      players_scores={}, 
                      guild_id=guild_id,
                      winner_role_id=winner_role_id)
        
        self.set_channel(textchannel_id, gummy) 

    def get_gummy_guild_id(self, textchannel_id: int) -> int:
        return self.all_gummies[textchannel_id].guild_id
    
    def get_channel_id_from_guild(self, guild_id: int) -> Optional[int]:
        for textchannel_id, gummy in self.all_gummies.items():
            if gummy.guild_id == guild_id:
                return textchannel_id
        return None 
    
    def set_channel(self, textchannel_id: int, init_gummy: Gummy) -> None:
        self.all_gummies[textchannel_id] = init_gummy

    def transfer_gummy(self, textchannel_id: int, mentioner_id: int, mentioned_id: int) -> Optional[Gummy]:
        if textchannel_id not in self.all_gummies:
            return 
        current_gummy = self.all_gummies[textchannel_id]

        if current_gummy.holder_id == mentioned_id:
            current_gummy.update_holder(mentioner_id)
            return current_gummy
    
    async def update_gummy(self, bot: discord.Client, textchannel_id: int, mentioner_id: int, mentioned_id: int) -> None: # with roles
        new_gummy = self.transfer_gummy(textchannel_id=textchannel_id, mentioner_id=mentioner_id, mentioned_id=mentioned_id)
        if new_gummy:
            await self.simply_update_roles(bot=bot, gummy=new_gummy, old_holder_id=mentioned_id)
    

    async def simply_update_roles(self, bot: discord.Client, gummy: Gummy, old_holder_id: int):
        guild, holder_member, role = await gummy.get_guild_member_data(bot)
        old_holder = await guild.fetch_member(old_holder_id)
        print("Removing role from", old_holder)

        await old_holder.remove_roles(role, reason="lost best gummy...")
        await holder_member.add_roles(role, reason="got best gummy!!")

    async def force_update_roles(self, bot: discord.Client) -> None:
        for gummy in self.all_gummies.values():
            guild, holder_member, role = await gummy.get_guild_member_data(bot)

            async for other_member in guild.fetch_members(limit=1000):
                if role in other_member.roles:
                    await other_member.remove_roles(role, reason="lost best gummy...")

            await holder_member.add_roles(role, reason="got best gummy!!")


    def generate_atlas_inc_string(self, bot: discord.Client) -> str:        
        return self.all_gummies[SLOW_MO_GAMING].generate_holder_string(bot)

    
    def is_gummy_change_allowed(self, gummy_change: GummyChange) -> bool:
        if (gummy_change.channel_id not in self.all_gummies):
            return False
        gummy = self.all_gummies[gummy_change.channel_id]
        return gummy.holder_id == gummy_change.mentioned_id and gummy_change.mentioned_id != gummy_change.mentioner_id
    
    def get_math_difficulty(self, textchannel_id: int, user_id: int):
        if (textchannel_id not in self.all_gummies):
            raise Exception(f"{textchannel_id} is not a gummy channel")
        gummy = self.all_gummies[textchannel_id]
        if user_id not in gummy.players_scores:
            return "1"
        sec_held = gummy.players_scores[user_id]
        hours_held = sec_held/3600.0
        diff = max(min(math.ceil(hours_held ** 0.6), 5), 1)
        return str(int(diff))

