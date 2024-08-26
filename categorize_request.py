import os
import csv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import json

# Load the environment variables from the .env file
load_dotenv()

# Initialize the ChatOpenAI model
chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0).bind(
    response_format={"type": "json_object"}
)

# Define the categories
CATEGORIES = [
    "Groceries",
    "Gas/EV charging",
    "Transportation",
    "Dining",
    "Recurring payments",
    "Other purchases",
]


def load_merchants(csv_file):
    merchants = {}
    # Columns are category and name
    with open(csv_file, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            # Skip the header row
            if row[0] == "category":
                continue
            merchants[row[1].lower()] = row[0]

    return merchants


def extract_merchant(query):
    template = """
    Extract the merchant name from the following query:
    {query}
    
    Respond in JSON in the following format:
    {{
        "merchant": "string"
    }}

    """
    prompt = ChatPromptTemplate.from_template(template)
    merchant = json.loads(chat.invoke(prompt.invoke(input={"query": query})).content)[
        "merchant"
    ]
    return merchant.strip()


def find_best_match(merchant, merchant_list):
    best_match = None
    highest_ratio = 0
    for m in merchant_list:
        ratio = fuzz.ratio(merchant.lower(), m.lower())
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = m
    return best_match if highest_ratio > 80 else None


def categorize_merchant(query, categories):
    template = """
    Given the user query, categorize the merchant based on the provided categories.
    {query}

    Strictly use one of the following categories:
    {categories}
    
    Respond in JSON in the following format:
    {{
        "category": "string"
    }}
    """
    prompt = ChatPromptTemplate.from_template(template)
    response = chat.invoke(
        prompt.invoke(input={"query": query, "categories": categories})
    )
    category = json.loads(response.content)["category"]
    return category.strip()


def main():
    # Load the CSV file
    merchants = load_merchants("merchants.csv")

    # Get user input
    query = "I'm at Walmart and I'm doing some shopping. I was wondering which credit card I should be using to maximize my benefits."

    # Extract merchant name
    merchant = extract_merchant(query)
    print(f"Extracted merchant: {merchant}")

    # Find the best match in the CSV list
    best_match = find_best_match(merchant, merchants.keys())

    if best_match:
        category = merchants[best_match.lower()]
        print(f"Matched merchant: {best_match}")
        print(f"Category: {category}")
    else:
        # If no match found, guess the category
        category = categorize_merchant(query, CATEGORIES)
        print(f"No exact match found. Guessed category: {category}")


if __name__ == "__main__":
    main()
