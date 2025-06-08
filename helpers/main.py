from langchain.chains import LLMChain
import datetime
import json
import re
from typing import Any, Union
from pymongo import MongoClient
from dateutil.relativedelta import relativedelta
from langchain.tools import tool


# --- Utility Functions for Date Placeholders ---
def get_iso_datetime(dt: datetime.datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    elif dt.tzinfo != datetime.timezone.utc:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt.isoformat(timespec='milliseconds') + 'Z'

def get_today_start_utc(): return get_iso_datetime(datetime.datetime.now(datetime.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0))
def get_yesterday_start_utc(): return get_iso_datetime((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
def get_current_utc_now(): return get_iso_datetime(datetime.datetime.now(datetime.timezone.utc))
def get_last_month_start_utc():
    now = datetime.datetime.now(datetime.timezone.utc)
    first_day = now.replace(day=1, hour=0, minute=0, second=0)
    return get_iso_datetime(first_day - relativedelta(months=1))
def get_last_month_end_utc():
    now = datetime.datetime.now(datetime.timezone.utc)
    first_day = now.replace(day=1, hour=0, minute=0, second=0)
    return get_iso_datetime(first_day - datetime.timedelta(microseconds=1))
def get_last_7_days_start_utc():
    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    return get_iso_datetime(dt.replace(hour=0, minute=0, second=0, microsecond=0))

def parse_and_format_date_placeholder(placeholder: str) -> str:
    if placeholder == "{{yesterday_start}}": return get_yesterday_start_utc()
    elif placeholder == "{{today_start}}": return get_today_start_utc()
    elif placeholder == "{{now}}": return get_current_utc_now()
    elif placeholder == "{{last_month_start}}": return get_last_month_start_utc()
    elif placeholder == "{{last_month_end}}": return get_last_month_end_utc()
    elif placeholder == "{{last_7_days_start}}": return get_last_7_days_start_utc()

    match_start = re.match(r"^{{(\d{4}-\d{2}-\d{2})_start}}$", placeholder)
    match_end = re.match(r"^{{(\d{4}-\d{2}-\d{2})_end}}$", placeholder)
    if match_start:
        dt = datetime.datetime.strptime(match_start.group(1), "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        return get_iso_datetime(dt)
    elif match_end:
        dt = datetime.datetime.strptime(match_end.group(1), "%Y-%m-%d").replace(hour=23, minute=59, second=59, microsecond=999999)
        return get_iso_datetime(dt)

    print(f"Warning: Unrecognized date placeholder: {placeholder}")
    return placeholder


def replace_placeholders(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: replace_placeholders(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_placeholders(v) for v in obj]
    elif isinstance(obj, str) and obj.startswith("{{") and obj.endswith("}}"):
        return parse_and_format_date_placeholder(obj)
    return obj



# eleven_labs_tts_tool = ElevenLabsText2SpeechTool()

# @tool
# def text_to_speech(text_output: str) -> str: 
#     """
#     Converts a text string into spoken audio using Eleven Labs and streams it directly.
#     This tool will *not* return raw audio bytes but will instead attempt to play
#     or save the audio directly as a side effect.

#     Args:
#         text_output (str): The text to be spoken.

#     Returns:
#         str: A confirmation message indicating the speech was streamed.
#     """
#     print(f"\nAttempting to stream speech via Eleven Labs for: '{text_output}'")
#     try:
#         # The stream_speech method typically yields audio chunks.
#         # In a web application or specific environment, you'd handle these chunks
#         # to play them back in real-time.
#         # For a basic script, you might just iterate through it or save it.

#         # Example: Streaming and saving to a file (for demonstration)
#         # This part depends on how you want to handle the audio output.
#         # In a real-time voice assistant, you'd feed these chunks to an audio playback library.
#         speech_file = eleven_labs_tts_tool.run(text_output)
#         eleven_labs_tts_tool.play(speech_file)
#         # audio_chunks = eleven_labs_tts_tool.stream_speech(text_output)

#         # --- IMPORTANT: How you handle 'audio_chunks' dictates real-time playback ---
#         # If you're in a Jupyter/Colab notebook and want to hear it immediately,
#         # you might need specific display integrations.
#         # For simple testing, you can save it:
#         # with open("output.mp3", "wb") as f:
#         #     for chunk in audio_chunks:
#         #         f.write(chunk)
#         # print("Audio streamed and saved to output.mp3 (for testing).")

#         # For demonstration, let's just confirm it started streaming.
#         # You might consume chunks here if needed for specific environments.
#         # If `stream_speech` is truly meant for direct stream to client,
#         # its internal logic handles the streaming, and this function
#         # just needs to initiate it.
#         # For typical usage where you want to actually *use* the chunks:
#         # all_audio_bytes = b"".join(list(audio_chunks)) # Collect all chunks
#         # Now, you'd play `all_audio_bytes`
#         # For demonstration, let's say it was successful.

#         return f"Speech for '{text_output[:50]}...' was streamed successfully."
#     except Exception as e:
#         return f"Failed to stream speech via Eleven Labs: {str(e)}"

