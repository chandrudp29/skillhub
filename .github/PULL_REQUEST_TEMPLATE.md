## Skill Name

<!-- The exact name from skill.json -->

## Problem This Solves

<!-- Describe the specific situation where you needed this skill and it didn't exist.
     "This could be useful" is not a problem statement.
     "I was building a RAG pipeline and had no systematic way to evaluate faithfulness" is. -->

## What the Skill Does

<!-- The workflow the skill provides. Not a list of the file's contents. -->

## Checklist

- [ ] `skills/<name>/SKILL.md` exists with valid frontmatter (name, description, version, agents, tags)
- [ ] `skills/<name>/skill.json` exists with all required fields
- [ ] Entry added to `registry/index.json` in alphabetical order
- [ ] Skill name is lowercase-hyphen-separated and matches the directory name
- [ ] Description is under 1024 characters and includes "Use when..."
- [ ] Skill is under 500 lines (or uses supporting files for overflow)
- [ ] I searched for existing skills and this doesn't duplicate one: `skillhub search <topic>`
- [ ] This is a single skill (not multiple skills bundled together)

## Authoring

<!-- Required: who wrote this? -->
- [ ] Written by hand (no AI assistance)
- [ ] AI-assisted — model used: __________, I reviewed the complete diff before submitting

## Existing PRs / Issues

<!-- Search open AND closed PRs for this skill or related ones. What did you find?
     If a prior PR was closed, what's different about this one? -->
