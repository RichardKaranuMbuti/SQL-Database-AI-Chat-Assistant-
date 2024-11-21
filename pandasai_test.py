from pandasai import SmartDataframe
import pandas as pd
from watson_llm import llm
from pandasai import Agent
import os

llm = llm
user_defined_path = 'media'

# Sample DataFrame
sales_by_country = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "sales": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
})

employees_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Name": ["John", "Emma", "Liam", "Olivia", "William"],
    "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
}

salaries_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Salary": [5000, 6000, 4500, 7000, 5500],
}

employees_df = pd.DataFrame(employees_data)
salaries_df = pd.DataFrame(salaries_data)


# df = SmartDataframe(sales_by_country, config={"llm": llm})
# output = df.chat('Which are the top 5 countries by sales?')
# print(output)

#Multiple datasets
# lake = SmartDatalake([employees_df, salaries_df])
# lake.chat("Who gets paid the most?")
# sdf = SmartDataframe("data/Countries.csv", config={
#     "save_charts": True,
#     "save_charts_path": user_defined_path,
# })
agent = Agent([employees_df, salaries_df],config={
    "llm": llm,
    "save_charts": True,
    "save_charts_path": user_defined_path,

}, memory_size=10)



query = "Show using a graph Who gets paid the most?"

# Chat with the agent
response = agent.chat(query)
print(response)

# # Get Clarification Questions
# questions = agent.clarification_questions(query)

# for question in questions:
#     print(question)

# # Explain how the chat response is generated
# response = agent.explain()
# print(response)