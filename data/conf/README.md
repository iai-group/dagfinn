# Conference Skill
Gives information about the different sessions at the conference.

### Functioning questions
- What is the next session about?
  - (example answer: The next session is Paper session 2)
  - You can then follow up with: Tell me about [paper session 2].
  
- Tell me about the keynotes.
- Tell me about [todays] keynote.
- Tell me about [tomorrows] schedule.
- Tell me about [speaker]. (speaker names can be found in speakers.yml)
- Can you recommend me a session? (session topics can be found in keywords.yml)

# Conference-related Information Needs

## Single-turn examples:

- When does the next session start?
- What is the next session about?
- Where will the next session be?
- Who are the speakers at the next session?
- Who are the keynote speakers of the conference?
- What will tomorrow's keynote be about?
- What is the schedule for the workshops?
- Are there any sessions going on right now?
- When is the next paper session?
- When is the lunch break?
- When does the opening ceremony start?
- When is [name]'s talk?

## Multi-turn examples (non-personalized):

- [USER] Can you recommend me a session to attend?
- [DAGFINN] What topics are you interested in?
- [USER] I'm interested in recommender systems
- [DAGFINN] Session 7, scheduled at 12:30 tomorrow is about recommender systems.
<br/>

- [USER] Can you recommend me a session to attend?
- [DAGFINN] What topics are you interested in?
- [USER] Nothing in particular.
- [DAGFINN] The next session at 15:00 is about recommender systems.
<br/>

- [USER] Can you recommend me a workshop to attend?
- [DAGFINN] Any topic in particular?
- [USER] Robots.
- [DAGFINN] The workshop at 10:00 is about robots.
<br/>

## Slots, intents and actions

### Slots

- user_interest: What type of conference content they like.
- session_time: A set time the user enters to see if there are any sessions around then.
- session_date: Date of a session.
- session_name: Name of a person hosting a session.
- session_room: Name/number of session room.


### Intents

- when_next_session
  - "When does the next session start?"
- what_next_session
  - "What is the next session about?"
- where_next_session
  - "Which room will the next session be in?"
- who_next_session
  - "Who will host the next session?"

### Responses/Stories

Actions will take care of most of the replies, unless its like the one above where the information is static and doesnt change

### Actions

- get_next_session
  - Will find the next session depending on what the current time is.
- get_session
  - Same as the one above except it gets the closest session to an entered time.
- get_opening_ceremony
  - Gets the time when the opening ceremony takes place

Most other actions will use the ones above to get the necessary info like:
- get_session_who
  - Gets who hosts a certain session.

