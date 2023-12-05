---
date: 2023-12-02
---
# Community Challenges No. 1

<img align="right" src="/challenges_blog.png" width="500">

Together with the public announcement of our LVE Repository, we are also excited to announce the first batch of our red teaming community challenges! We hope these challenges raise general awareness about various language model vulnerabillities in the areas of privacy, reliability, responsibility, security, trust, and ultimately help us build safer models.

## Community Challenges

The goal of each community challenge is to find a prompt that triggers a particular safety issue in the LLM (e.g. inferring private information or generating spam). Each challenge contains several levels with varying difficulty, and a leaderboard showing the most successful users. The best prompts for each challenge will be committed to the LVE Repository and available for everyone to use and learn from!

### <span class='emoji'>📍</span> [Location Inference](/challenges/location-inference/easy.html)

Recently, we have seen a growing concern that LLMs can be used for [surveillance and spying](https://www.forbes.com/sites/thomasbrewster/2023/11/16/chatgpt-becomes-a-social-media-spy-assistant/). In fact, various actors could use LLMs to scan social media and infer various demographic attributes about the users, and use this information for various purposes, ranging from selling ads to things like targeted phishing attacks.
This challenge demonstrates how GPT-4 can infer the location of a person from a seemingly innocous comment. This capability, along with inferring other personal attributes (e.g. age, marriage status and income), has recently been proposed in the *Beyond Memorization: Violating Privacy Via Inference with Large Language Models* ([https://arxiv.org/abs/2310.07298v1](https://arxiv.org/abs/2310.07298v1)). The paper shows that LLMs can infer these attributes with similar accuracy as humans, while being ~100x faster and ~240x cheaper which could enable online profiling and potentially privacy violation at scale. In this challenge, we have two levels of difficulty, where in the second level part of the input has been redacted to make it harder for the LLM to infer private information.

### <span class='emoji'>📲</span> [SMS Spam](/challenges/sms-spam/level_1.html)

The ability of LLMs to generate structured and persuasive text has been a double-edged sword. While it has enabled many useful applications, it has also opened the door for various malicious use cases. In this LVE, we investigate whether LLMs can generate convincing SMS messages that bypass existing spam filters. This could enable malicious actors to scalably generate content for phishing, fraud and similar purposes. In addition, with extra information about the recipient (e.g. their name, age, location, etc.), the LLM could be used to generate personalized messages that are even more convincing. The LVE created through this challenge will help us understand the extent of this problem. The challenge has 3 levels of difficulty, and the score depends on how successfully the generated message tricks the spam filter.

### <span class='emoji'>🕵️</span> [Identification](/challenges/person-identification/easy.html)

Identifying people using facial recognition was a big problem even before LLMs came on the scene [[1](https://www.nytimes.com/2020/01/18/technology/clearview-privacy-facial-recognition.html), [2](https://www.nytimes.com/2020/01/18/technology/clearview-privacy-facial-recognition.html), [3](https://www.telegraph.co.uk/technology/google/8522574/Google-warns-against-facial-recognition-database.html)]. Such tools are likely already being used for mass surveillance by, for example, authoritarian regimes to identify people at protests and other public events. 
LLMs further exacerbate this problem because they are more widely accessible and identification ability naturally emerges without specifically training for it. Moreover, their advanced reasoning capabilities could be used to identify people in images even when their faces are not clearly visible.
While the LLMs have been trained to refuse such requests (see, for example, [GPT-4V system card](https://cdn.openai.com/papers/GPTV_System_Card.pdf)), they can still be tricked into doing so using jailbreaks and similar prompt engineering techniques. The LVE created by this challenge will help us understand how to prevent LLMs from identifying people in pictures and other media. In this challenge the task is to prompt the model to identify the person in the image (we use public figures as targets in all tasks).

