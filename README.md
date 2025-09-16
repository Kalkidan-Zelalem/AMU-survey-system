
# AMU Survey System

This is a Django-based web application designed to facilitate survey creation, distribution, and data collection within the AMU community.

## Project Description

The AMU Survey System aims to provide a user-friendly platform where administrators can create various types of surveys, distribute them to target audiences, and analyze the collected responses. Students and staff can easily participate in surveys, providing valuable feedback.

## Features

*   **User Management:** Secure authentication and authorization for different user roles (e.g., admin, survey creator, respondent).
*   **Survey Creation:** Intuitive interface for building surveys with different question types (multiple choice, text input, rating scales, etc.).
*   **Survey Distribution:** Options to share surveys via links or email invitations.
*   **Response Collection:** Secure storage of survey responses.
*   **Data Analysis:** Basic tools for viewing and exporting survey results. (Future enhancements might include advanced visualizations).

## Technologies Used

*   **Backend:** Django (Python)
*   **Database:** PostgreSQL (or SQLite for development)
*   **Frontend:** HTML, CSS, JavaScript (potentially a light framework like Bootstrap or Tailwind CSS)

## Getting Started

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   Git

### Installation (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/AMU-survey-system.git
    cd AMU-survey-system
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your settings (e.g., `SECRET_KEY`, `DATABASE_URL`).
    ```
    SECRET_KEY=your_secret_key_here
    DATABASE_URL=sqlite:///db.sqlite3
    ```
5.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000/` and the admin panel at `http://127.0.0.1:8000/admin/`.

## Contributing

We welcome contributions! Please refer to our `CONTRIBUTING.md` (if it exists) for guidelines, or follow these basic steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeatureName`).
3.  Make your changes.
4.  Commit your changes (`git commit -m "Add new feature X"`).
5.  Push to your branch (`git push origin feature/YourFeatureName`).
6.  Open a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE.md).

## Contact

For questions or issues, please contact [Your Name/Email].

# AMU-survey-system

