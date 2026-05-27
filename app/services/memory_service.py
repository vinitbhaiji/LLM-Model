import uuid

conversation_store = {}


def create_session():

    session_id = str(uuid.uuid4())

    conversation_store[session_id] = []

    return session_id


def get_or_create_session(session_id=None):

    if session_id and session_id in conversation_store:

        return session_id

    return create_session()


def add_message(session_id, role, content):

    if session_id not in conversation_store:

        conversation_store[session_id] = []

    conversation_store[session_id].append({
        "role": role,
        "content": content
    })


def get_conversation_history(
    session_id,
    limit=2
):

    history = conversation_store.get(
        session_id,
        []
    )[-limit:]

    formatted = ""

    for msg in history:

        formatted += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    return formatted