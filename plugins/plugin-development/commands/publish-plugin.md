---
description: Validate, then commit and push pending marketplace changes
---

# Publish

1. Run `/validate-plugin` first (or the underlying script) if it hasn't been run
   this session. Stop and report if errors remain — never publish broken
   state.
2. Show `git status` and `git diff --stat` so the person can see what's
   about to ship, including anything the fix loop changed automatically.
3. Ask for a short summary of the change if not already clear from context
   (used as the commit message, e.g. `helm: add chart naming skill`).
4. `git add -A && git commit -m "<message>"`.
5. `git push`. Report the result plainly — if it fails (auth, conflicts),
   say so rather than retrying blindly.