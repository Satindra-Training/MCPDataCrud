from google import genai
from dotenv import load_dotenv
import os
from mcp.client.stdio import stdio_client,StdioServerParameters
from mcp import ClientSession
import streamlit as st
import asyncio
import sys

#Create an Gemini Object.
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
print("Gemini Connected")

#Streamlit GUI
st.title("Welcome to Database Agent:")
st.write('''
     Prompt Example:
         1.Add student name=Rahul 
                     email=rahul@yahoo.com
                     course=React
                     fees=32000
         2.Show/Display all students.
''')
textArea = st.text_area("Prompt:")
btn = st.button("Submit Query:")


#Connecting to mcp tools.
server = StdioServerParameters(
    command=sys.executable,
    args=["tools.py"]
)
async def connectMCP():
    async with stdio_client(server) as (read,write):
        async with ClientSession(read,write) as session:
            #Initialize all sessions.
            await session.initialize()
            #Get all available tools
            tools = await session.list_tools()
            #Converting mcp tools into gemini tools
            gemini_tools =[] #Empty list
            for tool in tools.tools:
                print(tool.name)
                gemini_tools.append({
                    "name":tool.name,
                    "description":tool.description,
                    "parameters":tool.inputSchema
                })
            #print(gemini_tools)
        #ChatLoop
            if btn:
             
             
             responses = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=textArea,
                config={
                    
                    "tools":[
                        {
                            "function_declarations":gemini_tools
                        }
                    ]
                }
            )
             #Check whether Gemini is using the tools or not.
             candidate = responses.candidates[0]
             if candidate.content.parts[0].function_call:
                tool_name = candidate.content.parts[0].function_call.name
                tool_args = dict(candidate.content.parts[0].function_call.args)
                #executing mcp tools.
                result =await session.call_tool(tool_name,tool_args)
                st.write("Agent Detected tools :",tool_name)
                st.write("Agent Final Reply :",result.content[0].text)
             else:
                st.write("Agent : I can only help with Database Automation")


asyncio.run(connectMCP())
