# Installation

The easiest way to install DAGFiNN and all of its dependencies is by using pip:

```
python -m pip install --upgrade pip
pip install -r requirements.txt

python -m spacy download en_core_web_md
```

**NB!** There is a [known issue](https://forum.rasa.com/t/problem-with-websockets/49570) with websockets and Rasa 3.0. If you get a server error on launching the webchat in the browser you might need to downgrade the sanic libraires. To do so, use the commands:

```
pip install sanic==21.6.0
pip install Sanic-Cors==1.0.0
pip install sanic-routing==0.7.0
```