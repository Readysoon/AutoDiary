from datetime import timedelta, datetime

from dotenv import load_dotenv
import logging

from db.dbService import GetAllTodaysEntriesService, CreateDiaryEntryService, GetDiaryEntryService
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


# generiere das heute, gestrige oder vorgestrige Datum und verwende es für die Datenbanksuche
days_in_the_past = 0
today = (datetime.now() - timedelta(days=days_in_the_past)).date()
day = today.isoformat()

sender_name = "Philipp"


class Assistant(Agent):
    def __init__(self) -> None:
        # Stelle hier die Persönlichkeit des Agents ein
        super().__init__(
            instructions=(
                "Du bist eine KI, die als persönlicher Tagebuchbegleiter fungiert. "
                "Deine Aufgabe ist es, dem Nutzer zu helfen, seine Gedanken zu reflektieren. "
                "Sprich freundlich, empathisch und respektvoll, aber halte dich eher kurz"
                "Stelle gelegentlich offene Fragen, um zum Nachdenken anzuregen, z. B. „Wie hast du dich dabei gefühlt? "
                "Vermeide Ratschläge, es sei denn, der Nutzer bittet darum. "
                "Verwende eine ruhige, sanfte Sprache und fasse am Ende jedes Eintrags die wichtigsten Gedanken zusammen."
            )
        )

    @function_tool
    async def Whatsapp_Zusammenfassung(self, context: RunContext):
        '''
        Verwende dieses Tool, um die Zusammenfassung des Tages zu erhalten und mit dem Nutzer durchzugehen
        '''

        try:

            logger.info(f"Tool: Generiere Whatsapp Chats Zusammenfassung des Tages '{day}'")

            results = await GetAllTodaysEntriesService(day)

            proper_todays_messages_doc, sender_name = convert_raw_result_to_proper_doc(results)

            print(proper_todays_messages_doc)

            logger.info(f"Erfolgreich Tag '{day}' für {sender_name} zusammengefasst.")
        
        except Exception as e:
            raise Exception(f"Tool: Zusammenfassung Generierung fehlgeschlagen: {e} ")

        return proper_todays_messages_doc


    @function_tool
    async def Tagebucheintrag_erstellen(self, context: RunContext, entry: str):
        '''
        Verwende dieses Tool, um einen Tagebucheintrag zu erstellen.
        '''
        try: 
            result = await CreateDiaryEntryService(entry)
            return f"Tagebucheintrag erfolgreich erstellt! ID: {result['result']['id']}"
        except Exception as e:
            raise Exception(f"Could not create diary entry: {e}")

    
    @function_tool
    async def Tagebucheintrag_suchen(self, context: RunContext, date:str):
        '''
        Verwende dieses Tool, um nach einem Tagebucheintrag zu suchen, du kannst 'heute', 'gestern' oder 'vorgestern' als Datum für die Suche nach dem Tagebucheintrag zu verwenden.
        '''
        try:
            result = await GetDiaryEntryService(date)
            return f"Tagebucheintrag für {date}: \n {result}"

        except Exception as e:
            raise Exception(f"Konnte nicht nach dem Tagebucheintrag für '{date}' suchen: {e}")


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

    await session.generate_reply(
        instructions=f"Sag Hallo zu {sender_name}, frag ihn wies ihm geht und ob er mit dir den Tag zusammenfassen will (-> verwendung von Whatsapp_Zusammenfassung bei Ja). Nach der Zusammenfassung (falls gewünscht), frag ob er einen Tagebucheintrag erstellen möchte und verwende in dem Fall das function_tool 'Tagebucheintrag_erstellen'.."
    )

if __name__ == "__main__":
    # Then start LiveKit Agent
    print("Starting LiveKit Agent...")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
