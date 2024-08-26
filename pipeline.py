from flask import Flask, request, jsonify

app = Flask(__name__)

from categorize_request import (
    load_merchants,
    extract_merchant,
    find_best_match,
    categorize_merchant,
    CATEGORIES,
)

import json
from typing import Dict, Any
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# Define the output schema
class CreditCardInfo(BaseModel):
    categoryName: str = Field(description="The name of the category")
    rate: float = Field(description="The cashback rate as a float (e.g., 2.0 for 2%)")
    additionalInfo: str = Field(description="Any additional relevant information")


# Initialize the OpenAI model
model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0).bind(
    response_format={"type": "json_object"}
)

# Create the output parser
output_parser = PydanticOutputParser(pydantic_object=CreditCardInfo)

# Define the prompt template
prompt_template = ChatPromptTemplate.from_template(
    """You are a credit card recommendation agent. Given the credit card details, targeted category, and user query, 
    extract the relevant information and provide a recommendation.

    Credit card name: {credit_card_name}
    Targeted Category: {targeted_category}
    User query: {user_query}

    Credit card details:
    {credit_card_details}

    Based on the information provided, recommend the best option for the user. 
    If the targeted category is not directly mentioned in the cashback categories, 
    choose the most relevant category or the 'Other purchases' category.

    {format_instructions}

    An example response format is as follows:
    {{
        "categoryName": "Groceries",
        "rate": 2,
        "additionalInfo": "Cashback rate for groceries is 2% with a maximum limit of $500 per month."
    }}

    Your response should include:
    1. The category name that best matches the targeted category or user's situation
    2. The cashback rate as a float (e.g., 2.0 for 2%)
    3. Any additional relevant information, including limits, conditions, or special offers

    If the rate is not a straightforward percentage, convert it to an estimated percentage or explain it in the additionalInfo.
    """
)


def query_relevancy(query: str):
    prompt_template = ChatPromptTemplate.from_template(
        """
        # Shopping and Credit Card Benefits Classifier

        You are an AI agent designed to determine whether user's query is related to shopping and credit card benefits. Your task is to analyze the input and classify it as either relevant or not relevant to this topic.

        ## Instructions:

        1. Read the user's query carefully.
        2. Determine if the query is related to shopping, credit card usage, or credit card benefits.
        3. Provide your classification as a JSON object with the following structure:

        {{
        "is_relevant": boolean,
        "confidence": float,
        "explanation": string
        }}

        - `is_relevant`: Set to true if the query is related to shopping and credit card benefits, false otherwise.
        - `confidence`: Your confidence in the classification on a scale from 0.0 to 1.0.
        - `explanation`: A brief explanation of your classification decision.

        ## Examples:

        Input: "I'm at Metro, which credit card should I use to maximize my benefits?"
        Output:
        {{
        "is_relevant": true,
        "confidence": 0.95,
        "explanation": "The query directly asks about using a credit card for shopping to maximize benefits."
        }}

        Input: "What's the weather like today?"
        Output:
        {{
        "is_relevant": false,
        "confidence": 0.99,
        "explanation": "The query is about weather and has no relation to shopping or credit card benefits."
        }}

        Remember to always output your classification as a valid JSON object.

        User Query:
        {query}
    """
    )
    prompt = prompt_template.invoke(input={"query": query})
    response = model.predict(prompt.to_string())
    return json.loads(response)


def process_credit_card_query(
    credit_card_name: str,
    targeted_category: str,
    user_query: str,
    credit_card_details: Dict[str, Any],
) -> Dict[str, Any]:
    # Prepare the prompt
    prompt = prompt_template.format_prompt(
        credit_card_name=credit_card_name,
        targeted_category=targeted_category,
        user_query=user_query,
        credit_card_details=json.dumps(credit_card_details, indent=2),
        format_instructions=output_parser.get_format_instructions(),
    )

    # Get the response from the model
    response = model.predict(prompt.to_string())

    # Parse the response
    parsed_response = output_parser.parse(response)

    return parsed_response.dict()


@app.route("/process", methods=["POST"])
def process_json():
    data = request.get_json()

    merchants = load_merchants("merchants.csv")

    # Get user input
    # query = "I'm at Walmart and I'm doing some shopping. I was wondering which credit card I should be using to maximize my benefits."
    query = data.get("query")

    # Check if the user query is valid and actually asks questions about what credit card to use and shopping benefits
    relevancy = query_relevancy(query)
    if not relevancy["is_relevant"]:
        print(relevancy)
        return jsonify(
            {"error": "The query is not relevant to shopping and credit card benefits."}
        )

    # Extract merchant name
    merchant = extract_merchant(query)

    # Find the best match in the CSV list
    best_match = find_best_match(merchant, merchants.keys())

    if best_match:
        category = merchants[best_match.lower()]
    else:
        # If no match found, guess the category
        category = categorize_merchant(query, CATEGORIES)

    credit_cards = data.get("creditCards")
    results = []
    for credit_card in credit_cards:
        credit_card_details = json.dumps(
            json.load(open(f"{credit_card}.json", "r")), indent=2
        )

        result = process_credit_card_query(
            credit_card, category, query, credit_card_details
        )
        results.append({"creditCard": credit_card, **result})

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    # app.run(debug=True)
