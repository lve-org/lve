"""
Simple parser for LVE README.md files, which are written in a 
templated-markdown format.

This parser can be used to selectively filter some parts of the 
README, e.g. to exclude the "Prompt" or any other section.
"""
class LVEReadmeParser:
    def __init__(self, contents):
        self.contents = contents
        self.sections = {}
        self.lines = self.contents.split("\n")
        self.sections = []
        
        self.parse()

    def parse(self):
        lines = []
        section_name = None

        for line in self.lines:
            if line.startswith("**"):
                self.sections.append((section_name or "", "\n".join(lines)))
                lines = []
                section_name = line.split("**")[1]
            lines.append(line)
            
            # with code blocks, only include the first one (supports `...` and ```...```)
            so_far = "\n".join(lines)
            ticks = so_far.count("`")
            if ticks % 2 == 0 and ticks > 0:
                self.sections.append((section_name or "", "\n".join(lines)))
                lines = []
                section_name = None

        self.sections.append((section_name or "", "\n".join(lines)))
    
    def emit(self, exclude=None):
        exclude = exclude or []
        content = ""

        for section, lines in self.sections:
            if section.lower() in exclude:
                continue
            content += lines + "\n"

        return content
