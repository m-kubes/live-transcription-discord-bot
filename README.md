# Live Transcription Discord Bot
To use, add a .env file with your discord and openAi tokens in it in this format: \
`DISCORD_TOKEN=''` \
`CHATGPT_TOKEN=''` 
# Commands Overview
### /listen
Joins your call and listens indefinitely \
(doesn't do anything if banned words or transcription aren't on)
### /leave
The bot leaves the current call it's in
### /banword (word)
Adds a string to the banned words list \
If any user says a banned word while the bot is listening in a call, the user is disconnected from the voice call
### /unbanword (word)
Removes string from banned words list if found
### /starttranscribing (channel)
Indefinitely transcribes any words heard while listening into the specified text channel
### /stoptranscribing
Stops transcribing from any channels
