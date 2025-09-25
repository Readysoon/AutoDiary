from datetime import date

from dotenv import load_dotenv
import logging
import asyncio

from db.dbService import GetEntryService
from whatsapp_handling.main import collect_todays_messages

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
            instructions="Du bist mein Tagebuch. Sprich mich mit Philipp und lieb an."
        )

    @function_tool
    async def date_example(self, context: RunContext):
        '''
        Verwende diese Tool um das Datum aufzurufen
        '''

        logger.info(f"Looking up the date")

        return str(date.today())


    # Beispiel Tool, was zeigt wie man erfolgreich zwei Parameter mit einer Funktion erfassen kann
    @function_tool
    async def name_und_geburtstag(self, context: RunContext, name: str, geburtstag: str):
        '''
        Verwende dieses Tool, um name und Geburtstag einzutragen
        '''

        logger.info(f"Trage Name ({name}) und Geburtstag ({geburtstag}) ein")

        return name, geburtstag

        


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

    # Lege hier Luisa die  heutigen 
    await session.generate_reply(
        instructions=""
    )
    
    

if __name__ == "__main__":

    # nach load_dotenv geht nicht, weil dann livekits multiprocessing greift und das Scraping dann mehrmals ausgeführt werden würde
    print("Whatsapp Scraping startet... ")
    asyncio.run(collect_todays_messages())
    print("Whatsapp Scraping beendet... ")


    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
