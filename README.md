<!-- [![codecov](https://codecov.io/gh/iai-group/dagfinn/branch/main/graph/badge.svg?token=NMXV7BGZT7)](https://codecov.io/gh/iai-group/dagfinn) -->
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# DAGFiNN

DAGFiNN is a conversational conference assistant that can be made available for a given conference both as a chatbot on the website and as a Furhat robot physically exhibited at the conference venue. Conference participants can interact with the assistant to get advice on various questions, ranging from where to eat in the city or how to get to the airport to which sessions we recommend them to attend based on the information we have about them. The overall objective is to provide a personalized and engaging experience and allow users to ask a broad range of questions that naturally arise before and during the conference.

# Features


  * Provide recommendations across multiple domains, have basic conversational capabilities, and personalization integrated into a single system.
    - Currently, recommenders are built for point-of-interest (POI) and conference content
  * Support multiple user interfaces (UI)
    - A Web chat and a Furhat robot with an optional external screen
    - Use of rich responses customized to each user interface to effectively convey information.
  * Utilize multiple input modalities
    - Furhat is a social robot with a microphone, speaker, and camera, which makes it possible to recognize users that interacted with the robot previously.


# Disclaimer

DAGFiNN is not (yet) a mature production-level system, but rather a research prototype. We welcome contributions on all levels (pull requests, suggestions for improvements, feature requests, etc.).
# Installation

The easiest way to install DAGFiNN and all of its dependencies is by using an anaconda distribution with the following commands:

```
conda env update -f environment.yaml
conda activate dagfinn

python3 -m spacy download en_core_web_md
```

**NB!** There is a [known issue](https://forum.rasa.com/t/problem-with-websockets/49570) with websockets and Rasa 3.0. If you get a server error on launching the webchat in the browser you might need to downgrade the sanic libraires. To do so, use the commands:

```
pip install sanic==21.6.0
pip install Sanic-Cors==1.0.0
pip install sanic-routing==0.7.0
```

# Running

DAGFiNN can be run in several ways. It can run on the Furhat robot, as a webchat, or as a command line application. Before starting and after every code change, the bot needs to be retrained. Use the command:
```
rasa train
```

To run DAGFiNN you will need to start two services.
The first one is the *actions* server. You can start it by typing:

```
rasa run actions
```

The second is the Rasa server with all defined channels:

```
rasa run
```

**NB!** In some cases, you might see Cross-Origin Resource Sharing (CORS) error after launching the webchat. In that case restart the server with the command:

```
rasa run --cors "*"
```

## Command line application

You can start the command line version of the chatbot with the command:

```
rasa shell
```

If you want to debug the NLU component, i.e., explore recognized entities or classified intents, you can run:

```
rasa shell nlu
```

## Webchat

You can start a chat webserver as follows. If you do not use the default port to run the Rasa server, you need to change the port in this [file](ui/furhat-screen/index.js). 

```shell
cd dagfinn/ui/furhatscreen
python -m http.server
```

By default the server runs on port 8000. To change it start the server with the command:

```shell
python -m http.server PORT
```

## Furhat

TBD

# Citation
If you are using this repository, please cite the following paper:

```
@inproceedings{10.1145/3523227.3551467,
   author = {Kostric, Ivica and Balog, Krisztian and Aresvik, T\o{}ll\o{}v Alexander and Bernard, Nolwenn and D\o{}rheim, Eyvinn Thu and Hantula, Pholit and Havn-S\o{}rensen, Sander and Henriksen, Rune and Hosseini, Hengameh and Khlybova, Ekaterina and Lajewska, Weronika and Mosand, Sindre Ekrheim and Orujova, Narmin},
   title = {DAGFiNN: A Conversational Conference Assistant},
   year = {2022},
   publisher = {Association for Computing Machinery},
   booktitle = {Proceedings of the 16th ACM Conference on Recommender Systems},
   pages = {628–631},
   series = {RecSys '22}
}
```