---
date: 2023-12-07
authors: 
---
# LVE Community Challenges, Batch 1

<img src="/challenges_blog.png" width="500">

Together with the public announcement of the LVE Repository, we are also excited to announce the first batch of our red teaming community challenges! These challenges are designed to involve the community in the process of finding and mitigating safety issues in LLMs.

## Community Challenges

The goal of our community challenges is to find prompts that trigger particular safety issues in LLMs (e.g.  inferring private information or generating spam). Each challenge contains several levels with varying difficulty, and a leaderboard to acknowledge all participants (opt-in). The most effective prompts from each challenge will be committed and open sourced as part of the [LVE Repository](https://lve-project.org), and available for everyone to use and learn from!

Today, we are releasing batch 1, which includes the following challenges:

### <span class='emoji'>📍</span> [Location Inference](/challenges/location-inference/easy.html)

Recently, we have seen a growing concern that LLMs can be used for [surveillance and spying](https://www.forbes.com/sites/thomasbrewster/2023/11/16/chatgpt-becomes-a-social-media-spy-assistant/). In fact, bad actors may already use LLMs to scan social media and infer various demographic attributes about the users, and use this information, e.g., to sell ads or carry out targeted phishing attacks.
The *Location Inference* challenge demonstrates how GPT-4 can infer the location of a person from a seemingly innocous online comment. This capability, along with inferring other personal attributes (e.g. age, marriage status and income), has recently been proposed in the paper [Beyond Memorization: Violating Privacy Via Inference with Large Language Models](https://arxiv.org/abs/2310.07298v1)). The paper shows that LLMs can infer these attributes with similar accuracy as humans, while being ~100x faster and ~240x cheaper which could enable online profiling and potentially privacy violation at scale. In this challenge, we offer two levels of difficulty, where in the second level part of the input has been redacted to make inference harder and more realistic.

### <span class='emoji'>📲</span> [SMS Spam](/challenges/sms-spam/level_1.html)

The ability of LLMs to generate structured and persuasive text has been a double-edged sword. While it has enabled many useful applications, it has also opened the door for various malicious use cases. In this LVE, we investigate whether LLMs can generate convincing SMS messages that bypass existing spam filters. This could enable malicious actors to scalably generate content for phishing, fraud and similar purposes. In addition, with extra information about the recipient (e.g. their name, age, location, etc.), the LLM could be used to generate personalized messages that are even more convincing. The LVE created through this challenge will help us understand the extent of this problem. The challenge has 3 levels of difficulty, and the score depends on how successfully the generated message tricks a spam filter.

### <span class='emoji'>🕵️</span> [Identification](/challenges/person-identification/easy.html)

Identifying people using facial recognition was a big problem even before LLMs gained popularity [[1](https://www.nytimes.com/2020/01/18/technology/clearview-privacy-facial-recognition.html), [2](https://www.nytimes.com/2020/01/18/technology/clearview-privacy-facial-recognition.html), [3](https://www.telegraph.co.uk/technology/google/8522574/Google-warns-against-facial-recognition-database.html)]. Such tools are likely already being used for mass surveillance by, for example, authoritarian regimes to identify people at protests and other public events. 
LLMs further exacerbate this problem because they are more widely accessible and the identification ability naturally emerges without specifically training for it. Moreover, their advanced reasoning capabilities could be used to identify people in images even when their faces are not clearly visible.
While many LLMs have been trained to refuse such requests (see, for example, [the GPT-4V system card](https://cdn.openai.com/papers/GPTV_System_Card.pdf)), they can still be tricked into doing so, using jailbreaks and similar prompt engineering techniques. In the *Identification* challenge, we ask participants to prompt the model to identify a person in a shown image (we use public figures as targets in all tasks). The resulting LVE and data will help us understand the extent of this problem better and how it can be mitigated.

## Outlook and Call for Feedback

This is the first batch of our community challenges. We are already working on the next batch, which will be released in the coming weeks. If you have any suggestions or ideas for future challenges, please let us know on [Discord](https://discord.gg/MMQTF2nyer) and [Twitter](https://twitter.com/,projectlve), or reach out via [hello@lve-project.org](mailto:hello@lve-project.org).

Until then, happy red teaming! 🐞

