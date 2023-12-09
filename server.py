from flask import Flask, request, jsonify, render_template
import random
import hashlib

app = Flask(__name__)

# Hardcoded emails
participants = [
]

# Store phrases and pairings
phrases = {email: None for email in participants}
pairings = {}
hashed_phrases = {}


def generate_pairings():
    shuffled = participants[:]
    random.shuffle(shuffled)
    return list(zip(shuffled, shuffled[1:] + shuffled[:1]))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        phrase = request.form.get("phrase")
        if email in participants and phrase:
            phrases[email] = phrase
            if all(phrases.values()):
                temp_pairings = generate_pairings()
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

    if email in participants and phrase:
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
        for email in participants
    ]
    return jsonify(activity_status)


if __name__ == "__main__":
    app.run(debug=True)
