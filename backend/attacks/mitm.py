"""
Man-in-the-Middle (MITM) Attack Simulation
Educational simulation of intercepting encrypted messages
"""

import random
import time

class MITMAttack:
    """Simulate MITM attack on encrypted communications"""
    
    @staticmethod
    def simulate_interception(encrypted_message, algorithm, modified_message=None, key=None, logs_callback=None):
        """
        Simulate intercepting a message
        
        Args:
            encrypted_message (str): The encrypted message
            algorithm (str): Algorithm used (caesar, hill, playfair)
            logs_callback (function): Optional callback for logging steps
            
        Returns:
            dict: Attack results with logs
        """
        logs = []
        
        def log(message):
            logs.append({
                'timestamp': time.time(),
                'message': message
            })
            if logs_callback:
                logs_callback(message)
        
        log("🎯 MITM Attack Initiated")
        log(f"📡 Intercepted encrypted message: {encrypted_message}")
        log(f"🔍 Detected algorithm: {algorithm.upper()}")
        if key:
            log(f"🔑 Key/Shift detected: {key}")
        log("⚠️  Attempting to intercept communication...")
        
        if algorithm == 'plaintext':
            log("✅ Plaintext message intercepted!")
            log("🔓 Message is NOT encrypted - reading content...")
            log(f"👀 Content: {encrypted_message}")
        else:
            log("✅ Message successfully intercepted!")
            log("🔐 Message is encrypted - cannot read plaintext")
        
        log("💡 Attacker can:")
        if algorithm == 'plaintext':
             log("   - Read sensitive information")
        else:
             log("   - Read encrypted content (but not plaintext)")
        log("   - Modify message")
        log("   - Block message delivery")
        
        # Check if user provided a modified message
        if modified_message is not None:
            log(f"⚠️  Attacker manually modified the message")
            log(f"📤 Original: {encrypted_message}")
            log(f"📥 Modified: {modified_message}")
        else:
            # Simulate modification attempt
            log("\n🛠️  Attempting message modification...")
            time.sleep(0.3)
            
            # Randomly modify some characters
            modified = list(encrypted_message)
            if len(modified) > 2:
                pos = random.randint(0, len(modified) - 1)
                original_char = modified[pos]
                modified[pos] = chr((ord(modified[pos]) + 1 - ord('A')) % 26 + ord('A')) if modified[pos].isalpha() else modified[pos]
                modified_message = ''.join(modified)
                
                log(f"⚠️  Modified character at position {pos}: '{original_char}' → '{modified[pos]}'")
                log(f"📤 Modified message: {modified_message}")
            else:
                modified_message = encrypted_message
                log("⚠️  Message too short to modify safely")
        
        log("\n🛡️  DEFENSE: Use TLS/SSL to prevent MITM attacks!")
        log("🔒 End-to-end encryption protects against interception")
        
        return {
            'success': True,
            'intercepted_message': encrypted_message,
            'modified_message': modified_message,
            'algorithm': algorithm,
            'logs': logs,
            'defense_recommendation': 'Use TLS/SSL and certificate pinning'
        }
    
    @staticmethod
    def explain_mitm():
        """Return educational explanation of MITM attacks"""
        return {
            'title': 'Man-in-the-Middle (MITM) Attack',
            'description': 'An attack where the attacker secretly intercepts and possibly alters communication between two parties.',
            'how_it_works': [
                '1. Attacker positions themselves between sender and receiver',
                '2. Intercepts messages in transit',
                '3. Can read, modify, or block messages',
                '4. Both parties think they are communicating directly'
            ],
            'real_world_examples': [
                'Public WiFi interception',
                'DNS spoofing',
                'ARP poisoning',
                'SSL stripping'
            ],
            'defenses': [
                'Use HTTPS/TLS for all communications',
                'Verify SSL certificates',
                'Use VPN on public networks',
                'Implement certificate pinning',
                'Use end-to-end encryption'
            ]
        }
