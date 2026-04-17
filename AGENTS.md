# Repository Guidelines

## Project Structure & Module Organization
This repository is currently documentation-first. The main project artifacts live at the repo root:

- `AI旅行Vlog剪辑系统PRD重构版.md`: primary product requirements document and the most detailed source of truth
- `AI旅行Vlog剪辑系统方案.md`: solution and architecture proposal
- `AI旅行Vlog开源工具调研.md`: tool research and dependency evaluation
- `.claude/`: local assistant workflow notes; change only when updating contributor tooling

Keep new planning, architecture, or research documents in Markdown at the root unless a clear subdirectory is introduced for a new document set.

## Build, Test, and Development Commands
There is no application build or automated test pipeline checked in yet. Use lightweight validation commands before opening a PR:

- `git diff --check` — catches trailing whitespace and malformed patches
- `rg -n "TODO|待确认|TBD" *.md` — finds unresolved placeholders
- `sed -n '1,80p' AI旅行Vlog剪辑系统PRD重构版.md` — spot-check document structure and heading flow

Preview Markdown in your editor before submitting to verify tables, lists, and heading hierarchy.

## Coding Style & Naming Conventions
Use concise, professional Markdown. Prefer:

- ATX headings (`#`, `##`, `###`) with a clear hierarchy
- short paragraphs and scannable bullet lists
- backticks for module names, interfaces, commands, and file names
- consistent terminology across documents; reuse established names such as `Project Manager`, `Media Analyzer`, and `EditPlan`

Preserve the repository’s existing naming pattern: descriptive Chinese document titles for product docs, with English identifiers only for technical concepts.

## Testing Guidelines
Because this repo is documentation-based, “testing” means review for consistency and completeness:

- verify section numbering and heading depth
- confirm new terms match existing PRD vocabulary
- update cross-document references when changing module names, flows, or V1 scope
- avoid leaving unresolved assumptions without marking them explicitly

## Commit & Pull Request Guidelines
Match the current Git history: concise, imperative summaries in sentence case, for example `Refine fallback strategies in PRD`. Do not use noisy multi-topic commits.

For pull requests:

- explain which document(s) changed and why
- call out any scope, terminology, or architecture decisions
- include before/after screenshots only if formatting changed substantially in Markdown preview
- link related issues, plans, or discussion notes when available

## Agent-Specific Notes
Make minimal, surgical edits. Prefer updating the existing PRD or proposal files over creating overlapping documents. When adding a new document, state its purpose and relationship to the current PRD in the opening section.
