import google.generativeai as genai
import os
import pprint

genai.configure(api_key="AIzaSyCUhFvNw8JNmH5-17EbX2lK3XCssANVRJY")

# response = genai.chat(messages=["Hello."])
# print(response.last) #  'Hello! What can I help you with?'
# response.reply("Can you tell me a joke?")

model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("The opposite of hot is")
print(response.text)