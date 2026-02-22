# 🔐 Cyber Security Learning Platform - Project Documentation

## 📋 Project Overview

This is a complete, production-ready **Cyber Security Learning Platform** built for educational purposes. It's designed as a PFE (Projet de Fin d'Études) project that demonstrates:

- **Full-stack web development** (Python Flask + HTML/CSS/JavaScript)
- **Cryptography algorithms** (Caesar, Hill, Playfair ciphers)
- **Cyber attack simulations** (MITM, Dictionary, Brute Force)
- **Secure authentication** (JWT + bcrypt)
- **Modern UI/UX design** (Dark cybersecurity theme with neon accents)

---

## ✅ Project Status

**STATUS: FULLY COMPLETE AND RUNNING** ✅

- ✅ Backend API (Flask) - Running on http://localhost:5000
- ✅ Database (SQLite) - Initialized with all tables
- ✅ Frontend (HTML/CSS/JS) - All pages created
- ✅ Authentication System - JWT + bcrypt implemented
- ✅ Encryption Algorithms - Caesar, Hill, Playfair
- ✅ Attack Simulations - MITM, Dictionary, Brute Force
- ✅ Messaging System - Send/receive encrypted messages
- ✅ Defense Module - Security best practices

---

## 📁 Project Structure

```
SEC/
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── setup.bat                      # Automated setup script
├── run.bat                        # Run application script
├── venv/                          # Python virtual environment
│
├── database/
│   └── security.db                # SQLite database (auto-generated)
│
├── backend/
│   ├── app.py                     # Main Flask application (14.9 KB)
│   ├── init_db.py                 # Database initialization
│   │
│   ├── auth/
│   │   └── auth_handler.py        # Authentication logic (JWT + bcrypt)
│   │
│   ├── crypto_algorithms/
│   │   ├── caesar.py              # Caesar cipher implementation
│   │   ├── hill.py                # Hill cipher implementation
│   │   └── playfair.py            # Playfair cipher implementation
│   │
│   └── attacks/
│       ├── mitm.py                # MITM attack simulation
│       ├── dictionary.py          # Dictionary attack simulation
│       └── bruteforce.py          # Brute force attack simulation
│
└── frontend/
    ├── index.html                 # Login page
    ├── register.html              # Registration page
    ├── dashboard.html             # Main dashboard
    ├── encryption.html            # Encryption module
    ├── attacks.html               # Attack simulations
    ├── defense.html               # Defense mechanisms
    ├── inbox.html                 # Message inbox
    │
    ├── css/
    │   └── style.css              # Main stylesheet (dark cyber theme)
    │
    └── js/
        ├── auth.js                # Authentication JavaScript
        ├── dashboard.js           # Dashboard logic
        ├── encryption.js          # Encryption UI logic
        ├── attacks.js             # Attack simulations
        └── inbox.js               # Inbox functionality
```

---

## 🚀 How to Run

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script (first time only)
setup.bat

# Run the application
run.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python backend\init_db.py

# 5. Run the application
python backend\app.py
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🎨 Features Overview

### 1. **Authentication System** 🔐
- **Secure Registration**: Username + password with validation
- **Login**: JWT token-based authentication
- **Password Security**: bcrypt hashing with salt
- **Session Management**: Token stored in localStorage

### 2. **Encryption Module** 🔑
Three classical cryptography algorithms:

#### Caesar Cipher
- **Type**: Substitution cipher
- **Key**: Shift value (0-25)
- **Example**: "HELLO" with shift 3 → "KHOOR"

#### Hill Cipher
- **Type**: Polygraphic substitution
- **Key**: 2x2 matrix (4 letters)
- **Example**: Uses linear algebra for encryption

#### Playfair Cipher
- **Type**: Digraph substitution
- **Key**: Keyword
- **Example**: Uses 5x5 key matrix

**Features**:
- Encrypt messages with any algorithm
- Decrypt received messages
- Send encrypted messages to other users
- Copy encrypted text to clipboard

### 3. **Attack Simulations** ⚔️

#### Man-in-the-Middle (MITM)
- Intercept encrypted communications
- Modify messages in transit
- Educational demonstration of network attacks
- Terminal-style logs showing attack steps

#### Dictionary Attack
- Test password strength
- Try common passwords from dictionary
- Real-time attack progress
- Password strength analyzer

#### Brute Force Attack
- Try all possible keys (Caesar cipher)
- Shows all 26 possible decryptions
- Demonstrates key space importance
- Educational comparison of algorithms

### 4. **Defense Module** 🛡️
Educational content on:
- Defending against MITM attacks (TLS/SSL, VPN)
- Protecting against dictionary attacks (strong passwords, MFA)
- Preventing brute force (large key spaces, rate limiting)
- Security best practices

### 5. **Messaging System** 📨
- Send encrypted messages to other users
- Inbox with unread message indicators
- Decrypt messages with correct key
- Message history with timestamps
- Algorithm badges (Caesar, Hill, Playfair)

---

## 🎨 Design Features

### Dark Cybersecurity Theme
- **Background**: Deep navy (#0a0e27) with animated gradients
- **Neon Accents**: Cyan (#00f0ff), Green (#00ff88), Purple (#b84fff)
- **Typography**: Inter font family for clean, modern look
- **Monospace**: Fira Code for terminal and encrypted text

### UI Components
- **Glassmorphism Cards**: Frosted glass effect with backdrop blur
- **Neon Glow Effects**: Hover animations with neon shadows
- **Terminal Interface**: Authentic terminal-style logs for attacks
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Fade-ins, slides, and hover effects

### Accessibility
- High contrast colors
- Clear typography
- Keyboard navigation support
- Screen reader friendly

---

## 🔧 Technical Stack

### Backend
- **Framework**: Flask 3.0.0
- **Authentication**: PyJWT 2.8.0 + bcrypt 4.1.2
- **Database**: SQLite (built-in)
- **CORS**: Flask-CORS 4.0.0
- **Math**: NumPy 1.26.3 (for Hill cipher)

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables
- **JavaScript**: Vanilla JS (no frameworks)
- **Fonts**: Google Fonts (Inter, Fira Code)

### Security
- **Password Hashing**: bcrypt with salt
- **Authentication**: JWT tokens
- **Input Validation**: Client and server-side
- **SQL Injection Prevention**: Parameterized queries

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    algorithm TEXT NOT NULL,
    encrypted_text TEXT NOT NULL,
    key_used TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);
```

### Attack Logs Table
```sql
CREATE TABLE attack_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    attack_type TEXT NOT NULL,
    target_message_id INTEGER,
    success BOOLEAN,
    attempts INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/users` - Get all users (authenticated)

### Encryption
- `POST /api/encrypt/caesar` - Encrypt with Caesar
- `POST /api/decrypt/caesar` - Decrypt with Caesar
- `POST /api/encrypt/hill` - Encrypt with Hill
- `POST /api/decrypt/hill` - Decrypt with Hill
- `POST /api/encrypt/playfair` - Encrypt with Playfair
- `POST /api/decrypt/playfair` - Decrypt with Playfair

### Messaging
- `POST /api/messages/send` - Send encrypted message
- `GET /api/messages/inbox` - Get inbox messages
- `PUT /api/messages/:id/read` - Mark message as read

### Attacks
- `POST /api/attack/mitm` - Simulate MITM attack
- `POST /api/attack/dictionary` - Simulate dictionary attack
- `POST /api/attack/bruteforce` - Simulate brute force attack

### Educational
- `GET /api/info/mitm` - Get MITM attack info
- `GET /api/info/dictionary` - Get dictionary attack info
- `GET /api/info/bruteforce` - Get brute force attack info
- `POST /api/password/strength` - Check password strength

---

## 📝 Usage Examples

### 1. Create Account
1. Navigate to http://localhost:5000
2. Click "Register here"
3. Enter username (min 3 characters)
4. Enter password (min 6 characters)
5. Click "Create Account"

### 2. Send Encrypted Message
1. Login to your account
2. Click "Encryption / Decryption"
3. Select algorithm (Caesar, Hill, or Playfair)
4. Enter your message
5. Enter encryption key
6. Select receiver from dropdown
7. Click "Encrypt"
8. Message is automatically sent!

### 3. Decrypt Received Message
1. Click "Message Inbox" from dashboard
2. View encrypted messages
3. Enter the decryption key
4. Click "Decrypt"
5. View the plaintext message

### 4. Simulate Attack
1. Click "Attack Simulations"
2. Choose attack type (MITM, Dictionary, Brute Force)
3. Enter required parameters
4. Click "Start Attack"
5. Watch terminal logs in real-time

---

## 🎓 Educational Value

This project demonstrates:

### Cryptography Concepts
- Classical cipher algorithms
- Encryption vs. Decryption
- Key management
- Algorithm strengths and weaknesses

### Cybersecurity Principles
- Attack vectors and methodologies
- Defense mechanisms
- Security best practices
- Password security

### Software Engineering
- Full-stack development
- RESTful API design
- Database design
- Authentication systems
- Modern UI/UX design

---

## 🔒 Security Considerations

### What This Project Does Well
✅ Password hashing with bcrypt
✅ JWT authentication
✅ Input validation
✅ SQL injection prevention
✅ CORS configuration

### Educational Disclaimer
⚠️ This is an **educational platform** using **classical ciphers**
⚠️ Caesar, Hill, and Playfair are **NOT secure** for real-world use
⚠️ For production: Use AES-256, RSA, or modern encryption
⚠️ Attack simulations are for **learning purposes only**

---

## 🚀 Future Enhancements (Optional)

### Potential Additions
- [ ] Steganography module (hide messages in images)
- [ ] RSA encryption (modern asymmetric encryption)
- [ ] AES encryption (modern symmetric encryption)
- [ ] Hash functions (MD5, SHA-256)
- [ ] Digital signatures
- [ ] Certificate management
- [ ] Network packet analysis
- [ ] SQL injection simulator
- [ ] XSS attack simulator

---

## 📚 References & Learning Resources

### Cryptography
- "Introduction to Cryptography" - William Stallings
- "Applied Cryptography" - Bruce Schneier

### Cybersecurity
- OWASP Top 10
- NIST Cybersecurity Framework
- CIS Controls

### Web Development
- Flask Documentation
- MDN Web Docs
- OWASP Secure Coding Practices

---

## 👨‍💻 Development Notes

### Code Quality
- ✅ Modular architecture
- ✅ Comprehensive comments
- ✅ Error handling
- ✅ Input validation
- ✅ Consistent code style

### Testing Recommendations
1. Test all encryption algorithms
2. Verify attack simulations
3. Test messaging between users
4. Check authentication flows
5. Test on different browsers

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: Database not found
**Solution**: Run `python backend\init_db.py`

**Issue**: Module not found
**Solution**: Activate venv and run `pip install -r requirements.txt`

**Issue**: Port 5000 already in use
**Solution**: Change port in `backend\app.py` (last line)

**Issue**: CORS errors
**Solution**: Check Flask-CORS is installed

---

## 📄 License

MIT License - Educational Project

---

## 🎉 Conclusion

This is a **complete, production-ready** Cyber Security Learning Platform that:

✅ Implements 3 classical cryptography algorithms
✅ Simulates 3 types of cyber attacks
✅ Provides secure user authentication
✅ Enables encrypted messaging between users
✅ Teaches defense mechanisms
✅ Features a stunning modern UI
✅ Is fully documented and ready to present

**Perfect for**: PFE projects, cybersecurity education, portfolio demonstrations

**Server Status**: ✅ RUNNING on http://localhost:5000

---

**Created**: February 2026
**Version**: 1.0.0
**Status**: Production Ready ✅
