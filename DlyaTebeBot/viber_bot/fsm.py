user_states = {}

def set_state(user_id, state):
    user_states[user_id] = state

def get_state(user_id):
    return user_states.get(user_id, "default")

def clear_state(user_id):
    user_states[user_id] = None