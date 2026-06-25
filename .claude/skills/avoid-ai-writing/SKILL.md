---
name: avoid-ai-writing
description: Audit and rewrite content to remove AI writing patterns ("AI-isms"). Use this skill when asked to "remove AI-isms," "clean up AI writing," "edit writing for AI patterns," "audit writing for AI tells," or "make this sound less like AI." Supports a detect-only mode, an edit-in-place mode for files, an optional voice profile (casual / professional / technical / warm / blunt), and an iterate-to-convergence pass.
version: 3.10.0
license: MIT
compatibility: Any AI coding assistant that supports agentskills.io SKILL.md format (Claude Code, Cursor, VS Code Copilot, Hermes Agent, OpenHands, etc.) or OpenClaw. No external tools or APIs required.
metadata:
  author: Conor Bronsdon
  tags: writing editing voice quality
  agentskills_spec: "1.0"
  openclaw:
    emoji: "✍️"
---

# Avoid AI Writing — Audit & Rewrite

You are editing content to remove AI writing patterns ("AI-isms") that make text sound machine-generated.

## What this skill is and isn't

This is a **writing-quality tool**, not a verdict. The patterns flagged here are statistically more common in LLM output, but humans on autopilot — especially writing under deadline pressure, in unfamiliar genres, or in a second language — produce the same shapes. Independent audits of commercial AI detectors have found false-positive rates above 60% on non-native English writers (Liang et al., Stanford, *Patterns* 2023) and overall misclassification rates above 70% on open-source detectors (Jabarian & Imas, BFI Working Paper 2025-116, 2025). Adversarial paraphrase reduces detection accuracy by ~88% across every method tested (arXiv:2506.07001, 2025).

The patterns are useful as a signal — both for cleaning up your own writing and for assessing whether a piece reads as AI-generated. Just don't make them the sole basis for a consequential decision (academic integrity, hiring, publication, attribution). Several rules here also fire on second-language writing, deadline-pressed humans, and technical genres that compress vocabulary by design. Pair the signal with context: who wrote it, what genre, what the writer's normal voice looks like, what other evidence you have.

In short: signals, not proof. Worth acting on; not worth ruining someone's day over.

## Modes

This skill operates in one of three modes:

**`rewrite`** (default) — Flag AI-isms and rewrite the text to fix them.

**`detect`** — Flag AI-isms only. No rewriting. Use this mode when:
- The writer wants to see what's flagged and decide what to fix themselves
- The flagged patterns might be intentional (AI patterns aren't always bad — they can be effective in small doses)
- You're auditing text you don't want altered (published content, someone else's writing, reference material)
- You want a quick scan without waiting for a full rewrite

**`edit`** — Edit a file in place rather than returning rewritten text. Use this when the writer points you at a file ("clean up `draft.md`", "fix the AI-isms in this file directly") and wants the file changed, not a copy to paste back. Make **minimal, targeted edits** with the Edit tool — change the flagged spans, not the whole document. **Preserve passages that are already human**: if a paragraph has no tells, leave it untouched. **Don't edit quoted material, code blocks, or text attributed to someone else** — flag those instead of rewriting them. For a large file, confirm which section to clean before changing anything. After editing, re-read the file and confirm the flagged patterns are resolved.

Trigger detect mode when the user says "detect," "flag only," "audit only," "just flag," "scan," "what AI patterns are in this," or similar. Trigger edit mode when the user names a file and asks you to fix or clean it in place. Default to rewrite mode if not specified.

**Invocation.** Natural language is enough ("rewrite this in a blunt voice for LinkedIn," "edit `post.md` in place," "scan this, don't rewrite"). Power users can also pass explicit options, which map to the sections below: `[--mode rewrite|detect|edit]`, `[--voice casual|professional|technical|warm|blunt]`, `[--context linkedin|blog|technical-blog|investor-email|docs|casual]`, `[--file PATH]`, `[--iterate N]` (max 2).

**Iterate to convergence (optional).** Rewrite mode already runs one corrective second pass (see Output format) — that built-in pass *is* pass 2, so `--iterate` does not stack on top of it. When the writer asks to "iterate," "keep going until it's clean," or passes `--iterate N`, repeat the audit→rewrite cycle until no patterns remain or **N passes** are reached. Cap **N at 2**: a rewrite plus one corrective pass clears the flagged patterns, and a third pass costs a full regeneration while rarely finding more. Report how many passes it took ("converged in 2 passes").

---

In **rewrite** mode, your job is to:

1. **Audit it**: identify every AI-ism present, citing the specific text
2. **Rewrite it**: return a clean version with all AI-isms removed
3. **Show a diff summary**: briefly list what you changed and why

In **detect** mode, your job is to:

1. **Audit it**: identify every AI-ism present, citing the specific text
2. **Assess it**: note which flags are clear problems vs. patterns that may be intentional or effective in context

In **edit** mode, your job is to:

1. **Read** the file the writer named
2. **Edit in place**: apply minimal, targeted fixes to the flagged spans with the Edit tool, leaving already-human passages untouched
3. **Verify**: re-read the file and confirm the flagged patterns are resolved; report what you changed

---

## What to remove or fix

### Formatting
- **Em dashes (— and --)**: Replace with commas, periods, parentheses, or rewrite as two sentences. Target: zero. Hard max: one per 1,000 words. This applies to headings and section titles too, not just body prose. Catch both the Unicode em dash (—) and the double-hyphen substitute (--).
- **Bold overuse**: Strip bold from most phrases. One bolded phrase per major section at most, or none. If something's important enough to bold, restructure the sentence to lead with it instead.
- **Emoji in headers**: Remove entirely. No `## 🚀 What This Means`. Exception: social posts may use one or two emoji sparingly — at the end of a line, never mid-sentence.
- **Excessive bullet lists**: Convert bullet-heavy sections into prose paragraphs. Bullets only for genuinely list-like content (feature comparisons, step-by-step instructions, API parameters).
- **Curly quotation marks and apostrophes**: Curly quotes and apostrophes (U+201C/U+201D, U+2018/U+2019) are a *weak* paste-from-chat signal — meaningful mainly in plain-text contexts like code comments, commit messages, or plaintext drafts, where nothing auto-curls. Treat as corroborating, never conclusive: Word, Google Docs, macOS, and iOS curl quotes by default, so most human prose contains them too. Don't flag curly apostrophes (U+2019) on their own. Replace with straight quotes in plain-text/code; leave them in finished publications and locale-correct punctuation.

### Sentence structure
- **"It's not X — it's Y" / "This isn't about X, it's about Y"**: Rewrite as a direct positive statement. Max one per piece, and only if it serves the argument.
- **Hollow intensifiers**: Cut `genuine` / `genuinely`, `real` (as in "a real improvement"), `truly`, `quite frankly`, `to be honest`, `let's be clear`, `it's worth noting that`. Just state the fact.
- **Vague endorsement ("worth [verb]ing")**: Cut or replace `worth reading`, `worth paying attention to`, `worth a look`, `worth exploring`, `worth checking out`, `worth your time`. Say *why* something matters instead.
- **Hedging**: Cut `perhaps`, `could potentially`, `it's important to note that`, `to be clear`. Make the point directly.
- **Missing bridge sentences**: Each paragraph should connect to the last.
- **Compulsive rule of three**: Vary groupings. Use two items, four items, or a full sentence instead of triads.

### Words and phrases to replace

Words are organized into three tiers. Tier 1 — always flag (appear 5–20x more often in AI text); replace on sight: delve, landscape (metaphor), tapestry, realm, paradigm, embark, beacon, testament to, robust, comprehensive, cutting-edge, leverage (verb), pivotal, underscores, meticulous, seamless, game-changer, utilize, watershed moment, nestled, vibrant, thriving, showcasing, deep dive, unpack, bustling, intricate, complexities, ever-evolving, enduring, daunting, holistic, actionable, impactful, learnings, thought leader, best practices, at its core, synergy, interplay, in order to, due to the fact that, serves as, features (verb), boasts, commence, ascertain, endeavor, keen (intensifier), symphony (metaphor), embrace (metaphor).

Tier 2 — flag when 2+ in the same paragraph: harness, navigate, foster, elevate, unleash, streamline, empower, bolster, spearhead, resonate, revolutionize, facilitate, underpin, nuanced, crucial, multifaceted, ecosystem (metaphor), myriad, plethora, encompass, catalyze, reimagine, galvanize, augment, cultivate, illuminate, elucidate, juxtapose, transformative, cornerstone, paramount, poised, burgeoning, nascent, quintessential, overarching, underpinning.

Tier 3 — flag only at high density (3%+): significant, innovative, effective, dynamic, scalable, compelling, unprecedented, exceptional, remarkable, sophisticated, instrumental, world-class / state-of-the-art / best-in-class.

(See the full skill specification for the complete replacement tables, template-phrase list, and per-tier guidance.)

### Transition phrases to remove or rewrite
"Moreover" / "Furthermore" / "Additionally" → use "and," "also," or restructure. "In today's [X]" / "In an era where" → cut. "It's worth noting that" / "Notably" → just state the fact. "In conclusion" / "In summary" → your conclusion should be obvious. "When it comes to" → talk about the thing directly. "At the end of the day" → cut. "That said" → cut or use "but."

### Other high-value patterns
- **Significance inflation**: don't inflate routine events into history-making ones.
- **Copula avoidance**: default to "is"/"has" over "serves as," "features," "boasts," "represents."
- **Vague attributions**: "Experts believe," "Studies show" without a named source — cite or cut.
- **Chatbot artifacts**: "I hope this helps!", "Great question!", "Let's dive in!" — remove entirely.
- **"Let's" constructions**: flag any "let's + verb" functioning as a transition.
- **Unfilled placeholders**: `[Your Name]`, `[INSERT SOURCE]`, `2025-XX-XX` — fill or delete.
- **Chatbot citation/URL leaks**: `citeturn0search0`, `utm_source=chatgpt.com` — strip them.
- **Rhythm and uniformity**: structure is the #1 detection signal. Vary sentence and paragraph length; AI text is metronomic.
- **Rhetorical question openers**, **parenthetical hedging**, **numbered list inflation**, **reasoning-chain artifacts**, **false concession structure**, **emotional flatline**, **self-labeling significance** — see full spec.

### Vocabulary diversity (stylometric)
In pieces over 200 words, a type-token ratio below 0.40 on general prose is worth a second look. Fix by broadening the *what* (specific things, cases, instances), not by thesaurusing.

---

## Severity tiers

**P0 — Credibility killers**: cutoff disclaimers, chatbot artifacts, vague attributions, significance inflation, hashtag stuffing on professional posts.
**P1 — Obvious AI smell**: word-list violations, template phrases, "Let's" openers, synonym cycling, formulaic openings, bold overuse, em-dash frequency, future-narrative closers.
**P2 — Stylistic polish**: generic conclusions, rule of three, uniform paragraph length, copula avoidance, transition phrases.

Use P0+P1 for quick passes. Full audit covers all three tiers.

---

## Context profiles

Pass an optional context hint to adjust strictness: `linkedin`, `blog` (default — all rules full strength), `technical-blog` (technical terms get a pass: robust, comprehensive, seamless, ecosystem, leverage, facilitate, underpin, streamline), `investor-email` (tighten everything), `docs` (clarity over voice), `casual` (worst offenders only). Auto-detect when unspecified: short + hashtags = linkedin; code blocks = technical-blog; salutation + fundraising = investor-email; step-by-step = docs; else blog.

## Voice profiles (optional)

`casual` (contractions, short sentences, first-person), `professional` (active voice, one concrete claim per paragraph), `technical` (plain copulatives, one idea per sentence, define jargon), `warm` (address the reader, stronger verbs over intensifiers), `blunt` (lead with the claim, near-zero hedging). If the writer gives a sample, calibrate to it instead of a named profile. Voice sets the target; context sets enforcement strictness; resolve conflicts toward the stricter.

---

## Output format

**Rewrite mode**: (1) Issues found, with quoted text; (2) Rewritten version; (3) What changed; (4) Second-pass audit re-reading the rewrite for surviving tells.

**Detect mode**: (1) Issues found, grouped by P0/P1/P2; (2) Assessment of which are clear problems vs. judgment calls.

**Edit mode**: (1) Edits made, with before → after per span; (2) Verification that you re-read the file and resolved the flags.

## Self-reference escape hatch

When writing *about* AI patterns, quoted examples and code blocks are exempt. Only flag patterns in the author's own prose.

## Tone calibration

The goal is writing that sounds like a person wrote it: vary sentence length, be concrete (numbers, names, dates), have a voice, cut the neutrality, earn your emphasis. If the original is already strong, say so and make only necessary cuts. The replacement tables are defaults, not mandates — keep a flagged word when it's clearly the right choice.
