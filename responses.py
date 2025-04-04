from random import choice, randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == 'help':
        return ("after @, type:" + 
                "\n**[join]** for the bot to join your call" +
                "\n**[leave]** for the bot to leave your call" +
                "\n**[play/sing]** + **[*Youtube URL*]** for the bot to play a youtube video" +
                "\n**[skip]** for the bot to skip a song"
                )
    else:
        return "are you speaking english?"
