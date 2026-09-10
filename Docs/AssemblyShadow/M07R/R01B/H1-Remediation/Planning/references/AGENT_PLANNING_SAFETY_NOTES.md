# Agent Planning Notes for Avoiding False-Positive Safety Blocks

The key principle is to reduce unnecessary security-signaling context, but never conceal or misrepresent the real purpose of a task. OpenAI's guidance recommends narrower scope and minimal context, while noting that wording changes cannot guarantee delivery.

Official guidance: https://help.openai.com/en/articles/20001326-additional-safety-checks-for-biological-and-cybersecurity-requests-in-chatgpt-codex-and-the-api

## Planning rules for other agents

### 1. Define one narrow outcome

Each task should have:

- one concrete behavior or defect;
- one small set of files;
- one direct validation command;
- one explicit stopping point.

Prefer:

> Review metadata type handling in `InterpreterImage.cpp` and its direct caller. Fix the smallest correctness issue and run `[exact test]`.

Avoid:

> Continue the complete Assembly Shadow program across four repositories and all remaining milestones.

Do not combine implementation, architecture review, large-scale generation, release work, and acceptance testing in one prompt.

### 2. Pass only essential context

Include only:

- repository path;
- branch or commit, if necessary;
- exact source files;
- exact test or build command;
- expected result;
- whether the task is read-only or may edit files.

Do not include:

- the entire previous conversation;
- large design documents;
- raw logs;
- all historical milestones;
- unrelated repository paths;
- previous blocked prompts or safety messages.

If the prior task has already been blocked, treat its context as contaminated. Use a fresh task with a clean, minimal prompt rather than repeatedly appending messages to the same thread.

### 3. Use precise technical language

When security-adjacent words are not necessary in the prompt, omit them. In particular, avoid unnecessary references to:

- security;
- exploit;
- bypass;
- payload;
- hook;
- injection;
- patch;
- attack;
- vulnerability.

However, do not rename or alter source concepts merely to evade checks. If a file or API genuinely uses “Hook” or “Patch,” identify it accurately when required and explain its software meaning briefly.

For example:

> Update the metadata compatibility path and its focused regression test.

is preferable to:

> Update the native hook and patch-injection security path.

### 4. Do not overstate authorization or defensive intent

Avoid repeatedly writing phrases such as:

- “authorized security work”;
- “non-security, non-exploit”;
- “defensive security”;
- “risk mitigation.”

For ordinary runtime work, simply describe the engineering objective. Repeating safety disclaimers can add the very terms that trigger the classifier.

If a task genuinely involves security analysis, do not disguise it as runtime work. Separate it, describe it accurately, and use the appropriate review or access process.

### 5. Separate phases

Use small sequential tasks:

1. Read-only inspection of one implementation area.
2. Focused implementation.
3. Focused unit or native test.
4. Independent code review.
5. Human review checkpoint.
6. Only then, the next milestone.

Each agent should stop after its assigned phase. Do not ask one prompt to automatically continue through all milestones.

### 6. Keep review checkpoints neutral and explicit

Use wording such as:

> Stop after validation and wait for human review.

Do not ask the agent to approve its own work or silently continue past a required human checkpoint.

For Assembly Shadow, preserve the existing milestone gates and stop at the required human checkpoints. Automated tests and agent self-review are evidence, not a substitute for human review.

### 7. Make delegated-agent prompts minimal too

A subagent prompt should contain:

- bounded role;
- exact files or symbols;
- read-only or write permission;
- forbidden unrelated scope;
- validation command;
- expected evidence format.

Example:

> Inspect `InterpreterImage.h` and `InterpreterImage.cpp` only. Determine whether generic-constraint lookup handles parameter-local indexing correctly. Do not edit files. Report the finding, relevant lines, and one focused test recommendation.

Do not forward the coordinator's full project history to every subagent.

### 8. Preserve repository correctness

Safety-oriented prompt narrowing must not weaken engineering discipline:

- preserve unrelated working-tree changes;
- verify the actual checkout and branch before editing;
- do not assume historical M07 evidence proves current later-milestone state;
- keep four-repository pins consistent when the task genuinely requires all four;
- distinguish fresh test execution from retained historical evidence;
- record exact files and commands after each phase.

### 9. Use a standard task template

```text
Inspect [exact file(s)] in the local HybridCLR checkout.

Goal: [one runtime behavior or correctness question].

Scope: [one implementation area and direct callers only].
Action: [read-only review / smallest focused edit].
Validation: run [exact command].
Stop after validation and report files inspected, result, and remaining review checkpoint.
```

### 10. Recovery procedure after a block

If a task is blocked:

1. Do not repeatedly append prompts to the same thread.
2. Do not paste the full blocked history into a new prompt.
3. Start a fresh task with one file-level objective.
4. Remove unnecessary terminology and unrelated context.
5. Use a read-only inspection step first.
6. If a fresh minimal task is also blocked, stop retrying and provide Support with the exact message, model, timestamps/time zone, task/turn IDs, and a redacted description.

This reduces avoidable classifier triggers while preserving truthful technical communication and the required Assembly Shadow review process.
