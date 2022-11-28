# About

The Rasa skill is a basic skill that waits for a user to enter the attention zone and then attends to it.

When Furhat is in the attention mode, it listens for a user input and sends the utterance to the Rasa server using rest API.
Utters the response back to the user and listens for the next utterance.

The required Kotlin code is under `src/main/kotlin/furhatos/app/rasa/`.

# Usage

The communication to the Rasa server is implemented in `<Kotlin-code>/flow/interaction.kt`. At the top of the file, after imports we declare the constant `URL` which points to the Rasa rest API, in this example to the localhost on port 5005.

To start the skill follow instructions [here](../README.md).

Make sure the Rasa servers are running -- see [here](/README.md).
