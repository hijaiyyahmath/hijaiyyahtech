class OwnerModel:
    """Deterministic owner recognizer (offline)."""
    def __init__(self):
        self.observations = []

    def observe(self, data: str):
        # Deterministic append for demo purposes
        if data not in self.observations:
            self.observations.append(data)

    def get_state_hash(self) -> str:
        import hashlib
        return hashlib.sha256(",".join(sorted(self.observations)).encode()).hexdigest()
