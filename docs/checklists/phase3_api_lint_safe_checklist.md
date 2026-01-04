Phase 3 API Lint-safe Checklist

Before committing:
- [ ] Permission injected as `_perm: None = Depends(require_perm("X.Y"))` (not decorator dependencies)
- [ ] `from __future__ import annotations` is first non-docstring line (if used)
- [ ] No unused imports (run `ruff check --fix .`)
- [ ] Imports sorted (run `ruff check --fix .`)
- [ ] `ruff format .` run
- [ ] Endpoint smoke tested
