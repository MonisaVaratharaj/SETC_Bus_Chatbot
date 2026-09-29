from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from fuzzywuzzy import process
import re

app = Flask(__name__)

# Get the folder where this Python file is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------------
# Load route data from CSV
# -------------------------------------------------------------------
csv_file_path = os.path.join(BASE_DIR, "cleaned_data.csv")
data = pd.read_csv(csv_file_path)

unique_locations = pd.concat([data["From"], data["To"]]).dropna().unique()
unique_locations_df = pd.DataFrame(unique_locations, columns=["Location"])
unique_locations_df["Location"] = unique_locations_df["Location"].astype(str).str.lower()


# -------------------------------------------------------------------
# Load chatbot training data from JSON
# -------------------------------------------------------------------
json_file_path = os.path.join(BASE_DIR, "data.json")


def load_training_data(file_path):
    """Load training data from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            return json_data.get("data", [])

    except FileNotFoundError:
        print(f"Error: The file at {file_path} does not exist.")
        return []

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

    except Exception as e:
        print(f"An unexpected error occurred while loading the JSON file: {e}")
        return []


training_data = load_training_data(json_file_path)


# -------------------------------------------------------------------
# General chatbot response
# -------------------------------------------------------------------
def find_response(user_query):
    """Find a predefined chatbot response from data.json."""
    user_query = user_query.lower().strip()

    for item in training_data:
        # Your JSON contains both "User" and a few "user" keys.
        question = item.get("User", item.get("user", ""))

        if question.lower().strip() == user_query:
            return item.get("Example", "No specific response found.")

    return "No data available or query was irrelevant."


# -------------------------------------------------------------------
# Route search
# -------------------------------------------------------------------
def find_location(query):
    """Find route information based on origin and destination."""
    query = query.strip()
    words = query.lower().split()

    location_matches = {
        word: process.extractOne(
            word,
            unique_locations_df["Location"].values,
            score_cutoff=80
        )
        for word in words
    }

    to_index = words.index("to") if "to" in words else -1

    from_location = None
    to_location = None

    for word, match in location_matches.items():
        if match:
            word_index = words.index(word)

            if to_index != -1 and word_index > to_index:
                to_location = match[0]

            elif to_index == -1 or word_index < to_index:
                from_location = match[0]

    if not from_location or not to_location:
        return "No complete route data found in your query."

    result = data[
        (data["From"].astype(str).str.lower() == from_location.lower())
        & (data["To"].astype(str).str.lower() == to_location.lower())
    ]

    if result.empty:
        return f"No route from {from_location} to {to_location} found."

    return format_result(result, query)


# -------------------------------------------------------------------
# Format route result
# -------------------------------------------------------------------
def format_result(result, query):
    """Format selected route attributes as HTML."""
    columns_to_display = extract_attributes(query, result)

    # Keep only columns that actually exist in the CSV.
    columns_to_display = [
        col for col in columns_to_display if col in result.columns
    ]

    attribute_values = {col: set() for col in columns_to_display}

    for _, row in result.iterrows():
        for col in columns_to_display:
            attribute_values[col].add(row[col])

    formatted_result = ""

    for col, values in attribute_values.items():
        formatted_result += (
            f"<strong>{col}:</strong> "
            + ", ".join(map(str, values))
            + "<br>"
        )

    return formatted_result.strip()


# -------------------------------------------------------------------
# Detect which route attributes the user requested
# -------------------------------------------------------------------
def extract_attributes(query, result):
    """Extract requested route attributes from the user's query."""
    query = query.lower()

    patterns = {
        "Depot": r"depots?|central depot|central|depot",
        "Route No.": r"route number|route no\.?|routes?|route",
        "From": r"from|departure points?|departing from|depart",
        "To": r"to|destinations?|arrival points?|arriving at",
        "Route Length": r"route length|length|distance",
        "Type": r"types?|kind|kinds|categories?|class(es)?|buses?|bus type|bus category",
        "No. of Service": r"services?|number of services?|number of buses?|no\.? of buses?|no\.? of services?|available service",
        "Departure Timings": r"departure timings?|timings?|departure times?|time|timing",
        "All": r"details|all data|whole",
    }

    attribute_names = []

    for attribute, pattern in patterns.items():
        if re.search(pattern, query):
            attribute_names.append(attribute)

    if "All" in attribute_names or not attribute_names:
        return list(result.columns)

    return attribute_names


# -------------------------------------------------------------------
# Convert a user query into a chatbot response
# -------------------------------------------------------------------
def process_query(user_query):
    """Process a chatbot query using route data or predefined responses."""
    user_query = user_query.strip()

    if not user_query:
        return "Please enter a query."

    query_lower = user_query.lower()

    # Preserve the original project's route-query logic.
    if "route" in query_lower or (
        "from" in query_lower and "to" in query_lower
    ):
        return find_location(user_query)

    return find_response(user_query)


# -------------------------------------------------------------------
# Web page route - keeps your original browser-based Flask app working
# -------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def query_form():
    if request.method == "POST":
        user_query = request.form.get("query", "")
        response = process_query(user_query)
        return render_template("results.html", response=response)

    return render_template("form.html")


# -------------------------------------------------------------------
# API route - this is what Typebot can call after deployment
# -------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def chat_api():
    """
    Accept a JSON request such as:
    {
        "query": "bus from Chennai to Coimbatore"
    }

    Returns:
    {
        "response": "..."
    }
    """
    request_data = request.get_json(silent=True) or {}

    user_query = request_data.get("query", "")

    if not isinstance(user_query, str):
        return jsonify({
            "response": "Please provide your query as text."
        }), 400

    response = process_query(user_query)

    return jsonify({
        "response": response
    })


# -------------------------------------------------------------------
# Simple health-check endpoint for deployment/testing
# -------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "SETC Bus Chatbot"
    })


# -------------------------------------------------------------------
# Local development
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
