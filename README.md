# EverGlow - AI Driven Storefront PoC

This project is a Proof of Concept (PoC) for an AI-driven storefront for EverGlow, a 100% vegan skincare brand. The goal is to create an adaptive UI that personalizes the shopping experience for each customer.

## Folder Structure

The project is organized into two main folders:

-   **/frontend**: Contains the Next.js web application for the storefront.
-   **/backend**: Will contain the Python FastAPI application for the AI agent and backend logic. (Currently, this folder will be a placeholder).

## Setup

### Frontend (Next.js)

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```
3.  **Run the development server:**
    ```bash
    npm run dev
    # or
    yarn dev
    ```
    The application will be accessible at `http://localhost:3000`.

### Backend (Python FastAPI)

(Instructions to be added once the backend development starts.)

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
    uvicorn main:app --reload
    ```
    The API will be accessible at `http://localhost:8000`.

## Environment Variables

Currently, no specific environment variables are required for the frontend PoC. This section will be updated as the project progresses.

For the backend, environment variables might include:
-   `DATABASE_URL`: Connection string for the database.
-   `AI_MODEL_API_KEY`: API key for the AI model service.

## Next Steps

-   Develop the UI components for the frontend as per the issue requirements.
-   Implement the adaptive UI features (dynamic theming).
-   Define data models for products and customer profiles.
-   Integrate dummy data for frontend development.
-   Begin development of the backend AI agent.
