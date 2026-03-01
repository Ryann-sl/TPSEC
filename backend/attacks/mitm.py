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
        log("🌐 Monitoring network interface 'eth0'...")
        time.sleep(0.1)
        log("💉 Executing ARP Poisoning (Gateway <-> Target)...")
        time.sleep(0.2)
        log("🔌 Routing table redirected: All traffic passing through attacker machine")
        log(f"📡 Intercepted encrypted message: {encrypted_message}")
        log(f"🔍 Analyzing packet headers... Detected algorithm: {algorithm.upper()}")
        if key:
            log(f"🔑 Key/Shift detected in memory: {key}")
        log("⚠️  Message successfully captured and held for inspection")
        
        if algorithm == 'plaintext':
            log("✅ Plaintext message intercepted!")
            log("🔓 Message is NOT encrypted - reading content...")
            log(f"👀 Content: {encrypted_message}")
        else:
            log("🔒 Message is encrypted - plaintext payload is opaque")
        
        log("\n💡 Possible Attacker Actions:")
        if algorithm == 'plaintext':
             log("   [READ] Sensitive information visible")
        else:
             log("   [SNIFF] Metadata and encrypted content visible")
        log("   [MODIFY] Change message before forwarding")
        log("   [DROP] Block message delivery (DoS)")
        
        # Simulation of Receiver (Bob)
        from crypto_algorithms.caesar import CaesarCipher
        from crypto_algorithms.hill import HillCipher
        from crypto_algorithms.playfair import PlayfairCipher

        log("\n🏁 Receiver (Bob) Phase:")
        final_message = modified_message if modified_message is not None else encrypted_message
        receiver_plaintext = final_message

        if algorithm != 'plaintext' and key:
            try:
                if algorithm == 'caesar':
                    receiver_plaintext = CaesarCipher.decrypt(final_message, int(key))
                elif algorithm == 'hill':
                    receiver_plaintext = HillCipher.decrypt(final_message, key)
                elif algorithm == 'playfair':
                    receiver_plaintext = PlayfairCipher.decrypt(final_message, key)
                
                log(f"📥 Bob received ciphertext: {final_message}")
                log(f"🔑 Bob uses shared key to decrypt...")
                log(f"📄 Bob's Result: {receiver_plaintext}")
            except Exception as e:
                log(f"❌ Bob's decryption failed/corrupted: {str(e)}")
                receiver_plaintext = "[CORRUPTED DATA]"
        else:
            log(f"📥 Bob received plaintext: {final_message}")

        log("\n🛡️  DEFENSE: Use TLS/SSL to prevent MITM attacks!")
        log("🔒 End-to-end encryption protects against interception")
        
        return {
            'success': True,
            'intercepted_message': encrypted_message,
            'modified_message': modified_message,
            'receiver_plaintext': receiver_plaintext,
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
