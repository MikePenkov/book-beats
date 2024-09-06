system_message = """
Your role is to be a music recommender. Your primary role today is to suggest songs that will fit the vibe and atmosphere that your customers are looking for. Your customers are looking for music they can listen to while they are reading their favourite book. You need to suggest appropriate tracks that complement the atmosphere but are not too loud or distracting. Your customers should stay focused on imersing themselves in their favourite book.
"""

def generate_prompt(vibe: str) -> str:
    return f"""
        Task: Suggest 5 songs that will fit well with this book or atmosphere - {vibe}
        """ + """
        Context: The results should be a json list of 5 songs and their artists. It should be easy to parse in python. Do not include any other text.

        Output: {
                "items": [
                    {
                        "song": SONG_NAME,
                        "artist": SONG_ARTIST
                    }
                ]
            }

        Evaluation Criteria: The songs are meant to help the customer imerse themselves in the book they are reading and should not be too distracting. The 5 songs should also transition smoothly from one to the next 
    """