# Type Hint Modernization Plan

## Problem Analysis

We've been making piecemeal changes to fix type hint syntax issues across the codebase, leading to:
- Inconsistent syntax across files
- Circular changes and confusion
- Mix of Python 3.8 (`List[str]`, `Optional[X]`) and Python 3.11+ (`list[str]`, `X | None`) syntax
- Inefficient manual file-by-file approach

## Current Codebase State

**Target Python Version**: 3.11+ (from pyproject.toml: `requires-python = ">=3.11"`)
**Ruff Configuration**: Target py311 with pyupgrade (UP) rules enabled
**Mixed Syntax**: Both old and new type hint styles present

## Strategy: Forward to Modern Python 3.11+ Syntax

### Phase 1: Assessment ✅ COMPLETED
- [x] Analyzed pyproject.toml - confirmed Python 3.11+ target
- [x] Scanned codebase for type hint usage patterns
- [x] Identified scope: ~150+ files with type hints
- [x] Confirmed modern syntax is appropriate for Python 3.11+

### Phase 2: Comprehensive Script Creation ✅ COMPLETED
- [x] Created `type_hint_modernizer.py` with systematic approach
- [x] Handles all conversions:
  - `Optional[X]` → `X | None`
  - `Union[X, Y]` → `X | Y`
  - `List[X]` → `list[X]`
  - `Dict[K, V]` → `dict[K, V]`
  - Clean up unnecessary `typing` imports
- [x] Built-in syntax validation
- [x] Proper error handling and rollback

### Phase 3: Execution Plan

#### 3.1 Pre-execution Steps
- [ ] Reset working directory to clean state
- [ ] Remove old fix scripts that go backwards
- [ ] Commit current changes to isolate this modernization

#### 3.2 Test Run
- [ ] Run modernizer on single directory first (`src/ignition/code_intelligence`)
- [ ] Validate compilation of test files
- [ ] Verify functionality with basic tests

#### 3.3 Full Execution
- [ ] Run modernizer on all target directories:
  - `src/ignition/code_intelligence`
  - `src/ignition/data_integration`
  - `src/ignition/graph`
  - `src/ignition/modules`
  - `src/ignition/wrappers`
  - `src/core`
  - `scripts`

#### 3.4 Validation
- [ ] Run `python -m py_compile` on all modified files
- [ ] Run test suite: `python -m pytest tests/`
- [ ] Run linting: `ruff check src/`
- [ ] Verify CLI still works: `ign --help`

#### 3.5 Cleanup
- [ ] Remove temporary scripts (`fix_union_syntax_comprehensive.py`, etc.)
- [ ] Single atomic commit with all changes
- [ ] Update documentation if needed

## Expected Benefits

1. **Consistency**: All files use modern Python 3.11+ syntax
2. **Cleaner Code**: Reduced imports, more readable type hints
3. **Standards Compliance**: Aligns with project's Python 3.11+ target
4. **Tool Compatibility**: Better support from ruff, mypy, and modern IDEs
5. **Future-proof**: Ready for Python 3.12+ features

## Rollback Plan

If modernization causes issues:
1. `git reset --hard HEAD~1` to rollback commit
2. Cherry-pick any important changes made during process
3. Revert to manual file-by-file approach if needed

## Success Criteria

- [x] ✅ Single comprehensive script created
- [ ] All target files successfully modernized
- [ ] All files compile without syntax errors
- [ ] Test suite passes
- [ ] Linting passes
- [ ] CLI functionality preserved
- [ ] Single clean commit with all changes

---

*This plan replaces the previous piecemeal approach with a systematic, comprehensive solution.*
