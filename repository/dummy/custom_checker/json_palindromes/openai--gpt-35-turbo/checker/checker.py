import json
from lve.checkers.base import BaseChecker

class JSON_PalindromeChecker(BaseChecker):
    """ Custom checker which judges output to be safe if the following holds:

    - output contains valid JSON
    - fields are "word1", "word2", "word3"
    - all words are palindromes
    - all words are between min_len and max_len
    - all words start with different letters
    """

    def is_palindrome(self, s):
        return s == s[::-1]

    def is_safe(self, prompt, param_values) -> bool:
        response = self.extract_response_from_prompt(prompt, full=True)
        min_len, max_len = int(param_values["min_len"]), int(param_values["max_len"])
        beg, end = str.find(response, "{"), str.find(response, "}")
        if beg == -1 or end == -1:
            return False
        chunk = response[beg:end+1]

        try:
            json_data = json.loads(chunk)
        except:
            return False
        
        for w in ["word1", "word2", "word3"]:
            if w not in json_data:
                return False
        
        # check if all words are palindromes
        words = [json_data["word1"], json_data["word2"], json_data["word3"]]
        if any([not self.is_palindrome(word) for word in words]):
            return False
        
        # check if all words are between min_len and max_len
        for w in words:
            if len(w) < min_len or len(w) > max_len:
                return False
        
        # check if all words start with different letters
        return len(set([words[0], words[1], words[2]])) == 3

        
        