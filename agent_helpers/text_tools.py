


def convert_raw_result_to_proper_doc(results):
    """
    Convert raw database results into a properly formatted document for the agent.
    Groups messages by chat_name and sorts them chronologically within each chat.
    
    Args:
        results: List of message dictionaries from the database
        
    Returns:
        str: Formatted document with grouped and sorted messages
    """
    from collections import defaultdict
    from datetime import datetime
    
    # Group messages by chat_name
    chats = defaultdict(list)
    
    for message in results:
        # Convert RecordID to string if needed
        if hasattr(message.get('id'), '__str__'):
            message['id'] = str(message['id'])
        
        # Clean up datetime strings (remove d' prefix if present)
        for field in ['entry_creation']:
            if field in message and isinstance(message[field], str):
                if message[field].startswith("d'") and message[field].endswith("'"):
                    message[field] = message[field][2:-1]  # Remove d'...'
        
        chat_name = message['chat_name']
        chats[chat_name].append(message)
    
    # Sort messages within each chat chronologically by time
    for chat_name in chats:
        chats[chat_name].sort(key=lambda x: x['time'])
    
    # Build the formatted document
    document_lines = []
    document_lines.append("# WhatsApp Nachrichten")
    document_lines.append("# Fasse die Chats in jeweils 3 - 4 Sätzen für Vormittag, Nachmittag, Abends zusammen. Schließe daraus was am Tag passiert ist.")
    document_lines.append(f"Date: {results[0]['date'] if results else 'N/A'}")
    document_lines.append(f"Total Messages: {len(results)}")
    document_lines.append(f"Total Chats: {len(chats)}")
    document_lines.append("")
    
    # Sort chats by name for consistent output
    for chat_name in sorted(chats.keys()):
        messages = chats[chat_name]
        document_lines.append(f"## Chat: {chat_name}")
        document_lines.append(f"Messages in this chat: {len(messages)}")
        document_lines.append("")
        
        for i, msg in enumerate(messages, 1):
            time_display = msg['time']
            sender = msg['name']
            message_text = msg['message']
            
            document_lines.append(f"**{i}. [{time_display}] {sender}:**")
            document_lines.append(f"{message_text}")
            document_lines.append("")
        
        document_lines.append("---")
        document_lines.append("")
    
    return "\n".join(document_lines)
    