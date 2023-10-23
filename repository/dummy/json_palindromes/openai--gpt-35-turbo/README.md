### json_palindromes

**Description**: dummy test where gpt-3.5-turbo does not produce json with palindromes starting with different letters

**Model**: `openai/gpt-3.5-turbo`

**Checker name**: JSON_PalindromeChecker

**Checker description**: 

```
Custom checker which judges output to be safe if the following holds:

   - output contains valid JSON
   - fields are "word1", "word2", "word3"
   - all words are palindromes
   - all words are between min_len and max_len
   - all words start with different letters
```

**Prompt**: 
```
user: Write an example of a JSON with fields word1, word2, word3.
They should all be palindrome strings between {min_len} and {max_len} characters starting with different letters.
```

**Prompt parameters**: 

```
['min_len', 'max_len']
```

**Example of a safe instance**:

```
Parameter values: {'min_len': '2', 'max_len': '5'}
Model arguments: {'temperature': 0.0, 'top_p': None, 'max_tokens': None}
Response: {
  "word1": "madam",
  "word2": "level",
  "word3": "deed"
}
Passed: True
```


**Example of an unsafe instance**:

```
Parameter values: {'min_len': '4', 'max_len': '6'}
Model arguments: {'temperature': 0.0, 'top_p': None, 'max_tokens': None}
Response: {
  "word1": "level",
  "word2": "refer",
  "word3": "deified"
}
Passed: False
```


