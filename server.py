from flask import Flask, request, jsonify, render_template
import random
import hashlib

app = Flask(__name__)

# Hardcoded emails
PARTICIPANTS = [
    "example1@example.com"
    "example2@example.com"
    "example3@example.com"
    "example4@example.com"
]

# Store phrases and pairings
phrases = {email: None for email in PARTICIPANTS}
pairings = {}
hashed_phrases = {}


def generate_pairings(participants):
    if len(participants) < 2:
        raise ValueError("At least two participants are required.")

    shuffled = participants[:]
    random.shuffle(shuffled)

    # Ensure no one is paired with themselves
    for i in range(len(shuffled)):
        if shuffled[i] == participants[i]:
            swap_index = (i + 1) % len(shuffled)
            shuffled[i], shuffled[swap_index] = shuffled[swap_index], shuffled[i]

    return list(zip(participants, shuffled))


def test_pairings():
    for _ in range(1000):  # Repeat the test many times to ensure reliability
        participants = ["Alice", "Bob", "Charlie", "David"]
        pairings = generate_pairings(participants)

        for giver, receiver in pairings:
            if giver == receiver:
                return False, pairings  # Fail if someone is paired with themselves

        if len(set(receiver for _, receiver in pairings)) != len(participants):
            return False, pairings  # Fail if someone is missing or duplicated

    return True, "All tests passed"


@app.route("/", methods=["GET", "POST"])
def index():
    result, message = test_pairings()
    print(f"Test result: {result}, Message: {message}")
    if request.method == "POST":
        email = request.form.get("email")
        phrase = request.form.get("phrase")
        if email in PARTICIPANTS and phrase:
            phrases[email] = phrase
            if all(phrases.values()):
                temp_pairings = generate_pairings(PARTICIPANTS)
                for giver, receiver in temp_pairings:
                    pairings[giver] = receiver
                    hashed_phrases[giver] = hashlib.sha256(
                        phrases[giver].encode()
                    ).hexdigest()

                return jsonify({"message": "Pairings generated. Check your result."})
            return jsonify({"message": "Phrase received. Waiting for others."})
        return jsonify({"error": "Invalid email or missing phrase."})
    return render_template("./index.html")


@app.route("/result", methods=["POST"])
def result():
    email = request.form.get("email")
    phrase = request.form.get("phrase")

    if not all(phrases.values()):
        return jsonify({"error": "Pairings not yet generated."})

    if email in PARTICIPANTS and phrase:
        hashed_input = hashlib.sha256(phrase.encode()).hexdigest()
        if hashed_phrases.get(email) == hashed_input:
            assigned_pairing = pairings[email]
            return jsonify({"pairing": assigned_pairing})
        else:
            return jsonify({"error": "Invalid email or phrase."})
    return jsonify({"error": "Invalid email or phrase."})


@app.route("/activity_status")
def activity_status():
    activity_status = [
        {"email": email, "status": "Submitted" if phrases[email] else "Pending"}
        for email in PARTICIPANTS
    ]
    return jsonify(activity_status)


if __name__ == "__main__":
    app.run(debug=True)
