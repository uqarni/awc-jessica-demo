
import openai
import os
import re
import random

#generate openai response; returns messages with openai response
def ideator(messages, system_prompt):

  messages = messages[1:]
  messages.insert(0,{"role": "system", "content": system_prompt})
  key = os.environ.get("OPENAI_API_KEY")
  openai.api_key = key

  result = openai.ChatCompletion.create(
    model="gpt-4",
    messages= messages
  )
  response = result["choices"][0]["message"]["content"]
  
  def split_sms(message):
      import re
  
      # Use regular expressions to split the string at ., !, or ? followed by a space or newline
      sentences = re.split('(?<=[.!?]) (?=\\S)|(?<=[.!?])\n', message.strip())
      # Strip leading and trailing whitespace from each sentence
      sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
  
      # Compute the cumulative length of all sentences
      cum_length = [0]
      for sentence in sentences:
          cum_length.append(cum_length[-1] + len(sentence))
      
      total_length = cum_length[-1]
  
      # Find the splitting point
      split_point = next(i for i, cum_len in enumerate(cum_length) if cum_len >= total_length / 2)
  
      # Split the sentences into two parts at the splitting point
      part1 = sentences[:split_point]
      part2 = sentences[split_point:]
  
      # Join the sentences in each part back into strings and exclude any part that is empty
      strings = []
      if part1:
          strings.append(" ".join(part1))
      if part2:
          strings.append(" ".join(part2))
      
      return strings





  
  split_response = split_sms(response)
  count = len(split_response)
  for section in split_response:
    section = {
      "role": "assistant", 
      "content": section
    }
    messages.append(section)

  return messages, count


#prompt user with botresponse in terminal and ask for an input. returns messages with human response
#change this from input function to streamlit function
def terminaltalker(messages):

  botresponse = messages[-1]["content"]
  userresponse = input(botresponse+"\n")
  messages.append(
  {
    "role": "user",
    "content": userresponse
  }
  )
  return messages

#starts terminal conversation. Respond with exit() to exit. 
def terminalbot():
    import redis
    redis_host = os.environ.get("REDIS_1_HOST")
    redis_port = 25061
    redis_password = os.environ.get("REDIS_1_PASSWORD")
    rd = redis.Redis(host=redis_host, port=redis_port, password=redis_password, ssl=True, ssl_ca_certs="/etc/ssl/certs/ca-certificates.crt")

    system_prompt = rd.get("charli@appswithoutcode.com-systemprompt-01").decode('utf-8')
    initial_text = rd.get("charli@appswithoutcode.com-initialtext-01").decode('utf-8')
    
    #initialize message
    messages = [
          {"role": "system", "content": system_prompt},
          {"role": "assistant", "content": initial_text}]
    
    while True:
       messages = terminaltalker(messages)
       if messages[-1]["content"] == "exit()":
          break
       ideator(messages)
