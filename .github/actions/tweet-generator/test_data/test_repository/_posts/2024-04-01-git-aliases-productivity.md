---
title: 5 Git Aliases That Will 10x Your Productivity
date: 2024-04-01
categories:
  - git
  - productivity
  - tips
tags:
  - git
  - aliases
  - productivity
  - workflow
summary: Simple Git aliases that will dramatically speed up your development workflow.
publish: True
auto_post: True
canonical_url: https://example.com/git-aliases-productivity
---
# 5 Git Aliases That Will 10x Your Productivity

Stop typing the same long Git commands over and over. These 5 aliases will transform your workflow.

## 1. Super Status
```bash
git config --global alias.s "status -sb"
```
Instead of `git status`, just type `git s` for a clean, branch-aware status.

## 2. Pretty Logs
```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
```
`git lg` gives you a beautiful, visual commit history.

## 3. Quick Commit
```bash
git config --global alias.ac "!git add -A && git commit -m"
```
`git ac "message"` stages everything and commits in one command.

## 4. Undo Last Commit
```bash
git config --global alias.undo "reset HEAD~1 --mixed"
```
`git undo` safely undoes your last commit while keeping changes.

## 5. Branch Cleanup
```bash
git config --global alias.cleanup "!git branch --merged | grep -v '\*\|master\|main' | xargs -n 1 git branch -d"
```
`git cleanup` removes all merged branches automatically.

## Bonus: My Complete .gitconfig

Here's my full alias section:
```bash
[alias]
    s = status -sb
    lg = log --oneline --graph --decorate --all
    ac = !git add -A && git commit -m
    undo = reset HEAD~1 --mixed
    cleanup = !git branch --merged | grep -v '\*\|master\|main' | xargs -n 1 git branch -d
    co = checkout
    br = branch
    ci = commit
    st = status
```

These aliases have saved me hours every week. Set them up once, benefit forever.

What are your favorite Git aliases? Share them below!