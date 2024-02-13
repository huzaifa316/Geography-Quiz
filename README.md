# Geography Quiz 🌍

Geography Quiz 🌍 is a Flask web application designed to provide an engaging platform for users to test their geographical knowledge. With features such as user registration, login, quiz taking, leaderboard viewing, and question management, this application offers an interactive experience for users interested in exploring the world's geography.

## Features

### User Authentication
- **Registration**: New users can register an account with a unique username and password.
- **Login**: Registered users can securely log in to their accounts to access the quiz features.
- **Password Security**: Passwords are hashed using a secure algorithm to protect user data.

### Quiz Taking
- **Customizable Quizzes**: Users can take quizzes with a configurable number of questions and different difficulty levels.
- **Randomized Questions**: Quiz questions are randomly selected from a pool of available questions to ensure variety and challenge.
- **Real-time Feedback**: Users receive immediate feedback on their quiz answers, with correct and incorrect responses highlighted.

### Leaderboard
- **Performance Tracking**: Users can view a leaderboard to see how they rank against others based on their quiz performance.
- **Leaderboard Filters**: Leaderboards can be filtered by different criteria such as overall score, level achieved, or quiz completion rate.
- **Personal Achievement Tracking**: Users can track their progress over time and strive to improve their ranking on the leaderboard.

### Question Management
- **Question Submission**: Authorized users can add new questions to the quiz database, contributing to the diversity of quiz content.
- **Question Approval**: Admins have the authority to approve or deny submitted questions, ensuring quality and relevance.
- **Database Maintenance**: The application's database is regularly updated and maintained to ensure accuracy and reliability of quiz questions.

### Session Management
- **Secure Sessions**: Flask session management is used to maintain user authentication and track their progress throughout the application.
- **Session Timeout**: Sessions automatically expire after a period of inactivity to enhance security and privacy.

## Installation

To run the Geography Quiz 🌍 application locally, follow these steps:

1. Clone this repository to your local machine.
2. Install Python if you haven't already.
3. Install the required Python packages by running `pip install -r requirements.txt`.
4. Set up a SQLite database by running `python setup.py`.
5. Start the Flask server by running `flask run`.

## Usage

- Open your web browser and navigate to the application URL.
- Register an account or log in if you already have one.
- Explore the quiz features, take quizzes, view leaderboards, and manage questions as per your role.
- Log out when you're done to securely end your session.

- The default admin username and password is Username: Admin and Password: Admin
- Please change them by running `SQL("sqlite:///geog.db").execute("UPDATE users SET username = username, hash = ? WHERE id = 1", generate_password_hash("password"))` where username and password are the new values

## Contributing

Contributions to the Geography Quiz 🌍 application are welcome! If you find any bugs, have suggestions for improvements, or would like to contribute new features, please open an issue or submit a pull request.

## License

Geography Quiz 🌍 is licensed under the [Apache License 2.0](LICENSE), allowing for open collaboration and distribution while maintaining legal protections for contributors and users.
