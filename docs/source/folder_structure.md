# Folder Structure

## Actions

Here are python scripts related to the execution of custom actions. These include providing dynamic responses based on data from databases or external APIs.

## Addons

Here you can find the code for the custom connector. Custom connector is responsible for synchronizing inputs/outputs between Furhat and the external display.

## Data

This folder contains training data for the DAGFiNN. This includes user utterances to recognize, rules and story paths based on user intents, and responses to those intents.

## DB

This folder contains databases for DAGFiNN. Those include relevant information for the recommender modules (e.g., conference session and POI data) and dialogue tracking (i.e., historical conversations).

## Scripts

Here are stored additional scripts used e.g., for data processing and preparation.

## Tests

Unit tests for python scripts and tests for predicted intents based on the rules and stories.