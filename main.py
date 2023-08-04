import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
import redis



def main():

    # Create a title for the chat interface
    st.title("AWC Jess Bot")
    st.write("This bot is still in alpha. To test, first select some fields then click the button below.")

    st.write("These are standin variables to demonstrate the bot's ability to integrate variables into its instruction set.")
    
    #variables for system prompt
    name = st.text_input("Student name")
    app_idea = st.text_input("add app idea here")
    package = st.selectbox('Package', ('Half Package', 'Full Package'))
    level = st.selectbox('Level', ('1', '2', '3'))
    week = st.selectbox('Week', ('1,', '2,', '3', '4', '5', '6', '7', '8'))



    if name is None or name == "":
        name = 'unknown'
    if app_idea is None or app_idea == "": 
        app_idea = 'unknown'
    if package is None or package == "":
        package = 'unknown'
    if level is None or level == "":
        level = 'unknown'
        
    redis_host = os.environ.get("REDIS_1_HOST")
    redis_port = 25061
    redis_password = os.environ.get("REDIS_1_PASSWORD")
    rd = redis.Redis(host=redis_host, port=redis_port, password=redis_password, ssl=True, ssl_ca_certs="/etc/ssl/certs/ca-certificates.crt")

    system_prompt = rd.get("charli@appswithoutcode.com-systemprompt-01").decode('utf-8')
    system_prompt = system_prompt.format(name = name, app_idea = app_idea, package = package, level = level)

    initial_text = rd.get("charli@appswithoutcode.com-initialtext-01").decode('utf-8')
    initial_text = initial_text.format(name = name, app_idea = app_idea, package = package, level = level)

    
    if st.button('Click to Start or Restart'):
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
        #prep the json
        newline = {"role": "user", "content": userresponse}

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
        messages, count = ideator(messages)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')



        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)
            

if __name__ == '__main__':
    main()
