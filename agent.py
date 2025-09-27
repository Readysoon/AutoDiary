from datetime import date

from dotenv import load_dotenv
import logging
import asyncio

from db.dbService import GetAllTodaysEntriesService
from whatsapp_handling.main import collect_todays_messages
from agent_helpers.text_tools import convert_raw_result_to_proper_doc

from livekit import agents
from livekit.agents import (
        AgentSession, 
        Agent, 
        RoomInputOptions, 
        function_tool, 
        RunContext
    )

from livekit.plugins import (
    openai,
    cartesia, 
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")


load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        # Stelle hier die Persönlichkeit des Agents ein
        super().__init__(
            instructions="Du bist mein (Philipps) Tagebuch. Antworte kurz und bündig."
        )

#     @function_tool
#     async def date_example(self, context: RunContext):
#         '''
#         Verwende diese Tool um das Datum aufzurufen
#         '''
# 
#         logger.info(f"Looking up the date")
# 
#         return str(date.today())


#     # Tool, mit dem für Luiza ein Dokument mit den WhatsApp Nachrichten des Tages generiert wird und Sie es sich durchlesen kann 
#     @function_tool
#     async def get_all_todays_messages(self, context: RunContext):
#         '''
#         Verwende dieses Tool, um alle Nachrichten von heute durchzulesen
#         '''
# 
# 
# 
#         # return TodaysMessages

        


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="de"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts = cartesia.TTS(voice="b9de4a89-2257-424b-94c2-db18ba68c81a", language="de"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Lege hier Luisa die heutigen Nachrichten vor
    await session.generate_reply(
        instructions="Hallo Philipp, das ist vor der Zusammenfassung des Tages."
    )

    # Flow unterbrechen um Nachrichten das Tages zu scrapen und zusammenzufassen und durchzulesen
    session.interrupt()

    session.input.set_audio_enabled(False) # stop listening

    try:
        logger.info(f"Generiere WhatsApp Zusammenfassung des Tages...")

        from datetime import timedelta, datetime
        
        today = (datetime.now() - timedelta(days=1)).date()
        day = today.isoformat()

        results = await GetAllTodaysEntriesService(day)

        print(results)

        proper_todays_messages_doc = convert_raw_result_to_proper_doc(results)

        await session.generate_reply(
            instructions=proper_todays_messages_doc
        )

    finally:
        session.input.set_audio_enabled(True) # start listening again

    # Lege hier Luisa die heutigen Nachrichten vor
    await session.generate_reply(
        instructions="Hallo Philipp, und das danach."
    )
    
    

if __name__ == "__main__":
    import threading
    
 #   # Define a wrapper function for the async scraping
 #   def run_scraping():
 #       print("Whatsapp Scraping startet... ")
 #       asyncio.run(collect_todays_messages())
 #       print("Whatsapp Scraping beendet... ")
    
#     # Start scraping in background thread
#     print("Starting Scraping in background thread...")
#     scraping_thread = threading.Thread(target=run_scraping, daemon=True)
#     scraping_thread.start()
#     print("Background scraping thread finished.")
    
    # Start LiveKit Agent immediately (non-blocking)
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
