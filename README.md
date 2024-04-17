# Django Social Networking App

This is a social networking application built using Django Rest Framework (DRF).

## Features

- User Login/Signup: Users can sign up with their email and password, and log in with their credentials.
- User Search: Users can search for other users by email or name. The search results are paginated.
- Friend Requests: Users can send, accept, or reject friend requests. Users cannot send more than 3 friend requests within a minute.
- List Friends: Users can list their friends (users who have accepted friend requests).
- List Pending Friend Requests: Users can list pending friend requests (received friend requests).

## Installation

1. Clone the repository:

git clone <repository-url>
cd <project-directory>



2. Install dependencies:

pip install -r requirements.txt



3. Set up the database:

python manage.py migrate


4. Run the development server:

python manage.py runserver


5. Access the API endpoints at `http://localhost:8000`.

## API Endpoints

Refer to the API collection shared seperately


## HeadUp
If the docker file faces any issue, please clone the code and run it locally to test

## Contributing

Contributions are welcome! If you find any bugs or want to add new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for de
