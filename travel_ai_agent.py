# travel_ai_agent.py - Travel AI backend server

import os  # For environment variables and file paths
import google.generativeai as genai  # Google Gemini AI SDK
from flask import Flask, request, jsonify  # Flask web framework
from flask_cors import CORS  # For enabling CORS
import sys  # For error output
import threading  # For running Flask in a separate thread
import psycopg2  # PostgreSQL database adapter
from datetime import date  # For handling date objects from DB

# --- Configuration ---
# Set up API keys, model names, and server/database configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "Provide your own API key")  # Gemini API key (from env or default)
GEMINI_MODEL_NAME = "gemini-2.0-flash"  # Gemini model name
FLASK_HOST = "0.0.0.0"  # Listen on all interfaces
FLASK_PORT = 5001  # Flask server port

# PostgreSQL Database Configuration
DB_CONFIG = {
    "dbname": "travel_db",  # Database name
    "user": "mcuser",       # Database user
    "password": "mcpass",   # Database password
    "host": "localhost",    # Database host
    "port": "5432"          # Database port
}

# --- Database Connection Helper ---
def get_db_connection():
    """Establishes and returns a new PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # Connect to PostgreSQL
        return conn  # Return connection object
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}", file=sys.stderr)  # Print error
        return None  # Return None on failure

# --- AI Agent Class ---
class TravelAIAgent:
    def __init__(self, api_key: str):
        """
        Initializes the AI agent with the Gemini API key (though it won't be used for general queries now).
        Sets up the Gemini model for possible future use.
        """
        if not api_key:
            print("Warning: Gemini API Key is not set, but the agent will now reject general queries anyway.", file=sys.stderr)
        # Configure Gemini model
        try:
            genai.configure(api_key=api_key)  # Set API key
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)  # Create model instance
        except Exception as e:
            print(f"Error configuring Gemini API: {e}. Gemini functionality is not intended for general queries as per user request.", file=sys.stderr)
            self.model = None  # Set model to None on failure

    def _get_cities_from_db(self) -> list[str]:
        """Queries the database for a list of distinct hotel locations (cities)."""
        cities = []  # List to store city names
        conn = get_db_connection()  # Get DB connection
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT DISTINCT location FROM hotels ORDER BY location;")  # Query for unique cities
                    for row in cur:
                        cities.append(row[0])  # Add city to list
                print(f"Found cities: {', '.join(cities)}")  # Log found cities
            except psycopg2.Error as e:
                print(f"Error querying cities from DB: {e}", file=sys.stderr)  # Log error
            finally:
                conn.close()  # Always close connection
        return cities  # Return list of cities

    def _get_hotels_by_location_from_db(self, location: str) -> list[dict]:
        """Queries the database for hotels in a specific location."""
        hotels = []  # List to store hotel info
        conn = get_db_connection()  # Get DB connection
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, location, price_tier, checkin_date, checkout_date, booked FROM hotels WHERE LOWER(location) = LOWER(%s);", (location,))  # Query for hotels in location
                    for row in cur:
                        # Convert date objects to strings for JSON serialization
                        checkin = row[3].strftime("%Y-%m-%d") if isinstance(row[3], date) else str(row[3])
                        checkout = row[4].strftime("%Y-%m-%d") if isinstance(row[4], date) else str(row[4])
                        hotels.append({
                            "name": row[0],
                            "location": row[1],
                            "price_tier": row[2],
                            "checkin_date": checkin,
                            "checkout_date": checkout,
                            "booked": row[5]
                        })  # Add hotel dict to list
                print(f"Found {len(hotels)} hotels in {location}.")  # Log number of hotels
            except psycopg2.Error as e:
                print(f"Error querying hotels for {location} from DB: {e}", file=sys.stderr)  # Log error
            finally:
                conn.close()  # Always close connection
        return hotels  # Return list of hotels

    def _query_gemini(self, prompt: str) -> str:
        """
        Sends a query to the Gemini AI model.
        (This method is still present but will only be called if explicitly re-enabled for certain tasks).
        """
        if not self.model:
            return "AI functionality is not available due to missing or invalid API key."
        print(f"Querying Gemini AI with prompt: '{prompt}' (Note: This is not for general queries as per user config)...")
        context = "You are a travel agent. Only answer questions about country, state, cities, places in cities and what it is like to visit there or famous for, hotels/resorts/stays, travel planning, price details and travel related details of country. If a question is outside of this context, respond with: 'Hi, I'm an travel Agent and ask me question only about travel/country/state/city/stay/travel planning related details. Thank you!'"  # Context for Gemini
        prompt_with_context = f"{context}\n\nUser query: {prompt}"  # Combine context and user prompt
        try:
            response = self.model.generate_content(prompt_with_context)  # Query Gemini
            if response and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                text = response.candidates[0].content.parts[0].text  # Extract text
                print("Gemini AI response received.")
                return text  # Return Gemini response
            else:
                return "Gemini AI did not return a valid response."
        except Exception as e:
            print(f"Error querying Gemini AI: {e}", file=sys.stderr)  # Log error
            return f"Error communicating with AI: {e}"

    def handle_query(self, user_query: str) -> str:
        """
        Handles a user query by checking the PostgreSQL database for specific travel queries.
        Any other context or general query is now explicitly rejected.
        """
        user_query_lower = user_query.lower().strip()  # Normalize query
        # Check for city list queries
        if user_query_lower == "list cities" or user_query_lower == "show cities":
            cities = self._get_cities_from_db()  # Get cities from DB
            if cities:
                return "Available cities: " + ", ".join(cities) + "."  # Return city list
            else:
                return "Could not retrieve city list from database. Please ensure the database is running and accessible."
        # Check for hotel queries by location
        elif user_query_lower.startswith("hotels in "):
            location = user_query_lower.replace("hotels in ", "").strip()  # Extract location
            hotels = self._get_hotels_by_location_from_db(location)  # Get hotels from DB
            if hotels:
                response_str = f"Hotels in {location.title()}:\n"  # Start response string
                for hotel in hotels:
                    booked_status = "Booked" if hotel['booked'] else "Available"  # Determine booking status
                    response_str += (f"- {hotel['name']} ({hotel['price_tier']}) - "
                                     f"Check-in: {hotel['checkin_date']}, Check-out: {hotel['checkout_date']} "
                                     f"Status: {booked_status}\n")  # Add hotel info
                return response_str.strip()  # Return formatted hotel list
            else:
                return f"No hotels found in {location.title()} in our database, or an error occurred."
        # Alternate phrasing for hotel queries
        elif user_query_lower.startswith("find hotels in "):
            location = user_query_lower.replace("find hotels in ", "").strip()  # Extract location
            hotels = self._get_hotels_by_location_from_db(location)  # Get hotels from DB
            if hotels:
                response_str = f"Hotels found in {location.title()}:\n"  # Start response string
                for hotel in hotels:
                    booked_status = "Booked" if hotel['booked'] else "Available"  # Determine booking status
                    response_str += (f"- {hotel['name']} ({hotel['price_tier']}) - "
                                     f"Check-in: {hotel['checkin_date']}, Check-out: {hotel['checkout_date']} "
                                     f"Status: {booked_status}\n")  # Add hotel info
                return response_str.strip()  # Return formatted hotel list
            else:
                return f"No hotels found in {location.title()} in our database, or an error occurred."
        else:
            # Fallback: query Gemini for unsupported/general queries
            gemini_response = self._query_gemini(user_query)
            return gemini_response

# --- Flask App Setup ---
app = Flask(__name__)  # Create Flask app
CORS(app)  # Enable CORS for the entire app
agent_instance = None  # Global instance of our AI agent

@app.route('/query_ai', methods=['POST'])
def query_ai_endpoint():
    """
    Flask endpoint to receive AI queries.
    Expects a JSON payload like: {"query": "your question here"}
    """
    global agent_instance
    if not agent_instance:
        return jsonify({"error": "AI Agent not initialized. Please check server logs."}), 500  # Error if agent not ready
    data = request.get_json()  # Parse JSON body
    user_query = data.get('query')  # Extract query
    if not user_query:
        return jsonify({"error": "No query provided in the request body."}), 400  # Error if no query
    response_text = agent_instance.handle_query(user_query)  # Get response from agent
    return jsonify({"response": response_text})  # Return response as JSON

pass  # No-op (placeholder)

def run_flask_app(host, port):
    """Runs the Flask app in a blocking manner."""
    app.run(host=host, port=port, debug=False, use_reloader=False)  # Start Flask server

def init_agent_async():
    """Initializes the agent and tests DB connection."""
    global agent_instance
    agent_instance = TravelAIAgent(GEMINI_API_KEY)  # Create agent instance
    # Test DB connection on startup
    conn = get_db_connection()
    if conn:
        print("Successfully connected to PostgreSQL database.")
        conn.close()
    else:
        print("Failed to connect to PostgreSQL database. Database queries will not work. Please check DB_CONFIG.")

if __name__ == "__main__":
    # Initialize the AI agent and test DB connection asynchronously
    init_agent_async()
    print(f"\n--- Travel AI Agent Server Ready ---")  # Startup message
    print(f"Access the API at http://{FLASK_HOST}:{FLASK_PORT}/query_ai")
    print("Send POST requests with JSON body: {'query': 'your question'}")
    print("Example queries: 'list cities', 'hotels in Zurich'")
    print("Any other query will be rejected.")
    print("Press Ctrl+C to stop the server.")
    # Run Flask in a separate thread so the main thread can continue to manage the asyncio loop
    flask_thread = threading.Thread(target=run_flask_app, args=(FLASK_HOST, FLASK_PORT,))  # Create thread
    flask_thread.daemon = True  # Allow main program to exit even if thread is running
    flask_thread.start()  # Start Flask server in thread
    while True:
        pass  # Keep main thread alive
