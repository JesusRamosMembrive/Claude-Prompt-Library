# test-flow-v3

This file contains project context and instructions for Claude Code.

## Project Overview

*Add project description here*

## Tech Stack

*Add technologies used here*

## Getting Started

*Add setup instructions here*

---

# Custom Workflow Instructions

<!-- Added by claude-prompt-library init_project.py -->

## 🎯 PROJECT CONTEXT

Before ANY work, read in this order:
1. .claude/00-project-brief.md - Project scope and constraints
2. .claude/01-current-phase.md - Current state and progress
3. .claude/02-stage[X]-rules.md - Rules for current stage

## 📝 SESSION WORKFLOW

At START of session:
- Confirm you've read the context files
- Understand current phase and stage
- Ask for clarification if context is unclear

During WORK:
- Follow stage-specific rules strictly
- Propose plans before implementing
- Get approval for architectural decisions

At END of session:
- Update .claude/01-current-phase.md with:
  * What was implemented (with file names)
  * Decisions made and why
  * What was NOT done (deferred)
  * Next steps for next session
- Keep 01-current-phase.md concise and scannable

## ⚠️ CRITICAL RULES

- Never implement without reading current context
- Never skip updating progress at end of session
- Never assume you remember from previous sessions
- Always check current stage rules before proposing solutions

## 🚫 NEVER

- Over-engineer beyond current stage
- Implement features not in project brief
- Skip the "propose then implement" workflow
- Forget to update tracking