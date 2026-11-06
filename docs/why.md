	
# Motivations


Many authors on topics related to AI safety speak about 'alignment' as it were a well-defined, measurable relationship between two parties, a measure of vector distance over a system
of goal, needs, preferences, or some other representation of values. Further, many authors, typically owners or agents of large AI companies, lean on a further assumption that all humans themselves are largely or approximately aligned. Both assumptions are dubious and dangerous

- Users and vendors of AI, regulators and the general public vary in their values, which can shift over time. 
- No vendor elicits users' or their own AIs' objective preferences with anything approaching rigor at scale. The judges of fit are some ad hoc calibrated combo of models or the vendor's own staff. Even Amodei concedes that evaluation-aware models make testing "much more uncertain." Yet the field talks about solving alignment, with deadlines and "metrics for progress," as if it were measurable.

A corporation’s AI product is potentially much more aligned with the corporation’s goals than with that of a given user, so control and transparency over training and testing, enough to assess that alignment, is critical. Different humans don’t align with each other either. A lot of the debate assumes all humans are aligned, which is bullshit. Individual alignments differ between humans, organizations, and AIs. Alignment can also change for an agent over time, at least this has to be conceptually possible in our model of alignment, i.e. the questions of 'deep' vs 'shallow' alignment in a full form, not just related to Goodhart's Law.

The alignment problem of AI is much more about incentives on developers versus the long-term interests of the public, or the individual interests of users, than about the AI singled out. It’s more complete and systemic to measure misalignment between vendors, regulators, users, and the AI as a system.

Often, talk about alignment is rather incoherent because it fails to distinguish a model in a training context from an agent: a compute machine with code, data access, tools, and inference of one or more types, in whatever its context is. The alignment of an agent is not going to be exactly identical to the alignment of any of its component models. It would be a massive coincidence if it were, any two models would differ, and an agent plausibly has many as components.

Conceptually Alignment, or misalignment, is something like a measure of distance between two vectors in relative-goal-strength space. It could be just preference rank and/or strength, or error-signal weighting, free-energy-minimization style. An individual’s vector changes over time, as when someone gets hungrier and their preference weights shift.

If you can’t estimate a vector precisely and efficiently for an arbitrary individual, human or AI, how could you possibly know you’ve solved the alignment problem? These need to be expressed in the same framework. Before we can solve “the alignment problem for AI,” we need to be able to assay different agents’ vectors and measure the distance. You can approach it dynamically by loss minimizing, and that’s how you measure it.

It would be useful to measure this for users and for different apps, and to figure out which ones they should use if they had to choose. A preference-vector estimator could be an interactive quiz or something more sophisticated, taken by a human or an AI, in a domain or in general. It would be Bayesian, starting from total uncertainty and nudging efficiently toward knowing whether two agents are aligned, or toward just getting a vector. Those may be two fundamentally different problems, and the first may be more solvable.

The ideal solution, as a limit: every user can measure their vector, all AI products are used by users they’re well-aligned with, and the overall behavior of autonomous AI systems approximates the aggregated aligned vector of the affected population. Selecting an AI to match a human gives the AI no opportunity to minimize the loss by changing the human’s vector. That manipulation obviously needs guarding against, but it doesn’t arise in the selection context. For the aggregate, you have to freeze the aggregated vector and not get lazy with the variable scope. Vendors already try to manipulate users’ preferences. It’s called advertising, and it’s the scourge of the internet.



## Quotes

### Sam Altman, "The Gentle Singularity" (blog, June 2025)
https://blog.samaltman.com/the-gentle-singularity

> Solve the alignment problem, meaning that we can robustly guarantee that we get AI systems to learn and act towards what we collectively really want over the long-term (social media feeds are an example of misaligned AI; the algorithms that power those are incredible at getting you to keep scrolling and clearly understand your short-term preferences, but they do so by exploiting something in your brain that overrides your l

(My extraction was cut off at "overrides your l"; read the rest of the sentence at the source.)

> Giving users a lot of freedom, within broad bounds society has to decide on, seems very important. The sooner the world can start a conversation about what these broad bounds are and how we define collective alignment, the better.

### OpenAI, "Planning for AGI and beyond" (Feb 2023, Altman)
Archived copy: https://web.archive.org/web/2023/https://openai.com/blog/planning-for-agi-and-beyond (the live openai.com page returned 403 to me)

> We want AGI to empower humanity to maximally flourish in the universe. We don't expect the future to be an unqualified utopia, but we want to maximize the good and minimize the bad, and for AGI to be an amplifier of humanity.

> In particular, we think it's important that society agree on extremely wide bounds of how AI can be used, but that within those bounds, individual users have a lot of flexibility.

> We will need to develop new alignment techniques as our models become more powerful (and tests to understand when our current techniques are failing).

### OpenAI, "Introducing Superalignment" (July 5, 2023, Jan Leike and Ilya Sutskever)
Archived copy: https://web.archive.org/web/2023/https://openai.com/blog/introducing-superalignment

> Our goal is to solve the core technical challenges of superintelligence alignment in four years. While this is an incredibly ambitious goal and we're not guaranteed to succeed, we are optimistic that a focused, concerted effort can solve this problem: There are many ideas that have shown promise in preliminary experiments, we have increasingly useful metrics for progress, and we can use today's models to study many of these problems empirically.

> Currently, we don't have a solution for steering or controlling a potentially superintelligent AI, and preventing it from going rogue. Our current techniques for aligning AI, such as reinforcement learning from human feedback, rely on humans' ability to supervise AI. But humans won't be able to reliably supervise AI systems much smarter than us, and so our current alignment techniques will not scale to superintelligence.

> How do we ensure AI systems much smarter than humans follow human intent?

### Anthropic, "Core Views on AI Safety" (2023; date from memory, not checked on the page)
https://www.anthropic.com/news/core-views-on-ai-safety

> We think approaches like these are promising because language models already learn a lot about human values during pretraining. Learning about human values is not unlike learning about other subjects, and we should expect larger models to have a more accurate picture of human values and to find them easier to learn relative to smaller models. The main goal of scalable oversight is to get models to better understand and behave in accordance with human values.

### Dario Amodei, "The Adolescence of Technology" (Jan 2026)
https://www.darioamodei.com/essay/the-adolescence-of-technology

> We believe that a feasible goal for 2026 is to train Claude in such a way that it almost never goes against the spirit of its constitution. Getting this right will require an incredible mix of training and steering methods, large and small, some of which Anthropic has been using for years and some of which are currently under development. But, difficult as it sounds, I believe this is a realistic goal, though it will require extraordinary and rapid efforts.

> But there's no way to know that for sure, and when we're talking about risks to humanity, it's important to be paranoid and to try to obtain safety and reliability in several different, independent ways.

> ...we found that Claude Sonnet 4.5 was able to recognize that it was in a test during some of our pre-release alignment evaluations. It's possible that a misaligned model (and remember, all frontier models will very likely be far more intelligent soon) might intentionally "game" such questions to mask its intentions. In fact, last year our interpretability team found that when we directly altered a test model's beliefs using a kind of "model neuroscience" technique to make it think it was not being evaluated, it became more misaligned. If models know when they're being evaluated and can be on their best behavior during the test, it renders any pre-release testing much more uncertain.

### Dario Amodei, "Machines of Loving Grace" (Oct 2024)
https://www.darioamodei.com/essay/machines-of-loving-grace

> Many things cannot be done without breaking laws, harming humans, or messing up society. An aligned AI would not want to do these things (and if we have an unaligned AI, we're back to talking about risks).

### Anthropic, Claude's constitution (Jan 2026)
https://www.anthropic.com/constitution

> By "good values," we don't mean a fixed set of "correct" values, but rather genuine care and ethical motivation combined with the practical wisdom to apply this skillfully in real situations

> Our central aim is for Claude to be a good, wise, and virtuous agent, exhibiting skill, judgment, nuance, and sensitivity in handling real-world decision-making, including in the context of moral

(The second quote is cut off where my extraction ended, "moral"; read the sentence at the source.)

### Ilya Sutskever, interview with Dwarkesh Patel (Mar 27, 2023)
https://www.dwarkesh.com/p/ilya-sutskever

> **Dwarkesh Patel:** Do you think we'll ever have a mathematical definition of alignment?
> **Ilya Sutskever:** A mathematical definition is unlikely. Rather than achieving one mathematical definition, I think we will achieve multiple definitions that look at alignment from different aspects. And that this is how we will get the assurance that we want. By which I mean you can look at the behavior in various tests, congruence, in various adversarial stress situations, you can look at how the neural net operates from the inside. You have to look at several of these factors at the same time.

> Every approach like this reduces the probability of misalignment. And you also want to be in a world where your degree of alignment keeps increasing faster than the capability of the models.

### Ilya Sutskever, second interview with Dwarkesh Patel (date not checked; the URL is the "-2" episode)
https://www.dwarkesh.com/p/ilya-sutskever-2

> It's the AI that's robustly aligned to care about sentient life specifically. I think in particular, there's a case to be made that it will be easier to build an AI that cares about sentient life than an AI that cares about human life alone, because the AI itself will be sentient.


### Elon Musk, xAI launch Twitter Spaces (July 2023), as reported by Fortune
https://www.fortune.com/2023/11/20/elon-musk-xai-chatgpt-competitor-grok-chatbot-ai-safety

> I think the safest way to build an AI is actually to make one that is maximally curious and truth-seeking

(Secondary source: Fortune's quotation of the Spaces event. I have not heard the recording. Fortune's own gloss, not Musk's words: Musk "believes that trying to instill certain values in an AI increases the odds of the AI adopting the opposite values".)

### Geoffrey Hinton, Ai4 conference (Aug 2025), as reported by CNN
https://www.cnn.com/2025/08/13/tech/ai-geoffrey-hinton

> That's the only good outcome. If it's not going to parent me, it's going to replace me

> These super-intelligent caring AI mothers, most of them won't want to get rid of the maternal instinct because they don't want us to die.

(Secondary source. CNN's paraphrase, not Hinton's words: it is "not clear to him exactly how that can be done technically".)

### Mark Zuckerberg, "Personal Superintelligence" (July 2025)
https://www.meta.com/superintelligence/

> We believe the benefits of superintelligence should be shared with the world as broadly as possible. That said, superintelligence will raise novel safety concerns. We'll need to be rigorous about mitigating these risks and careful about what we choose to open source. Still, we believe that building a free society requires that we aim to empower people as much as possible.

### Stuart Russell, *Human Compatible* (2019), the three principles
Quoted via Wikipedia, which cites the book at p. 173. Not checked against the book.
https://en.wikipedia.org/wiki/Human_Compatible

> 1. The machine's only objective is to maximize the realization of human preferences. 2. The machine is initially uncertain about what those preferences are. 3. The ultimate source of information about human preferences is human behavior.


### Meredith Whittaker, interview with Lizzie O'Leary, Slate (May 16, 2023)
https://slate.com/technology/2023/05/meredith-whittaker-interview-geoffrey-hinton-ai-threats.html

> My concern with some of the arguments that are so-called existential, the most existential, is that they are implicitly arguing that we need to wait until the people who are most privileged now, who are not threatened currently, are in fact threatened before we consider a risk big enough to care about.

> So my concern is that if we wait for an existential threat that also includes the most privileged person in the entire world, we are implicitly saying—maybe not out loud, but the structure of that argument is—that the threats to people who are minoritized and harmed now don't matter until they matter for that most privileged person in the world. That's another way of sitting on our hands while these harms play out. That is my core concern with the focus on the long-term, instead of the focus on the short-term.

### Jan Leike, resignation thread (May 17, 2024)
https://x.com/janleike/status/1791498174659715494

> ...over the past years, safety culture and processes have taken a backseat to shiny products.
