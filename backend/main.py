import datetime
from typing import Optional
from openai import OpenAI
import re
import random
from dataclasses import dataclass

client = OpenAI()

@dataclass
class Message:
    content: str
    sender: str
    timestamp: datetime
    isTexter: Optional[bool] = False
    

def serialize_messages(messages, include_sender=True):
    serialized_msgs = ""
    for message in messages:
        if include_sender:
            serialized_msgs += f'{message.timestamp} - {message.sender}: {message.content}\n'
        else:
            serialized_msgs += f'{message.timestamp}: {message.content}\n'
    return serialized_msgs

def generate_summary(previous_summary, past_messages):
    response = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": "You will be provided with two inputs, a summary of a text message chain, and a set of additional messages continuing on this conversation. Generate a new 5 sentence summary given these inputs. The summary should include the inferred sentiment of the participants and a shortened version of the past summary"
        }, {
            "role": "user",
            "content": f'<summary>{previous_summary}<summary/>\n<messages>{serialize_messages(past_messages)}<messages/>'
        }],
        model="gpt-4o-mini",
    )
    return response.choices[0].message.content

def generate_response(summary, user_messages, temperature):
    response = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": "You are a hypersensitive text message commentator watching your friend Christina draft a text message. You will receive a summary of the previous text messages in the conversation, a temperature level from 1-10 of how anxiety inducing your commentary should be, and a list of timestamped edits that your friend has made to their current text message. Generate a list of short comments that will make your friend feel anxious and overthink their response to the text messages, paying attention to details such as spending too long typing, drawing examples from past context to suggest that the respondee has negative feelings towards the texter, or otherwise making comments about how ill-fitting the texters responses are. "
        }, {
            "role": "user",
            "content": """Summary:
Sohum starts the conversation with a playful greeting ("Dogeeeee") and shares their thoughts on the music shared through a Spotify blend. They find the user's music nostalgic, even though it's unfamiliar, describing it as slow and reflective, with an emphasis on the quality of the voices. Sohum links a song ("Spoonful") to illustrate their point. The user responds by explaining they had been listening to more pensive and folksy music recently.
Temperature:
7
Edits:
7:51:02am - hmmm
7:51:31am - hmmm I guess not?
7:52:01am - do you want to go get some ice cream
7:52:04am - do you want to go get some ice cream?
7:52:05am - do you want to go get some ice cream??
7:52:30am - do you want to go get some coffee."""
        }, {
            "role": "assistant",
            "content": """
1. Oh no, you know "hmmm" sounds unsure, right? Like you're not vibing with their song choice at all.
2. "I guess not?" - Wow, that's a lot of uncertainty. Do you even know what you want? Sohum might think you're indecisive or uninterested.
3. Why the sudden switch from deep music talk to ice cream? It feels totally random. Sohum might feel like you're avoiding the music convo.
4. "Do you want to go get some ice cream?" - Adding a question mark was a good move, but now it's a little too eager, like you're unsure if they even want to hang out.
5. Two question marks? Are you trying too hard? Sohum might think you're desperate or overcompensating for something.
6. Switching from ice cream to coffee so quickly? It feels like you're second-guessing yourself or trying to match their vibe too much. They might notice the flip-flopping and wonder if you're trying too hard to impress.
7. You've been editing this text for a while now! Sohum can probably see you're struggling to respond. He's probably thinking about how long you're taking to respond to such a simple message.
8. Remember last time when you suggested hanging out and Sohum was slow to respond??? What if they don't even want to get coffee this time?
"""
        }, {
            "role": "user",
            "content": f"""{summary}
            Temperature: {temperature}
            {serialize_messages(user_messages)}
            """
        }],
        model="gpt-4o-mini",
    )

    # parse content & select random response
    message = response.choices[0].message.content
    message = message.replace('\n', ' ').replace('\r', '')
    parsed_lines = re.findall(r'\d+\.\s*([^\d.]+)', message)

    r = random.randint(0, len(parsed_lines) - 1)
    return parsed_lines[r]

messages = [
    Message(content="Dogeeeee", sender="Sohum", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=5)),
    Message(content="I’m going through our Spotify blend and all ur music is so nostalgic", sender="Sohum", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=4)),
    Message(content="I’ve never heard it before but it sounds like it was from a before time", sender="Sohum", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=3)),
    Message(content="Or rather slow", sender="Sohum", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=3)),
    Message(content="haha i think i was listening to a lot of pensive / folksy music", sender="Christina", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=2)),
    Message(content="lol all of our shared songs are just the ones played on our roadtrip", sender="Christina", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=1)),
]

summary = generate_summary("", messages)
user_messages = [
     Message(content="hjmmmm", sender="Christina", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=5)),
    Message(content="i don't know????", sender="Christina", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=4)),
    Message(content="i don't know??", sender="Christina", timestamp = datetime.datetime.now() - datetime.timedelta(minutes=3)),
]
response = generate_response(summary, user_messages, 7)