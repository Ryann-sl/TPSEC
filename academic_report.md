# 📄 Academic Report: Cyber Security Learning Platform

**Prepared for:** Project Supervisors  
**Date:** March 9, 2026  
**Subject:** Technical Documentation and Simulation Optimization  

---

## 1. Executive Summary
The **Cyber Security Learning Platform** is a comprehensive educational tool designed to bridge the gap between theoretical cryptography and practical cybersecurity simulation. This report details the final system architecture, the implementation of core cryptographic modules, and recent optimizations made to enhance the educational value of attack simulations, specifically in the Brute Force and Dictionary Attack segments.

## 2. Project Objectives
The primary goal of this platform is to provide an interactive environment for students to:
- Understand the mathematical principles of **Classical Cryptography**.
- Experience real-time **Cyber Attack Simulations** in a controlled environment.
- Learn **Defensive Strategies** against common vulnerabilities.
- Master **Full-Stack Development** principles applied to security software.

## 3. Technical Architecture
The platform is built using a modern decoupled architecture:
- **Backend**: Python Flask 3.0 utilizing JWT (JSON Web Tokens) for secure session management and Bcrypt for salted password hashing.
- **Frontend**: A custom-built, responsive UI using Vanilla JavaScript and CSS3, styled with a "Cybersecurity Dark Mode" aesthetic to improve user engagement.
- **Database**: SQLite for lightweight, portable data persistence.

## 4. Recent Technical Enhancements

### 4.1. Optimized Brute Force Simulation
To improve the clarity of the underlying logic for students, the Brute Force algorithm was refactored for readability:
- **Simplified Loop Logic**: Implementation of `itertools.product` now reflects a more intuitive Cartesian product generation, making the "Combinations" step easier to explain.
- **Generator Pattern**: The use of Python Generators enables real-time "Streaming Logs" (Server-Sent Events), allowing students to observe the trial-and-error process without system latency.
- **Dynamic Key Space**: The module now explicitly categorizes attempts by complexity (Modes 3, 5, and 6), demonstrating the exponential growth of key spaces as entropy increases.

### 4.2. Dictionary Attack Restrictions & Guidance
Recognizing that Dictionary Attacks are often confused with Brute Force, we implemented a structural restriction:
- **Educational Guardrails**: The Dictionary Attack is now restricted to **Mode 3 (Low Entropy)**.
- **Intelligent Feedback**: Attempting to run high-complexity attacks via the dictionary module triggers a system alert: *"Please use Brute Force"*. This encourages students to select the appropriate tool for high-entropy targets, reinforcing correct methodology.

### 4.3. Steganography Integration
A new module for **LSB (Least Significant Bit) Image Steganography** has been integrated, allowing users to hide encrypted messages within digital images, demonstrating data concealment techniques.

## 5. Security Implementations
- **Authentication**: Salted Bcrypt hashing prevents rainbow table attacks.
- **Rate Limiting**: Implemented to demonstrate defense against automated login attempts.
- **SQL Injection Prevention**: All database interactions use parameterized queries.

## 6. Conclusion
The current iteration of the platform is fully production-ready for educational deployment. The recent simplifications in the attack logic ensure that it serves as an effective teaching aid, while the UI enhancements provide a professional and immersive experience for the end-user.

---
**Technical Appendix:**
- **Repository Location:** `d:\Documents\SecTP\TPSEC`
- **Primary Source Code:** [backend/attacks/bruteforce.py](file:///d:/Documents/SecTP/TPSEC/backend/attacks/bruteforce.py), [backend/app.py](file:///d:/Documents/SecTP/TPSEC/backend/app.py)
- **Documentation:** [backend/attacks/bruteforce_explanation.txt](file:///d:/Documents/SecTP/TPSEC/backend/attacks/bruteforce_explanation.txt)
