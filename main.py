import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import hashlib


def encrypt_message(message, password):
    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode("utf-8")
    ct = base64.b64encode(ct_bytes).decode("utf-8")
    return {"iv": iv, "ciphertext": ct}


def main():
    participants = ["Aneta", "Kacper", "Robert", "Kuba"]
    random.shuffle(participants)

    encrypted_pairings = {}
    for i in range(len(participants)):
        giver = participants[i]
        receiver = participants[(i + 1) % len(participants)]
        password = giver  # Example password
        encrypted_pairings[giver] = encrypt_message(
            f"Your secret Santa is: {receiver}", password
        )

    # Save this data to be used in the HTML file
    with open("pairings.json", "w") as file:
        json.dump(encrypted_pairings, file)


if __name__ == "__main__":
    main()
