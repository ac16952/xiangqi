# Xiangqi Divination API

This project provides a Flask-based API for Xiangqi (Chinese Chess) divination.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Start the Flask server:**

    ```bash
    python app.py
    ```

    The server will start on `http://0.0.0.0:5000`.

## API Endpoints

### Get a New Board

*   **URL:** `/api/board/new`
*   **Method:** `GET`
*   **Description:** Generates a new, randomly shuffled set of 32 Xiangqi pieces.
*   **Success Response:**
    *   **Code:** 200 OK
    *   **Content:**
        ```json
        {
          "pieces": [
            {
              "color": "red",
              "display_name": "帥",
              "piece_type": "將",
              "points": 80,
              "wu_xing": "金"
            },
            ...
          ]
        }
        ```

### Perform Divination

*   **URL:** `/api/divination`
*   **Method:** `POST`
*   **Description:** Performs a divination reading based on a selection of 5 pieces.
*   **Body:**
    ```json
    {
      "pieces": [
        // 5 ChessPiece objects from the /api/board/new endpoint
      ]
    }
    ```
*   **Success Response:**
    *   **Code:** 200 OK
    *   **Content:** A JSON object containing the divination result.
*   **Error Response:**
    *   **Code:** 400 Bad Request
    *   **Content:**
        ```json
        { "error": "Exactly 5 pieces must be selected" }
        ```
