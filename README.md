[![codecov](https://codecov.io/gh/iai-group/dagfinn/branch/main/graph/badge.svg?token=NMXV7BGZT7)](https://codecov.io/gh/iai-group/dagfinn)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Installation

To install Daggfinn and all its dependencies make sure you have anaconda distribution installed in your system and use the following commands:

```
conda env update -f environment.yaml
conda activate dagfinn

python3 -m spacy download en_core_web_md
```

**NB!** There is a [known issue](https://forum.rasa.com/t/problem-with-websockets/49570) with websockets and Rasa 3.0. If you get a server error on launching the webchat in your browser you might need to downgrade the sanic libraires:

```
pip install sanic==21.6.0
pip install Sanic-Cors==1.0.0
pip install sanic-routing==0.7.0
```

# Running

Before starting the bot and after every change we need to retrain the bot. This can be done with the command:
```
rasa train
```

To run the chatbot you will need two terminals.
The first one is for the *actions* server. You can start it by typing:

```
rasa run actions
```

In the second terminal you can start the Rasa server with all defined channels:

```
rasa run
```

**NB!** If you get Cross-Origin Resource Sharing (CORS) error in your browser after launching the webchat try to restart the server with the command:

```
rasa run --cors "*"
```

# Chatbot in terminal

You can start the terminal version of the chatbot with the command:

```
rasa shell
```

If you want to debug the NLU component, i.e., explore recognized entities or classified intents, you can run:

```
rasa shell nlu
```
