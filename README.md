# Cyber Security Learning Platform

An educational cybersecurity platform for learning cryptography, simulating attacks, and understanding defense mechanisms.

## Features

- 🔐 Secure Authentication (bcrypt + JWT)
- 🔑 Encryption/Decryption (Caesar, Hill, Playfair)
- 📨 Encrypted Messaging System
- ⚔️ Attack Simulations (MITM, Dictionary, Brute Force)
- 🛡️ Defense Mechanisms
- 🎨 Modern Cybersecurity-themed UI

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Authentication**: JWT + bcrypt

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository
```bash
cd SEC
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize database
```bash
python backend/init_db.py
```

5. Run the application
```bash
python backend/app.py
```

6. Open browser
```
http://localhost:5000
```

## Project Structure

```
SEC/
├── frontend/
│   ├── index.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Main dashboard
│   ├── encryption.html         # Encryption module
│   ├── attacks.html            # Attack simulations
│   ├── defense.html            # Defense module
│   ├── inbox.html              # Message inbox
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       ├── auth.js            # Authentication logic
│       ├── dashboard.js       # Dashboard logic
│       ├── encryption.js      # Encryption UI logic
│       ├── attacks.js         # Attack simulations
│       └── inbox.js           # Inbox logic
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── init_db.py             # Database initialization
│   ├── auth/
│   │   └── auth_handler.py    # Authentication logic
│   ├── crypto_algorithms/
│   │   ├── caesar.py          # Caesar cipher
│   │   ├── hill.py            # Hill cipher
│   │   └── playfair.py        # Playfair cipher
│   └── attacks/
│       ├── mitm.py            # MITM simulation
│       ├── dictionary.py      # Dictionary attack
│       └── bruteforce.py      # Brute force attack
├── database/
│   └── security.db            # SQLite database (auto-generated)
└── requirements.txt           # Python dependencies
```

## Default Users

For testing purposes, you can create users via the registration page.

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/users` - Get all users (for messaging)

### Encryption
- `POST /api/encrypt/caesar` - Encrypt with Caesar cipher
- `POST /api/decrypt/caesar` - Decrypt with Caesar cipher
- `POST /api/encrypt/hill` - Encrypt with Hill cipher
- `POST /api/decrypt/hill` - Decrypt with Hill cipher
- `POST /api/encrypt/playfair` - Encrypt with Playfair cipher
- `POST /api/decrypt/playfair` - Decrypt with Playfair cipher

### Messaging
- `POST /api/messages/send` - Send encrypted message
- `GET /api/messages/inbox` - Get inbox messages

### Attacks
- `POST /api/attack/mitm` - Simulate MITM attack
- `POST /api/attack/dictionary` - Simulate dictionary attack
- `POST /api/attack/bruteforce` - Simulate brute force attack

## Educational Purpose

This platform is designed for educational purposes to help students:
- Understand classical cryptography algorithms
- Learn about cyber attacks and defenses
- Practice secure communication
- Explore cybersecurity concepts interactively

## License

MIT License - Educational Project

## Contributors

PFE Project - Final Year Computer Science
