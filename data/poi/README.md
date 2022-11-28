# Point of Interest/Restaurant Recommendations

Check instructions [here](../../scripts/poi/README.md) to create a POI database.

The following utterances in the file [nlg.yml](nlg.yml) should be adapted to your use case:
* utter_general_poi_recommendation
* utter_see_more_bus_info
* utter_route_to_hospital
* utter_route_to_airport
* utter_general_bus_information
* utter_recommend_taxi

## Answerable requests (examples)

- What is there to see in Stavanger?
- Can you recommend me some bars?
- You know of any good Italian restaurants?
- Where can I go running?
- Where can I go hiking?
- Is there somewhere cheaper?
- How do I get there?
- How do I get to the airport?

## Implemented features
### Entities

- `poi_category` - type of location the user is looking for. E.g. restaurant, bar, cinema.
- `poi_tag` - product or service a location might provide. E.g. Italian food, bowling, coffee.
- `transport_preference` - preferred mode of transport indicated by the user.

### Slots

- `recommended_poi` - dictionary object containg information about the last recommended point of interest.
- `liked_poi_tags` - list of poi_tags the user said they wanted.
- `disliked_poi_tags` - list of poi_tags the user said they did not want.

### Implemented intents
#### Ask POI recommendation

User asks for advice on places to see without further details. Gets asked to provide more specific preferences.

#### Ask restaurant recommendation

User expresses hunger or interest in finding a place to eat. Gets asked follow-up question to clarify preferences.

#### Inform POI category

User expresses interest in finding a particular type of place. Gets recommended top rated point of interest with matching `poi_category`.

#### Inform POI tag

User expresses interest or disinterest in a particular product or service. Gets recommended place based on these `poi_tags`.

#### Ask cheap POI

User gets recommended a cheap place of interest. Inherits category, likes and dislikes from earlier.

#### Ask does POI have

User asks whether the previously recommended place has a certain POI tag. If it doesn't but another POI does, gets recommended that one.

#### Ask POI transport

User asks how to get somewhere, get's asked whether they would like to travel by bus or taxi.

#### Inform transport preference

User informs what mode of transportation they prefer. Receives response according to a number of factors.


# Originally envisioned features

## Example conversations
### Single turn examples

- What restaurants can I find nearby?
- Which bus goes from here to the airport?
- Are there any bars open now?
- How much does a beer cost here?
- Where can I go running?
- What is the closest grocery store from here?
- Are they open on Monday?

### Multi-turn examples

#### Example 1

- [USER] Are there any interesting places to see in town?
- [DAGFINN] {Best compromise between location, opening hours and rating} is a popular place near you.
- [DAGFINN] (Display several options on screen)
- [DAGFINN] Were you looking for anything in particular?
- [USER] Are there any museums?
- [DAGFINN] Yes, you should check out {best match with museum-tag}.
- [DAGFINN] (Display other options on map)

#### Example 2

- [USER] Can you recommend some places to eat?
- [DAGFINN] Yes of course, what would you like to eat today?
- [USER] I am a vegan, can you recommend some vegan places or where they serve vegan dishes?
- [DAGFINN] Yes, {best match based on vegan-tag} has the best vegan food.
- [USER] It is a bit expensive, can you recommend a cheaper place?
- [DAGFINN] Yes, {find next best option with lower price} is both cheap and vegan friendly.

## Slots, intents and actions

### Slots

#### P0 - Must have

- `POI_preferences`: Tags associated with user preferences. E.g. Mexican, vegan, beer, hiking.
  - Predefined list of recognized tags.

- `user_location`: The distance between the user and POIs will be used when ranking POIs.

- `chosen_POI`: Database-ID of the POI currently in focus.

  - E.g. there is only one airport in Stavanger, and therefore this POI should be chosen automtically if category==airport.
  - If a user references a previous recommendation, this should be recognized and picked by DAGFINN.

- `preferred_opening_hours`: Can be compared to restaruant opening hours. E.g. "now" = open for the next two hours, "tomorrow at 6" etc.


#### P1 - Should have

- `liked_POIs`: DAGFINN should keep track of the POIs the user has expressed favorability towards. This will be stored as a list of database IDs.

- `disliked_POIs`: Likewise, the POIs the user didn't like should also be tracked.

- `has_nearby_preference`: Ranking will emphasize proximity more.

- `has_rating_preference`: Ranking will emphasize rating more.

#### P2 - Would be nice to have

`previous_queries`: DAGFINN could look back on the things he recommended previously. How this is to be stored, and how many steps back it should be able to look is tbd.

### Intents

- `look_for_POI`
  - "Are there any places to run nearby?"
- `look_for_transport`
  - "How do I get to the city center?"
- `look_for_restaurant`
  - "I am hungry."
- `question_about_POI`
  - "Do they have beer?"

### Responses/Stories

Most responses will be generated through actions. Others will be associated with tags, and some will be added to make the flow of the converssation better.

### Actions

All actions will be able to display details on screen and web-interfaces as well as making the robot talk.

#### P0 - Must have

- `recommend_POI`: Recommends one or multiple locations depending on the modality. Gives best compromise between location, price, etc. by default. Narrows down and adjusts based on user preferences.
  - This can be called again and again as slots are updated throughout a conversation.

- `talk_about_POI`: DAGFINN should be able to compare some of the attributes of the database to slot values provided by the user. E.g. opening hours, rating etc.
  - Requires *chosen_POI*

#### P1 - Should have

- `recommend_transport`: Gives transit information (bus etc.) for going to a place.
  - Requires *chosen_POI* and *user_location*
  - This would have to be connected to Google Maps or Kolombus etc.
