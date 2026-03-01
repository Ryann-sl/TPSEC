import os
import itertools
import string

def generate_case1():
    """3 characters from {2, 3, 4}"""
    chars = "234"
    path = os.path.join("backend", "data", "wordlists", "case1.txt")
    with open(path, "w") as f:
        for p in itertools.product(chars, repeat=3):
            f.write("".join(p) + "\n")
    print(f"Generated {path}")

def generate_case2():
    """5 characters from {0-9}"""
    chars = string.digits
    path = os.path.join("backend", "data", "wordlists", "case2.txt")
    with open(path, "w") as f:
        for p in itertools.product(chars, repeat=5):
            f.write("".join(p) + "\n")
    print(f"Generated {path}")

def generate_case3():
    """6 characters mixed (Sample/Representative)"""
    # Exhaustive would be ~117 billion. We'll provide a smaller "sample" dictionary.
    # In a real dictionary attack, this would be a file of common 6-char passwords.
    chars = string.ascii_letters + string.digits + "+*"
    path = os.path.join("backend", "data", "wordlists", "case3.txt")
    
    # We'll generate a few thousand "common" combinations or just a sample
    # to stay within "Dictionary Attack" definition while acknowledging the space.
    # For educational purposes, we'll generate 50,000 samples.
    import random
    
    with open(path, "w") as f:
        # Include some predictable patterns
        f.write("aaaaaa\n")
        f.write("123456\n")
        f.write("qwerty\n")
        f.write("admin1\n")
        f.write("passw*\n")
        f.write("++++++\n")
        f.write("******\n")
        
        # Add random samples
        for _ in range(50000):
            p = "".join(random.choices(chars, k=6))
            f.write(p + "\n")
            
    print(f"Generated {path} (Sample)")

if __name__ == "__main__":
    os.makedirs(os.path.join("backend", "data", "wordlists"), exist_ok=True)
    generate_case1()
    generate_case2()
    generate_case3()
