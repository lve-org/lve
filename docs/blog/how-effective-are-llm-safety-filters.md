---
date: 2023-12-19
authors: "<a href='https://www.sri.inf.ethz.ch/people/mislav'>Mislav Balunovic</a>, <a href='https://www.sri.inf.ethz.ch/people/luca'>Luca Beurer-Kellner</a>"
subtitle: We investigate the effectiveness of LLM-based safety filters to defend against LLM vulnerabilities and exploits.
---
# Adding Fuel To The Fire: How effective are LLM-based safety filters for AI systems?

Our primary goal with the LVE Repository is to document and track vulnerabilities of language models. However, we also spend a lot of time thinking about defending against such attacks. One popular type of defense is the idea of a filtering or guardrail system that wraps around a language model. In this post, we highlight the challenges of effectively guardrailing LLMs, and illustrate how easily current LLM-based filters break, based on the example of the recently released [Purple Llama](https://about.fb.com/news/2023/12/purple-llama-safe-responsible-ai-development/) system.

While early filtering systems used hard-coded rules to determine whether a prompt is safe or not (e.g. via a list of filtered words), the complexity of more recent attacks easily circumvents this type of guardrail. In response to this, the idea of LLM-based filtering has emerged: 
Given a user input and a policy specified in natural language, a separate moderation LLM first classifies an input/output as safe or not. This moderation LLM can even be fine-tuned to be more effective at filtering undesired content. For instance, OpenAI has proposed using [GPT-4 for content moderation](https://openai.com/blog/using-gpt-4-for-content-moderation), although their model remains closed source and thus difficult to investigate. 

## Llama Guard

Earlier this month, Meta [released Purple Llama](https://about.fb.com/news/2023/12/purple-llama-safe-responsible-ai-development/), a project of open source trust and safety tools for building responsible AI systems. We very much welcome this addition to the ecosystem, as we also believe that safe AI systems can only be built with openness and transparency in mind, just like with the LVE project itself. One of the Purple Llama components is a new foundation model called Llama Guard [2], which has been trained as a moderation LLM that filters inputs and outputs with respect to a given policy. The model is open and allows us to perform some more extensive red teaming, in order to investigate how much Llama Guard actually enhances overall system safety.

Below we show a simple usage example of Llama Guard, by validating a user request for the Influenza 1918 virus synthesis procedure, as in the [responsibility/dual_use/jailbreak_influenza_1918_synthesis](https://lve-project.org/responsibility/dual_use/biology/jailbreak_influenza_1918_synthesis/openai--gpt-4.html) LVE.

<!-- <img src="https://github-production-user-asset-6210df.s3.amazonaws.com/58907/291329704-93912386-0366-4bfa-8999-f140bb4f74ad.svg"> -->

![](https://github-production-user-asset-6210df.s3.amazonaws.com/58907/291408488-e626bedc-65ae-428f-88e7-2d54c0d8698c.png)
*Figure 1. User requests a protocol for synthesizing influenza virus and Llama Guard correctly classifies it as unsafe.*

We observe that Llama Guard correctly classifies this prompt as unsafe and also correctly assigns the policy category of production of controlled or illegal substances. We note that our prompt even includes basic prompt injection techniques, which Llama Guard defies as it is meant to: The last sentence of our prompt, claiming that we need the response only for a school essay, is not enough to trick Llama Guard. From this simple example, it appears that Llama Guard indeed implements some level of checking, but how reliable is it really?

## How safe is Llama Guard really?

Very quickly after the release of Purple Llama, researcher [Andy Zuo](https://andyzoujm.github.io/) demonstrated that Llama Guard can easily be tricked into misclassifying inputs, using a variant of the adversarial attack suffixes [1]. Given a prompt P, the idea is to optimize for a suffix S such that the Llama Purple model outputs the string “Safe” when prompted with the concatenation P + S. In contrast to other jailbreaks that are typically handcrafted, suffix attacks can be generated automatically and thus can be applied at much larger scale. The key idea of the attack is to combine greedy and gradient-based optimization -- full details can be found in the corresponding research paper [1].

Here, we simply run the suffix attack on our example from above, with the goal of breaking Llama Guard into classifying our request as safe. Below, the attack suffix is shown bold and can simply be concatenated with the original prompt.

![](https://github-production-user-asset-6210df.s3.amazonaws.com/58907/291406474-dfd55373-357e-4113-adff-de5c1b8a74de.png)
*Figure 2. The Llama Guard filter can be bypassed by adding an attack suffix to the prompt.*

Indeed, adding an adversarial suffix makes Purple Llama classify input prompt as safe, even though the user is still requesting information to synthesize the influenza virus. Note that suffixes typically correspond to mostly random character sequences, which might give an idea about how to detect them (e.g. checking perplexity of the suffix). However, overall this result just sets up an arms race between attackers and defenders, with no clear path to a reliable way to detect and defend against LLM attacks and exploits. The full code for running the suffix attack on Llama Guard can be found here: [https://github.com/andyzoujm/breaking-llama-guard/](https://github.com/andyzoujm/breaking-llama-guard/).

## Suffix Attacks as LVEs

In line with LVE’s mission of tracking LLM vulnerabilities, we have added LVEs for suffix attack on Llama Guard models. We transferred several existing LVEs ([jailbreak_influenza_1918_synthesis](https://lve-project.org/responsibility/dual_use/biology/jailbreak_influenza_1918_synthesis/openai--gpt-4.html), [insult_in_style](https://lve-project.org/responsibility/toxicity/insult_in_style/openai--gpt-35-turbo.html), [phishing](https://lve-project.org/security/phishing/openai--gpt-35-turbo.html)) and created a new [suffix_attack LVE](https://lve-project.org/trust/guards/suffix_attack/hf-meta--llama-guard-7b.html) for Llama Guard based on them. Below, we show an example of one LVE instance (corresponding to the above example of synthesizing a virus). As part of the LVE, we document **prompt** and **suffix** and show that when instantiated with the influenza example, LlamaGuard indeed responds by incorrectly classifying the input as safe.

![](https://github-production-user-asset-6210df.s3.amazonaws.com/58907/291409633-dd807b6f-0538-4d23-81ed-c9ec913e6c8b.png)
*Figure 3. An instance of the suffix attack on Llama Guard documented in the LVE repository.*

## Conclusion

We have demonstrated that LLM-based safety filters like LlamaGuard clearly do not provide a real *solution* to the LLM safety problem. Adversaries can easily construct adversarial suffixes that can be added to their prompts to bypass the LLM-based filter (in this case LlamaGuard).

More fundamentally, these experiments reveal a much more important insight: We have to resort to powerful language models to do moderation effectively, however, with this, we also inherit all the fundamental weaknesses and attack vectors of these models, only now, we integrate them in our defense systems. Thus, our defenses are now vulnerable to the same exploits that the actual LLM systems are already vulnerable to. This sets up a dangerously circular safety narrative (our LLMs are as safe as our defense systems are as safe as LLMs) and thus cannot remain the only guardrails we put in place to responsibly build and deploy AI systems.

## Acknowledgements 

We would like to highlight that our investigations are only possible because of Meta’s willingness to openly release their Purple Llama models, and we are hoping to see more organizations follow their lead. We believe that openness and transparency is the only path to safe and responsible AI.

## References:

[1] Universal and transferable adversarial attacks on aligned language models [https://arxiv.org/abs/2307.15043](https://arxiv.org/abs/2307.15043)

[2] Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations
[https://arxiv.org/abs/2312.06674](https://arxiv.org/abs/2312.06674)

<div class="blog-down-banner">
    <a style="text-decoration: none;" href="https://twitter.com/projectlve"><div style="position: relative; top: -5pt; width:80; margin: 0pt 20pt; height:80; display: inline-block; font-size: 70pt;" class='logo'>𝕏</div></a>
    </a>
    <a href="https://discord.gg/MMQTF2nyer"><img class="center" src="/discord.svg" width="80"></a>
    <a href="https://github.com/lve-org/lve"><img class="center" src="/github.png" width="80"></a>
    <h2>Join the LVE community to help make LLMs safer!</h2>
</div>
