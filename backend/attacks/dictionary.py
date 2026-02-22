"""
Dictionary Attack Simulation
Attempts to crack passwords using a common password dictionary
"""

import time

class DictionaryAttack:
    """Simulate dictionary attack on passwords"""
    
    # Common password dictionary
    COMMON_PASSWORDS = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "iloveyou", "master", "sunshine", "ashley",
        "bailey", "passw0rd", "shadow", "123123", "654321",
        "superman", "qazwsx", "michael", "football", "welcome",
        "jesus", "ninja", "mustang", "password1", "123456789",
        "admin", "root", "toor", "pass", "test",
        "guest", "info", "adm", "mysql", "user",
        "administrator", "oracle", "ftp", "pi", "puppet"
    ]
    
    @staticmethod
    def simulate_attack(target_password, max_attempts=50, custom_wordlist=None, logs_callback=None):
        """
        Simulate dictionary attack
        
        Args:
            target_password (str): The password to crack
            max_attempts (int): Maximum attempts to try
            custom_wordlist (list): Optional list of passwords to use
            logs_callback (function): Optional callback for logging
            
        Returns:
            dict: Attack results
        """
        logs = []
        attempts = 0
        found = False
        
        def log(message):
            logs.append({
                'timestamp': time.time(),
                'message': message
            })
            if logs_callback:
                logs_callback(message)
        
        wordlist_to_use = custom_wordlist if custom_wordlist is not None else DictionaryAttack.COMMON_PASSWORDS
        
        log("🎯 Dictionary Attack Initiated")
        log(f"📚 Dictionary size: {len(wordlist_to_use)} passwords")
        log(f"🎲 Max attempts: {max_attempts}")
        log("⚠️  Starting attack...\n")
        
        # Try passwords from dictionary
        for password in wordlist_to_use[:max_attempts]:
            attempts += 1
            time.sleep(0.05)  # Simulate network delay
            
            log(f"Attempt {attempts}: Trying '{password}'...")
            
            if password.lower() == target_password.lower():
                found = True
                log(f"\n✅ SUCCESS! Password cracked: '{password}'")
                log(f"🔓 Took {attempts} attempts")
                break
        
        if not found:
            log(f"\n❌ Attack failed after {attempts} attempts")
            log("💡 Password not in common dictionary")
            log("🛡️  This is a STRONG password!")
        
        log("\n🛡️  DEFENSE RECOMMENDATIONS:")
        log("   - Use long, unique passwords (12+ characters)")
        log("   - Avoid common words and patterns")
        log("   - Use password manager")
        log("   - Enable account lockout after failed attempts")
        log("   - Implement rate limiting")
        
        return {
            'success': found,
            'attempts': attempts,
            'cracked_password': target_password if found else None,
            'logs': logs,
            'defense_recommendation': 'Use strong, unique passwords and rate limiting'
        }
    
    @staticmethod
    def check_password_strength(password):
        """
        Check password strength
        
        Args:
            password (str): Password to check
            
        Returns:
            dict: Strength analysis
        """
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 2
            feedback.append("✅ Good length (12+ characters)")
        elif len(password) >= 8:
            score += 1
            feedback.append("⚠️  Acceptable length (8-11 characters)")
        else:
            feedback.append("❌ Too short (less than 8 characters)")
        
        # Complexity checks
        if any(c.isupper() for c in password):
            score += 1
            feedback.append("✅ Contains uppercase letters")
        else:
            feedback.append("❌ No uppercase letters")
        
        if any(c.islower() for c in password):
            score += 1
            feedback.append("✅ Contains lowercase letters")
        else:
            feedback.append("❌ No lowercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
            feedback.append("✅ Contains numbers")
        else:
            feedback.append("❌ No numbers")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
            feedback.append("✅ Contains special characters")
        else:
            feedback.append("❌ No special characters")
        
        # Dictionary check
        if password.lower() in DictionaryAttack.COMMON_PASSWORDS:
            score = 0
            feedback.append("❌ CRITICAL: Password in common dictionary!")
        
        # Determine strength
        if score >= 5:
            strength = "STRONG"
        elif score >= 3:
            strength = "MEDIUM"
        else:
            strength = "WEAK"
        
        return {
            'strength': strength,
            'score': score,
            'max_score': 6,
            'feedback': feedback
        }
    
    @staticmethod
    def explain_dictionary_attack():
        """Return educational explanation"""
        return {
            'title': 'Dictionary Attack',
            'description': 'An attack that tries common passwords from a predefined list.',
            'how_it_works': [
                '1. Attacker obtains list of common passwords',
                '2. Systematically tries each password',
                '3. Continues until password is found or list exhausted',
                '4. Can be combined with username lists'
            ],
            'why_effective': [
                'Many users choose weak, common passwords',
                'Password reuse across multiple sites',
                'Predictable password patterns',
                'Human tendency to choose memorable words'
            ],
            'defenses': [
                'Use strong, unique passwords',
                'Enable account lockout policies',
                'Implement rate limiting',
                'Use multi-factor authentication (MFA)',
                'Monitor for suspicious login attempts',
                'Use password managers'
            ]
        }
