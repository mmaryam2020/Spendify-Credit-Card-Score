import os
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import requests
import json
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()


def download_pdf(url, filename):
    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)


def extract_info_from_pdf(filename):
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(pages)

    return "\n".join([t.page_content for t in texts])


def process_with_gpt(text, model_name):
    template = """
    You are an AI assistant tasked with extracting cashback categories from credit card benefit documents. Your goal is to identify and list all cashback categories mentioned in the document, along with their corresponding cashback rates and any relevant conditions or limitations. You will output this information in JSON format.

    ## Input:
    The input will be the text content of a credit card benefit PDF.

    ## Instructions:
    1. Carefully read through the entire document.
    2. Identify all mentions of cashback rewards or categories.
    3. For each cashback category, extract the following information:
    - Category name (must be one of: Groceries, Gas/EV charging, Transportation, Dining, Recurring payments, Other purchases)
    - Cashback rate (e.g., 3%, 2%, 1%)
    - Any spending limits or caps on the cashback
    - Any time limitations (e.g., quarterly rotating categories)
    - Any specific conditions or exclusions

    4. Organize the extracted information into a structured JSON format.
    5. If there's a base cashback rate for all other purchases, include that under the "Other purchases" category.
    6. If there are any sign-up bonuses or welcome offers related to cashback, include those in a separate field.

    ## Output Format:
    Present the extracted information in the following JSON format:

    {{
    "cashbackCategories": [
        {{
        "categoryName": "string",
        "rate": "string",
        "limit": "string",
        "duration": "string",
        "conditions": "string"
        }}
    ],
    "welcomeOffer": "string",
    "additionalNotes": "string"
    }}

    ## Notes:
    - Only use the following category names: Groceries, Gas/EV charging, Transportation, Dining, Recurring payments, Other purchases. If a cashback category in the document doesn't exactly match these names, assign it to the closest matching category or to "Other purchases" if there's no clear match.
    - Remember to use proper JSON formatting, including double quotes around string values and property names. Ensure that the output is valid JSON that can be parsed by standard JSON libraries.
    - If there are no cashback categories or other relevant information for a particular field, you can leave it as an empty string.
    - DO NOT INCLUDE ANY OTHER INFORMATION IN THE OUTPUT. ONLY INCLUDE THE CASHBACK CATEGORIES AND RELATED DETAILS. ONLY OUTPUT THE JSON OBJECT WITH THE SPECIFIED FIELDS.

    Text content of the credit card benefit PDF:
    {text}

    JSON Output:
    """

    prompt = PromptTemplate(template=template, input_variables=["text"])

    llm = ChatOpenAI(model_name=model_name, temperature=0).bind(
        response_format={"type": "json_object"}
    )
    chain = prompt | llm

    return chain.invoke(text).content


def main(credit_card, url, model_name="gpt-3.5-turbo"):
    filename = url.split("/")[-1]

    # Download PDF
    download_pdf(url, filename)

    # Extract text from PDF
    text = extract_info_from_pdf(filename)

    # Process with GPT-3.5
    result = process_with_gpt(text, model_name)

    # Clean up
    os.remove(filename)

    # Parse the JSON string to a Python dictionary
    try:
        result_dict = json.loads(result)
        # Convert back to a formatted JSON string
        formatted_result = json.dumps(result_dict, indent=2)
        # Save the result to a file
        with open(f"{credit_card}.json", "w") as f:
            f.write(formatted_result)

        return formatted_result
    except json.JSONDecodeError:
        return (
            "Error: The model did not return valid JSON. Here's the raw output:\n"
            + result
        )


if __name__ == "__main__":
    credit_cards = [
        (
            "RBC Cash Back Mastercard",
            "https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-cash-back-mastercard/rbc-cash-back-mastercard-benefits-guide.pdf",
        ),
        (
            "BMO CashBack Mastercard",
            "https://www.bmo.com/pdf/CB%20NoFee%20MCard%20Benefits%20Guide_EN.pdf",
        ),
        (
            "CIBC Dividend Visa Card",
            "https://www.cibc.com/content/dam/personal_banking/credit_cards/agreements_and_insurance/dividend-bengd-en.pdf",
        ),
        (
            "Amex SimplyCash Preferred Card",
            "https://www.americanexpress.com/content/dam/amex/ca/en/legal/cardmember-agreement/pdf/190392-SC-SC-Preferred-CMAs-16464-Eng1.pdf",
        ),
    ]

    # MODEL_NAME = "gpt-3.5-turbo"
    MODEL_NAME = "gpt-4o"

    # Check if already processed and data is available
    for credit_card, url in credit_cards:
        if os.path.exists(f"{credit_card}.json"):
            with open(f"{credit_card}.json", "r") as f:
                result = f.read()
        else:
            result = main(credit_card, url)
