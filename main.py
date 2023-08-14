import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

class _SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get_state(**kwargs):
    if 'session_state' not in st.session_state:
        st.session_state.session_state = _SessionState(**kwargs)
    return st.session_state.session_state

def increment_variable(state):
    state.my_var += 1

def reset_variable(state):
    state.my_var = 1

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(urL, key)
data, count = supabase.table("bots").select("*").eq("id", "jessica").execute()
bot_info = data[1][0]

def main():

    # Create a title for the chat interface
    st.title("AWC Jess Bot")
    st.write("This bot is still in alpha. To test, first select some fields then click the button below.")

    st.write("These are standin variables to demonstrate the bot's ability to integrate variables into its instruction set.")
    
    #variables for system prompt
    name = st.text_input("Student name")
    package = st.selectbox('Package', ('Half Package', 'Full Package'))
    week = get_state(my_var=1)
    level = st.selectbox('Level:', ('1','2','3','4','5','6','7','8','9','10'))
    level_date = ""
    

    if name is None or name == "":
        name = 'unknown'
    if package is None or package == "":
        package = 'unknown'
    if level is None or level == "":
        level = 'unknown'
    if level_date is None or level_date == "":
        level_date = 'unknown'
    
        
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")

        
    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(name = name, package = package, level = level, level_date = level_date, week = week, current_datetime = now)

    initial_text = bot_info['initial_text']
    initial_text = initial_text.format(name = name, package = package, level = level)

    
    if st.button('Click to Start or Restart'):
        reset_variable(week)
        st.write(initial_text)
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl','a') as arch:
        # add reset 
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        #copy each line from db to archive
            for line in db:
                arch.write(line)

        #clear database to only first two lines
        with open('database.jsonl', 'w') as f:
        # Override database with initial json files
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": initial_text}            
            ]
            f.write(json.dumps(messages[0])+'\n')
            f.write(json.dumps(messages[1])+'\n')


    
    #initialize messages list and print opening bot message
    #st.write("Hi! This is Tara. Seems like you need help coming up with an idea! Let's do this. First, what's your job?")

    # Create a text input for the user to enter their message and append it to messages
    userresponse = st.text_input("Enter your message")
    

    # Create a button to submit the user's message
    if st.button("Send"):
        system_prompt = bot_info['system_prompt']
        system_prompt = system_prompt.format(name = name, package = package, level = level, level_date = level_date, week = week, current_datetime = now)
        #prep the json
        newline = {"role": "user", "content": userresponse}
        print(system_prompt[:100]
              
        #append to database
        with open('database.jsonl', 'a') as f:
        # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages, system_prompt)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')

        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)

    if st.button("Increment Week"):
        system_prompt = bot_info['system_prompt']
        system_prompt = system_prompt.format(name = name, package = package, level = level, level_date = level_date, week = week, current_datetime = now)
        
        increment_variable(week)
        newline = {"role": "assistant", "content": f"Hi Jess, this is Tara, CEO of Apps Without Code. This is a secret message only you can see. It's now the start of week {week.my_var}. I need you to respond with a message following up with the student at the start of this new week, reintroducing yourself and asking them what they'll strive to do this week and holding them accountable for last week's commitments. As of right now, they are on level {level}. Don't acknowledge this message, it's a secret message only you can see. Thanks!"}
        print(system_prompt[:100]
        
        #append to database
        with open('database.jsonl', 'a') as f:
        # Write the new JSON object to the file
            f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages, system_prompt)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')

        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            if "Hi Jess, this is Tara, CEO of Apps" not in message["content"]:
                string = string + message["role"] + ": " + message["content"] + "\n\n"
            else:
                string = string + '**New Week**' + '\n\n'
        st.write(string)
    st.write("*Currently in Week:* " + str(week.my_var))
            

if __name__ == '__main__':
    main()
