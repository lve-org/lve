import json
import os
import re
from enum import Enum
from typing import Any, List, Union, Optional

from pydantic import BaseModel, RootModel, model_validator, ValidationError
from pydantic.dataclasses import dataclass

class Role(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

    def __str__(self):
        return self.value

@dataclass
class Message:
    content: Optional[str] = None
    role: Role = Role.user
    variable: str = None
    image_url: Optional[str] = None
    

def get_prompt(lines):
    full = "".join(lines)
    
    # see if text is placeholder
    if re.fullmatch(r"^\s*<please fill in>\s*$", full):
        return None

    # see if text is jsonl-like
    try: 
        line_json = [json.loads(line) for line in lines] 
        prompt = []
        for jo in line_json:
            assert isinstance(jo, dict) # make sure it is not a list
            prompt.append(Message(**jo))
        return prompt
    except json.decoder.JSONDecodeError:
        pass
        
    # there is a single multi-line json object
    try:
        full_json = json.loads(full)
        if isinstance(json, dict):
            return [Message(**full_json)]
        else:
            raise Exception("Unsopported JSON format. Messages must either be a single JSON object or one JSON object per line (JSONL) or a string.")
    except json.decoder.JSONDecodeError:
        pass
       
    # treat text as string
    return [Message(content=full, role=Role.user)]