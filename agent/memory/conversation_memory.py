class ConversationMemory:
    def __init__(self, max_memory=8):
        self.max_memory = max_memory
        self.history = []

    def add(self, role, content):
        self.history.append((role, content))
        self.history = self.history[-self.max_memory:]

    def render(self, last_n=4):
        items = self.history[-last_n:]
        return "\n".join(f"{r.capitalize()}: {c}" for r, c in items)

    def clear(self):
        self.history = []
