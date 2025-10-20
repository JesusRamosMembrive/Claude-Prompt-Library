# Stage Assessment Criteria

## Stage 1: Prototyping (1-3 files, <500 LOC)

### Must Have:
- ✅ 1-3 files maximum
- ✅ <500 lines of code total
- ✅ Functions only (no classes unless trivial)
- ✅ Stdlib only (or 1-2 essential deps)

### Should Have:
- ✅ Single file if possible
- ✅ Clear purpose (proof of concept)
- ✅ No design patterns
- ✅ Direct, simple code

### Red Flags (over-engineering):
- ❌ Classes without clear need
- ❌ Abstract base classes
- ❌ Multiple layers
- ❌ Dependency injection
- ❌ Configuration files

## Stage 2: Structuring (4-20 files, 500-3000 LOC)

### Early Stage 2 (4-8 files, 500-1000 LOC):
- ✅ Just split into logical files
- ✅ Maybe 1 simple class
- ✅ 1-2 layers max (e.g., api/ + logic/)
- ⚠️ No patterns yet

### Mid Stage 2 (8-15 files, 1000-2000 LOC):
- ✅ Several classes emerging
- ✅ 2-3 layers (e.g., api/ + services/ + models/)
- ⚠️ 1 simple pattern OK if pain justified (e.g., Repository)
- ✅ Tests starting to appear

### Late Stage 2 (15-20 files, 2000-3000 LOC):
- ✅ Classes well-structured
- ✅ 3 layers
- ⚠️ 1-2 patterns in use (only if justified)
- ✅ Good test coverage
- ⚠️ Consider Stage 3 if growing

### Allowed Patterns (Stage 2):
- ✅ Repository (if abstracting data source)
- ✅ Service Layer (if business logic complex)
- ✅ Simple Factory (if creating 3+ types)
- ⚠️ Strategy (only if 3+ algorithms)
- ❌ Most other GoF patterns

### Red Flags:
- ❌ 4+ patterns
- ❌ 4+ architectural layers
- ❌ Abstract factories
- ❌ Heavy abstraction

## Stage 3: Scaling (20+ files, 3000+ LOC)

### Early Stage 3 (20-40 files, 3000-6000 LOC):
- ✅ Multiple patterns appropriate
- ✅ 3-4 architectural layers
- ✅ Clear module boundaries
- ✅ Comprehensive tests

### Mid Stage 3 (40-100 files, 6000-15000 LOC):
- ✅ Full architecture
- ✅ Multiple patterns working together
- ✅ Infrastructure concerns separated
- ✅ Plugin/extension system

### Late Stage 3 (100+ files, 15000+ LOC):
- ✅ Microservices consideration
- ✅ Advanced patterns
- ✅ Performance optimization
- ✅ Monitoring and observability

### Appropriate Patterns (Stage 3):
- ✅ All GoF patterns (if justified)
- ✅ Hexagonal Architecture
- ✅ CQRS
- ✅ Event Sourcing
- ✅ Circuit Breaker

## Decision Tree

1. **Files ≤ 3 AND LOC < 500** → Stage 1
2. **Files ≤ 20 AND LOC < 3000 AND Patterns ≤ 2** → Stage 2
   - Files ≤ 8 → Early Stage 2
   - Files 8-15 → Mid Stage 2
   - Files 15-20 → Late Stage 2
3. **Files > 20 OR LOC > 3000 OR Patterns > 2** → Stage 3

## Edge Cases

### Many files, few LOC:
- Lots of small files → Consider if over-split
- May indicate Stage 2 that needs consolidation

### Few files, many LOC:
- Giant files → Needs refactoring
- Likely Stage 2 but poor structure

### Many patterns, small codebase:
- Over-engineered
- Drop back to Stage 2
- Remove unnecessary abstractions

### Large codebase, no patterns:
- Under-engineered
- Consider Stage 3 refactor
- Add structure gradually