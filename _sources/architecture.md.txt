# Architecture

DAGFiNN follows a client-server architecture. The server is built on top of the open-source [Rasa](https://rasa.com/open-source/) conversational framework. Rasa handles dialogue management by classifying intents and then invoking the respective skills to generate a response. 

Skills are implemented using a combination of rules, stories, and forms, which represent the various (increasingly complex) ways to provide training data in Rasa to train the dialogue management model. 

![architecture](_static/dagfinn_architecture.png)