# Gemini_Based_Travel_AI_Agent_With_MCP
This is a simple AI Agent for Travel which was developed in Python code with MCP and a chat window.

# DB creation script
CREATE DATABASE travel_db
    WITH
    OWNER = vijay //Replace this with your owner name here
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;
 
CREATE ROLE mcuser WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  NOBYPASSRLS
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:GQzf/zBIakzOGSmYRXa3Zw==$Fjn0BpB9+PyoR4oJd83O78u3KWFOdrNN/TcrVWX/9K0=:PbsBAINF2BCFVuVofvKtsCHuwHdo5E74xzJuLNghQJs=';
 
GRANT ALL ON DATABASE travel_db TO mcuser;
 
CREATE TABLE hotels(
 id            INTEGER NOT NULL PRIMARY KEY,
 name          VARCHAR NOT NULL,
 location      VARCHAR NOT NULL,
 price_tier    VARCHAR NOT NULL,
 checkin_date  DATE    NOT NULL,
 checkout_date DATE    NOT NULL,
 booked        BIT     NOT NULL
);
 
INSERT INTO hotels(id, name, location, price_tier, checkin_date, checkout_date, booked)
VALUES
 (1, 'Hilton Basel', 'Basel', 'Luxury', '2024-04-22', '2024-04-20', B'0'),
 (2, 'Marriott Zurich', 'Zurich', 'Upscale', '2024-04-14', '2024-04-21', B'0'),
 (3, 'Hyatt Regency Basel', 'Basel', 'Upper Upscale', '2024-04-02', '2024-04-20', B'0'),
 (4, 'Radisson Blu Lucerne', 'Lucerne', 'Midscale', '2024-04-24', '2024-04-05', B'0'),
 (5, 'Best Western Bern', 'Bern', 'Upper Midscale', '2024-04-23', '2024-04-01', B'0'),
 (6, 'InterContinental Geneva', 'Geneva', 'Luxury', '2024-04-23', '2024-04-28', B'0'),
 (7, 'Sheraton Zurich', 'Zurich', 'Upper Upscale', '2024-04-27', '2024-04-02', B'0'),
 (8, 'Holiday Inn Basel', 'Basel', 'Upper Midscale', '2024-04-24', '2024-04-09', B'0'),
 (9, 'Courtyard Zurich', 'Zurich', 'Upscale', '2024-04-03', '2024-04-13', B'0'),
 (10, 'Comfort Inn Bern', 'Bern', 'Midscale', '2024-04-04', '2024-04-16', B'0');

# What this AI Agent does?
This AI Agent acts as a travel assistant, primarily interacting with a PostgreSQL database to provide information about cities and hotels.

Key functionalities include:
- **Listing Cities**: Users can ask to "list cities" or "show cities" to get a list of distinct hotel locations available in the database.
- **Finding Hotels by Location**: Users can query for hotels in a specific city (e.g., "hotels in Zurich" or "find hotels in Basel") to retrieve details such as hotel name, price tier, check-in/check-out dates, and booking status.

While the agent integrates with the Gemini AI model, its current configuration is focused on database queries. General travel questions outside the scope of city and hotel listings from the database will receive a predefined response, directing users to ask travel-related questions within the agent's specific context.
