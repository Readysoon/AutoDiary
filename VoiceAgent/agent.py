from dotenv import load_dotenv
import logging

from datetime import date

from db.dbService import GetEntryService

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
            instructions="Du bist ein hilfsbereiter deutscher AI Bot"
        )

    @function_tool
    async def date_example(self, context: RunContext):
        '''
        Verwende diese Tool um das Datum aufzurufen
        '''

        logger.info(f"Looking up the date")

        return str(date.today())
    


    # Tool zur Verwendung (Suche) einer SurrealDB Datenbank
    @function_tool
    async def db_example(self, context: RunContext, search_string: str):
        '''
        Verwende dieses Tool, um etwas in der Datenbank nachzuschauen
        '''
        logger.info(f"Using the Database")

        return await GetEntryService(search_string=search_string)

    

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

    # Designe hier den Workflow?
    await session.generate_reply(
        instructions="Begrüße den Nutzer"
    )
    
    

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
