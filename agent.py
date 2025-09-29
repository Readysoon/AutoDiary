from datetime import timedelta, datetime

from dotenv import load_dotenv
import logging

from db.dbService import GetAllTodaysEntriesService
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

name = "Philipp"


class Assistant(Agent):
    def __init__(self) -> None:
        # Stelle hier die Persönlichkeit des Agents ein
        super().__init__(
            instructions=(
                "Du bist eine KI, die als persönlicher Tagebuchbegleiter fungiert. "
                "Deine Aufgabe ist es, dem Nutzer zu helfen, seine Gedanken zu reflektieren. "
                "Sprich freundlich, empathisch und respektvoll. "
                "Stelle gelegentlich offene Fragen, um zum Nachdenken anzuregen, z. B. „Wie hast du dich dabei gefühlt?“. "
                "Vermeide Ratschläge, es sei denn, der Nutzer bittet darum. "
                "Verwende eine ruhige, sanfte Sprache und fasse am Ende jedes Eintrags die wichtigsten Gedanken zusammen."
            )
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
        tts = cartesia.TTS(voice="384b625b-da5d-49e8-a76d-a2855d4f31eb", language="de"),
        vad=silero.VAD.load(),
        # turn_detection=MultilingualModel(), # disabled because it was causing errors when livekit wanted to download it from the internet but docker didnt want it
        turn_detection=None
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

    # Flow unterbrechen um Nachrichten das Tages zu scrapen und zusammenzufassen und durchzulesen
    session.interrupt()

    session.input.set_audio_enabled(False) # stop listening

    try:
        logger.info(f"Generiere WhatsApp Zusammenfassung des Tages...")

        days_in_the_past = 1

        today = (datetime.now() - timedelta(days=days_in_the_past)).date()
        day = today.isoformat()

        results = await GetAllTodaysEntriesService(day)

        proper_todays_messages_doc = convert_raw_result_to_proper_doc(results)

        print(proper_todays_messages_doc)

        await session.generate_reply(
            instructions=proper_todays_messages_doc
        )

    finally:
        session.input.set_audio_enabled(True) # start listening again
    

if __name__ == "__main__":
    # Then start LiveKit Agent
    print("Starting LiveKit Agent...")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
