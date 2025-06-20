# Phase 9.6 Pre-commit Hook Issues Fix Plan

Following the crawl_mcp.py principles of proper error handling and systematic resolution, here's the plan to fix all pre-commit hook issues:

## 1. Critical Issues to Fix

### A. Missing Method Attributes (scenario_runner.py)
- **Issue**: ValidationContext has no attribute 'validate_module' (line 397)
- **Fix**: The correct method is `async def validate_module(self, module_path: str)` in ModuleValidator, not ValidationContext
- **Action**: Fix the context manager usage pattern

### B. Type Annotation Issues (Multiple Files)
Files with missing return type annotations:
- `code_analyzer.py`: 11 functions missing return types
- `knowledge_validator.py`: 2 functions + unreachable statements
- `ai_assistant_module.py`: 1 function + var-annotated issues
- `integration_module.py`: 2 functions
- `module_validator.py`: var-annotated issue
- `test_environment.py`: 1 function + Any return issue
- `performance.py`: var-annotated issue
- `compatibility.py`: type assignment issue
- `scenario_runner.py`: var-annotated issue

### C. Missing Neo4j Async Support (knowledge_validator.py)
- **Issue**: Module "neo4j" has no attribute "AsyncGraphDatabase"
- **Fix**: Neo4j Python driver doesn't have async support by default. Need to use sync version or asyncio wrapper

## 2. Resolution Strategy

### Step 1: Fix Method Call Issues
1. Fix ValidationContext usage - it should be ModuleValidator context
2. Fix QualityAssurancePipeline method calls - check actual method names
3. Fix cleanup method calls - ensure proper context management

### Step 2: Add Missing Type Annotations
1. Add return type annotations to all functions
2. Fix var-annotated issues by providing type hints
3. Remove unreachable code

### Step 3: Fix Neo4j Async Issues
1. Replace AsyncGraphDatabase with regular GraphDatabase
2. Use asyncio.to_thread for async wrapping if needed
3. Or install neo4j async extension if available

### Step 4: Fix Compatibility Issues
1. Fix type mismatches (bool vs str)
2. Handle None values properly with Optional types

## 3. Implementation Order

1. **First**: Fix scenario_runner.py method calls (blocking commit)
2. **Second**: Fix type annotations in testing modules (quick fixes)
3. **Third**: Fix AI assistant module issues (more complex)
4. **Fourth**: Fix remaining type annotations and Neo4j issues

## 4. Testing After Fixes

1. Run pre-commit hooks locally: `pre-commit run --all-files`
2. Run mypy separately: `mypy src/`
3. Run ruff: `ruff check src/`
4. Ensure all tests pass

## 5. Fallback Plan

If fixes become too complex:
1. Temporarily disable specific pre-commit hooks
2. Create technical debt tickets for complex issues
3. Focus on getting core functionality committed
4. Address remaining issues in separate commits

This follows the crawl_mcp.py pattern of systematic validation and error handling.
