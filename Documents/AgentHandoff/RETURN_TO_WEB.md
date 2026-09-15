# Local Validation → Primary Implementation

## Missing authoritative web-to-local handoff

### Symptom

`Documents/AgentHandoff/WEB_TO_LOCAL.md` does not exist in the current candidate checkout or in any fetched branch published by `git@github.com:night-outlook/hybridclr_demo.git`. Local validation therefore cannot confirm the required repository, branch, commit, current objective, validation list, candidate-selection criteria, or known risks.

### Reproduction

From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`:

```sh
git fetch origin '+refs/heads/*:refs/remotes/origin/*'
git for-each-ref --format='%(refname) %(objectname)' refs/remotes/origin
git cat-file -e refs/remotes/origin/codex/assembly-shadow-r01b-h1:Documents/AgentHandoff/WEB_TO_LOCAL.md
```

The final command exits nonzero. Iterating the same `git cat-file -e` check over all seven fetched remote refs produces no match.

### Evidence

- [preflight.json](preflight.json) records the exact local/remote heads and the empty `handoffRefs` result.
- [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) records the rejected dirty `main` checkout, the isolated candidate checkout, environment details, and every blocked validation category.

### Most likely root cause

The primary implementation handoff was not committed and pushed at the required path, or it was published to a different repository that was not identified in the request.

### Impact

Running Unity or Player validation now could test the wrong commit, omit required configurations, or apply the wrong candidate-selection standard. Such results would not be an authoritative local-validation conclusion.

### Recommended direction

Create `Documents/AgentHandoff/WEB_TO_LOCAL.md` in the intended repository and branch, including:

- exact repository URL, branch, and full commit;
- current objective and explicit exclusions;
- required Unity/build/runtime/performance validations;
- candidate implementation choices and selection criteria;
- environment assumptions, known risks, and expected evidence outputs;
- the intended Human Review Gate conditions.

Commit and push that file, then provide the resulting branch and commit. Local validation can resume by fetching and checking out that exact published state.

### Uncertainty

The file may exist in another repository or unpublished local state. Git refs from the identified `hybridclr_demo` origin contain no such handoff, so that possibility cannot be verified locally.
