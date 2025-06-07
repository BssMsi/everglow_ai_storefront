# EverGlow - AI Driven Storefront PoC

This project is a Proof of Concept (PoC) for an AI-driven storefront for EverGlow Labs, a 100% vegan skincare brand.

## Folder Structure

The project is organized into two main folders:

-   **/frontend**: Contains the Next.js web application for the storefront.
-   **/backend**: Contains the Python FastAPI application for the AI agent and backend logic.

## Setup

### Frontend (Next.js)
1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be accessible at `http://localhost:3000`.

### Backend (Python FastAPI)
1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the FastAPI server:**
    ```bash
    uvicorn main:app --port 8000
    ```
    The API will be accessible at `http://localhost:8000`.

## Environment Variables
For the backend, environment variables include:
-   `PINECONE_API_KEY`
-   `PINECONE_ENV`
-   `COHERE_API_KEY`
-   `GEMINI_API_KEY`

## Issues
- Fuzzy match returns different product sometimes, so the review might cite for some other product rather than what user asked.
- Currently the reviews/support tickets might throw a bad light on the brand which should ideally be filtered out
- Default intent is 'search' which returns products, so if the intent is other than "review_explanation", "brand_info", "recommend", by default it will update products. Meaning you cannot have a normal conversation.

## Next Steps
- Add Login, Cart, Checkout, etc.
- Add Analytics
### Backend Analytics
#### Conversation Analytics
- Intent Distribution : Track which intents users most commonly express (recommend, review_explanation, brand_info, search)
- Conversation Flow : Monitor how users navigate between different agents and conversation stages
- Most common conversation paths (search → recommend → review_explanation)
- Abandonment points in conversations
- Entity Extraction Patterns : Analyze what categories, skin concerns, and ingredients users most frequently mention
- Conversation Length : Track number of turns before users get recommendations or abandon conversations
- Follow-up Question Effectiveness : Measure how often follow-up questions lead to successful recommendations
#### Recommendation Analytics
- Top requested categories and combinations
- Trending skin concerns and ingredients
- Filter usage patterns in Pinecone queries
- Search Success Rate : Track when searches return products vs. empty results
- Category Preferences : Analyze most requested product categories
- Skin Concern Trends : Monitor trending skin concerns and ingredient requests
- Recommendation Acceptance : Track which products users engage with (if frontend provides feedback)
- Query Complexity : Analyze semantic similarity scores and filter usage patterns
#### Performance Metrics
- Intent classification accuracy
- Agent response times
- Error rates by agent type
- Pinecone query performance
### Frontend Analytics
#### User Journey Mapping:
- Map out typical user flows on the storefront (e.g., landing page -> product listing -> product detail -> add to cart -> checkout -> purchase confirmation).
#### Define Critical Events:
- Page Views: Track every page loaded, including parameters like page title, URL, and category.
- Product Interactions: Clicks on product images, viewing product details, adding/removing items from cart.
- Search and Filter Usage: Tracking search terms, filter selections, and results viewed.
- User Engagement: Scroll depth, time spent on key sections, video plays, interaction with interactive elements.
- Error Tracking: When users encounter errors (e.g., broken links, form submission failures).
- A/B Test Variations: Track which variations users are exposed to and their behavior.
#### Standardize Data
- Implement a robust data layer on the frontend (e.g., a JavaScript object window.dataLayer) to push relevant information as events occur.