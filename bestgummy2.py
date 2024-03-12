import discord
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable
from dataclasses import dataclass
from file_management import *
from gummy_management import *
from question_generator import *
from typing import Any
import time
import yaml
from hapen import Hapen

SLOW_MO_GAMING = 748612584231665664
LARZLAPIZ_ID = 153714363881095168
ONGOING_QUESTIONS = "ongoing_questions.pickle"
GUMMY_DATA = "gummy_data.pickle"
MATH_DATA = "math_data.pickle"
ERROR_MARGIN = 0.00001

savables = [ONGOING_QUESTIONS, GUMMY_DATA, MATH_DATA]

QuestionResponse = Callable[[], None]

@dataclass
class Question:
    sender_id: int
    question_text: str
    solution_text: str
    correct_responses: list[str]
    deadline: datetime
    reply_callback: QuestionResponse
    saved_data: Any

    async def reply(self, answer: str, bot: discord.Client, reply_channel: discord.TextChannel) -> None:
        await self.reply_callback(self, answer, bot, reply_channel) 
    
    def is_correct(self, answer: str) -> bool:
        if answer in self.correct_responses:
            return True
        try:
            answer_float = float(answer)
            for correct_response in self.correct_responses:
                if abs(eval(correct_response) - answer_float) <= ERROR_MARGIN:
                    return True

        except ValueError:
            return False
        
        return False
    
    def is_late(self):
        return datetime.now() > self.deadline
    
@dataclass
class MathStreak:
    streak: int
    guild_id: int


def generate_wrong_msg() -> str:
    incorrect_messages = ["Incorrect.", "Nice try!", "Close...", 
            "Wow... That answer is an imposter in a field of crewmates.", "Not bad, but also not good.", "no",
            "Try better next time!", "What the heck dude. That's wrong.", "frick you", "what the frick is wrong with you why can you not do basic math",
            "skill issue", "you are wrong. cry about it", "NOO!!!!!!!!!!!", "Mathematics is like a cooking recipe, and you seem to have added a pinch of dumb idiot.",
            "Dafug?", "gg get rekt nooob..", "sus... suspicious.. suspiciously wrong......", "EMERGENCY MEETING!! WRONG ANSWER DETECTED!! EJECT HIM NOW!!!!",
            "Call u an escalator, cause u let people down", "Call you JFK, cause you're completely brainless", "Call me please, because i have no friends :sob:",
            "My math teacher used to call me 'average'. How mean!", "nope nope nopety nopenope.", "turn OFF NOW", "Fr?", "Blud, You trippn on god",
            """My Grandfather smoked his whole life. I was about 10 years old when my mother said to him, 'If you ever want to see your grandchildren graduate, you have to stop immediately.'. 
            Tears welled up in his eyes when he realized what exactly was at stake. He gave it up immediately. 
            Three years later he died of lung cancer. It was really sad and destroyed me. My mother said to me- 'Don't ever smoke. Please don't put your family through what your Grandfather put us through.' I agreed. At 28, I have never touched a cigarette. 
            I must say, I feel a very slight sense of regret for never having done it, because your answer gave me cancer anyway.""",
            ":x: BAD ANSWER :x:", "MAMMA MIA, I GOT FUCKING KILLED...said Mario as he looked at your trash answer. Wait, Did mario just fucking SWEAR?!", 
            "Simply put, no. Wrong. Really, the idea of a world with you posting that answer doesn't even make any sense. Think about it... ",
            "I like you but I can't agree with you.", "Hey, my son is a huge fan of yours. Anyway over the past few days of watching you play this game hes got much better at playing baseball (he plays in the 11-13 year old division). I just wanted to stop by and thank you for teaching him how to throw so well.",
            "this blokes a bloody schewpid one innit?"]
    return random.choice(incorrect_messages)

def generate_correct_msg() -> str:
    correct_messages = ["Genius Alert", "OMG yes", "wow you are good at mathematics...", "good answer. correct answer", 
            "albert einstein would be proud!", "damn SO FKING smart", "holy h*ll thats correct", "incorrect (Jk)", "CORRECT", 
            "you are so smart", "GOOD!!!", "WTF SO INTELLIGENT", "you have 10000 iq points", "Correct Answer", "omg plz teach me math!!",
            "Albert Einstein 2.0", "Yes", "your mom so SMART when she gave birth to you, you became smart", "Oh My God that is GOOD ANSWER",
            "OK", "My mum (82F) told me (12M) to do the dishes (16) but I (12M) was too busy playing Fortnite (3 kills) so I (12M) grabbed my controller (DualShock 4) and threw it at her (138kph) and she freaking died. Reddit,AITA?",
            "yep yep yep yeppers", "Even I couldn't do that one", "How many smart gummies did you eat to solve that question", "That answer is correct",
            "all i know is 1+1=2..........", "oh yeah yeah", "OK but im still smarter than you LOL", "you are LOCKED IN my g", "O_O", "Holy FRICK!", "DANG!", 
            "perhaps you are 10000000000000000000000000 iq?", "oh my lord. let's fricking go.", "okay buddy. calm down. you are too smart.", "You're a wizard Harry",
            "YAY!!!!!!!!! U DID IT!!!!!!!!!!!!!!!!!!!", "nice", "damn... nice going there...", "no cap, u legit goated fr", "THE GOAT"]
    
    return random.choice(correct_messages)

async def gummy_answer(question: Question, answer: str, bot: discord.Client, reply_channel: discord.TextChannel) -> None:
    gummy_change = question.saved_data
    mentioner_id = gummy_change.mentioner_id
    mentioned_id = gummy_change.mentioned_id
    textchannel_id = gummy_change.channel_id

    late = question.is_late()
    

    if question.is_correct(answer) and not late:
        await reply_channel.send(generate_correct_msg())
        await bot.gummy_tracker.update_gummy(bot=bot, textchannel_id=textchannel_id, mentioner_id=mentioner_id, mentioned_id=mentioned_id)
        
        await bot.log(f'{mentioner_id} : {time.time()}')

        to_delete = []

        for questioned_id, qn in bot.ongoing_questions.items(): # remove other questioners that were trying to steal same gummy
            gummy_change = qn.saved_data
            if gummy_change.mentioned_id == mentioned_id and gummy_change.mentioner_id != mentioner_id: 

                thief = bot.get_user(mentioner_id)

                pm_channel = await bot.get_user(questioned_id).create_dm()
                await pm_channel.send(f"You were too slow! {thief.display_name} has stolen the Gummy from you!!!")
                to_delete.append(questioned_id)

                print("sending", f"You were too slow! {thief.display_name} has stolen the Gummy from you!!! to ", bot.get_user(questioned_id).display_name)
        
        bot.delete_questions(*to_delete)

        gummy = bot.gummy_tracker.get_gummy(textchannel_id=textchannel_id)
        await gummy.randomize_gummy_color(bot=bot)

        return
    
    sol_text = ""

    if late:
        sol_text += "You are late! The time limit to answer a question is 30 minute!\n\n"

    # sol_text += "You are wrong!\n\n"
    sol_text += question.solution_text
    file_name = generate_latex(sol_text)
    await reply_channel.send(content=generate_wrong_msg(), file=discord.File(file_name)) 
    

async def i_wanna_math_answer(question: Question, answer: str, bot: discord.Client, reply_channel: discord.TextChannel) -> None:
    late = question.is_late()
    sender_id = question.sender_id
    math_streak = question.saved_data

    correct_and_not_late = question.is_correct(answer) and not late

    if correct_and_not_late:
        math_streak.streak += 1

    if math_streak.streak > 0:
        bot.math_leaderboard.set_bigger_value(question.sender_id, math_streak.streak)

    if correct_and_not_late:
        new_difficulty = str(min((math_streak.streak + 1) // 5 + 1, 5))

        q = bot.generate_math_question(sender_id=sender_id, callback=i_wanna_math_answer, difficulty=new_difficulty, saved_data=math_streak)
        print(q.correct_responses)
        q.question_text = f"Correct answer! Your streak is now {math_streak.streak}!\n\nHere is the next question:\\\\\\\\" + q.question_text
        await bot.start_question(q, bot.get_user(question.sender_id))
        
        bot.save_perm_data()
        return
    
    sol_text = ""

    if late:
        sol_text += "You are late! The time limit to answer a question is 30 minutes!\n\n"
    else:
        sol_text += f"Wrong answer...\n\nYour streak ends at {math_streak.streak}.\n\n"

    sol_text += "Here is the solution:"
    sol_text += "\\\\\\\\" # newline
    sol_text += question.solution_text
    file_name = generate_latex(sol_text)
    await reply_channel.send(file=discord.File(file_name)) 


class MyClient(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        # intents.reactions = True
        intents.members = True
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        self.question_generator = QuestionGenerator()
        
        super().__init__(status="Dafug? Is hapening?", intents=intents)


    async def on_ready(self) -> None:    
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        self.setup_data()
        self.load_perm_data()
        await self.setup_log_channel()

        self.hapen = Hapen()

    async def log(self, msg: str) -> None:
        await self.log_channel.send(msg)

    async def setup_log_channel(self) -> None:
        log_channel_id = 1215510923809394718 
        self.log_channel = await self.fetch_channel(log_channel_id)
        
    def delete_questions(self, *user_ids) -> None:
        for user_id in user_ids:
            if (user_id in self.ongoing_questions):
                print("DELETING", user_id)
                del self.ongoing_questions[user_id]

    def setup_data(self) -> None:
        self.ongoing_questions = {} # user_id (int): question (Question) pairs 

        self.gummy_tracker = GummyTracker()
        self.gummy_tracker.set_channel_with_new_gummy(textchannel_id=1124506333505396808,  #test server
                                                      member_id=469483194131939329, 
                                                      gummy_role_id=698486616297308200,
                                                      guild_id=307053813271887874,
                                                      winner_role_id=1216579197212823642)
        
        self.gummy_tracker.set_channel_with_new_gummy(textchannel_id=748612584231665664,  # atlas inc
                                                      member_id=469483194131939329, 
                                                      gummy_role_id=854985438997643294,
                                                      guild_id=662774317527859236,
                                                      winner_role_id=698495425996390441)
        
        self.math_leaderboard = Ranking(players_scores={}, guild_id=None, winner_role_id=923115215674032149)
        
        self.permanent_data = PermanentData()
        self.update_perm_data()


    def update_perm_data(self) -> None:
        self.permanent_data.set(ONGOING_QUESTIONS, self.ongoing_questions)
        self.permanent_data.set(GUMMY_DATA, self.gummy_tracker)
        self.permanent_data.set(MATH_DATA, self.math_leaderboard)

    def save_perm_data(self) -> None:
        self.update_perm_data()
        self.permanent_data.save()
    
    def load_perm_data(self) -> None:
        for savable in savables:
            self.permanent_data.load(savable)

        self.ongoing_questions = self.permanent_data.get(ONGOING_QUESTIONS)
        self.gummy_tracker = self.permanent_data.get(GUMMY_DATA)
        self.math_leaderboard = self.permanent_data.get(MATH_DATA)

        print("GUMMY TRACKER LOADED:", self.gummy_tracker.all_gummies)
        print("MATH TRACKER LOADED:", self.math_leaderboard)
    
    async def export_data(self, channel: discord.TextChannel) -> None:
        for savable in savables:
            await channel.send(file=discord.File(savable))
 
    def delete_late_questions(self) -> None:
        self.delete_questions(*[user_id for user_id, question in self.ongoing_questions.items() if question.is_late()])
            
    def get_number_one_holder_id(self) -> discord.User:
        return self.get_user(self.gummy_tracker.get_gummy(SLOW_MO_GAMING).get_number_one_id())

    def generate_math_question(self, sender_id: int, callback: Callable, difficulty="1", saved_data=None) -> None:
        problem, solution_explanation, solution_value = self.question_generator.get_math_question(difficulty=difficulty)

        q = Question(
                sender_id=sender_id, 
                question_text=problem,
                solution_text=solution_explanation,
                correct_responses=[solution_value],
                deadline=datetime.now() + timedelta(minutes=30,seconds=0),
                reply_callback=callback,
                saved_data=saved_data
            )
        
        return q

    

    async def start_question(self, q: Question, to: discord.User) -> None:

        pm_channel = await self.get_user(to.id).create_dm()

        file_name = generate_latex(q.question_text)
        await pm_channel.send(file=discord.File(file_name))

        self.ongoing_questions[q.sender_id] = q

    async def check_question(self, sender: discord.Member, answer: str) -> bool: # returns if question or not
        sender_id = sender.id
        
        if sender_id not in self.ongoing_questions:
            return False
        
        q = self.ongoing_questions[sender_id]
        pm_channel = await self.get_user(sender_id).create_dm()

        self.delete_questions(sender_id)
        correct = await q.reply(answer=answer, bot=self, reply_channel=pm_channel) 

        self.save_perm_data()
        return True

    async def on_message(self, message) -> None:
        if message.author.id == self.user.id:
            return
        content = message.content
        sender = message.author
        sender_id = message.author.id
        channel = message.channel
        
        

        if isinstance(channel, discord.channel.DMChannel):
            if sender_id == LARZLAPIZ_ID and content == "export":
                await self.export_data(channel)
                return

            is_question = await self.check_question(sender, content)
            if not is_question:
                holder_string = self.gummy_tracker.generate_atlas_inc_string(self)
                holder_string += "\n"
                holder_string += "Steal it from them as soon as possible!!!!!!!!"
                await channel.send(holder_string)

        if not isinstance(channel, discord.channel.TextChannel):
            return
        
        guild_id = message.guild.id

        if self.gummy_tracker.is_gummy_channel(channel.id) and len(message.mentions) >= 1:
            mentioned = message.mentions[0]
            mentioned_id = mentioned.id
            gummy_change = GummyChange(mentioner_id=sender_id, mentioned_id=mentioned_id, channel_id=channel.id)

            if not (self.gummy_tracker.is_gummy_change_allowed(gummy_change=gummy_change)):
                return

            diff = self.gummy_tracker.get_math_difficulty(channel.id, sender_id)
            q = self.generate_math_question(sender_id=sender_id, callback=gummy_answer, difficulty=diff, saved_data=gummy_change)     
            await self.start_question(q, message.author)
            
        if (content == "hey bro show me the leaderboards") or (content == "hey bro show the leaderboards"):
            gummy_channel_id = self.gummy_tracker.get_channel_id_from_guild(message.guild.id)
            if gummy_channel_id:
                LEADERBOARD_SLOTS = 10

                gummy = self.gummy_tracker.get_gummy(gummy_channel_id)

                lb = "" 
                lb += await gummy.generate_gummy_leaderboard_string(self)

                sender_rank = self.gummy_tracker.get_gummy(gummy_channel_id).get_rank(sender_id)

                if gummy.in_ranking(sender_id) and sender_rank >= LEADERBOARD_SLOTS:
                    sender_total_hold_time = gummy.generate_user_hold_time_string(user_id=sender_id)
                    lb += "\n" + sender_total_hold_time 

                lb += "\n\n"
                lb += "The math gummy leaderboards are:\n"
                lb += self.math_leaderboard.generate_leaderboard_string(bot=self, score_unit="score", score_value_callback=lambda x: str(x))

                if (self.math_leaderboard.in_ranking(sender_id) and self.math_leaderboard.get_rank(sender_id) >= LEADERBOARD_SLOTS):

                    lb += f"\nYour score is {self.math_leaderboard.get_value(sender_id)}.... so noob......\n\n"


                await channel.send(lb) 

            
        if (content == "hey bro i want to math") or (content == "hey bro i wanna math"): 

            math_streak = MathStreak(streak=0, guild_id=guild_id)

            q = self.generate_math_question(sender_id=sender_id, callback=i_wanna_math_answer, difficulty="1", saved_data=math_streak)
            await channel.send("so you want to math huh")
            await self.start_question(q, message.author)

        print("on going questions", self.ongoing_questions)
        self.delete_late_questions()
        self.save_perm_data()
        # await self.gummy_tracker.update_roles(self)

        if "hapen" in content or "dafug" in content:
            await channel.send(self.hapen.get_random_hapen())

            
        
def main():
    client = MyClient()
    token = yaml.safe_load(open("token.yaml"))["token"]
    client.run(token) 

main()