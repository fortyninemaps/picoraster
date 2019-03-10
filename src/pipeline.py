class Pipeline(object):

    def __init__(self, steps=None):
        self._instructions = steps if steps else []

    @property
    def instructions(self):
        return [instr for instr in self._instructions]

    def and_then(self, instruction):
        return Pipeline(self.instructions + [instruction])

    def apply(self, part):
        parts = [part]
        for instr in self.instructions:
            new_parts = []
            for p in parts:
                new_parts.extend(instr.apply(p))
            parts = new_parts
        return parts