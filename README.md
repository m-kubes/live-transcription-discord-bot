# Live Transcription Discord Bot
Requires environment variables: \
`DISCORD_TOKEN` \
`CHATGPT_TOKEN` 
# Commands Overview
### /listen
Joins your call and listens indefinitely \
(functionality requires turning on banned words or transcription)
### /leave
The bot leaves the current call it's in
### /banword (word)
Adds a string to the banned words list \
If any user says a banned word while the bot is listening in a call, the user is disconnected from the voice call
### /unbanword (word)
Removes string from banned words list
### /starttranscribing (channel)
Indefinitely transcribes any words while listening
### /stoptranscribing
Stops transcribing from any channels
