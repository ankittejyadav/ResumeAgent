---
name: drizzle-testing-mock
description: Guidelines for mocking and testing database logic during migrations from Supabase PostgREST queries to Drizzle ORM.
---

# Drizzle Testing & Mocking Guidelines

This skill documents standard architectures and practices for mocking database queries when migrating a codebase from Supabase PostgREST query builders to Drizzle ORM, ensuring existing unit/integration tests continue to run successfully.

## Core Concepts & Patterns

### 1. Legacy to Modern Chain Translation
During migrations, tests often mock Supabase chains (e.g., `.from('table').select().eq().single()`) while the production code is refactored to use Drizzle ORM select/insert statements.
To avoid rewriting all mock fixtures, implement a thread-safe factory proxy in the test file that translates Drizzle operator structures to match the existing mocked Supabase client chains.

### 2. Array vs. Single-Object Resolution (Destructuring Compatibility)
- **Supabase Mock Behavior:** Queries targeting single rows often end in `.single()` or `.maybeSingle()` and resolve directly to a single object (e.g. `{ data: { id: 1 } }`).
- **Drizzle Execution Behavior:** Queries like `const [row] = await db.select().limit(1)` or `const [row] = await db.insert().returning()` expect an array of rows.
- **Translation Rule:** The mock query translator's `.then()` method must:
  1. Detect if `.maybeSingle()` or `.single()` is present on the mocked chain and invoke it.
  2. Map non-array outputs from Supabase mocks (e.g. single row objects or `null`) into arrays (`[mappedRow]` or `[]`) to prevent destructuring exceptions (e.g., `(intermediate value) is not iterable`).

### 3. Join / Relation Field Mapping
- **Supabase Mock Joins:** Nested objects are returned for joined tables (e.g. `{ workout_exercises: { name: 'Bench Press' } }`).
- **Drizzle Joins:** Flattens selected columns into the base returned object (e.g. `{ exerciseName: 'Bench Press' }`).
- **Translation Rule:** The mock translator must explicitly check for nested relation objects (e.g. `workout_exercises`, `workout_sessions`) and map their inner properties to their flattened camelCase equivalents expected by Drizzle callers.

### 4. Error Wrapping
- Supabase queries return an object containing `{ data, error }` instead of throwing exceptions.
- Drizzle queries execute directly and throw database exceptions.
- Ensure the production database methods wrap Drizzle executions in `try-catch` blocks to reconstruct the identical error messages required by unit tests.

## Reference Mock Implementation

```javascript
function createQueryBuilder() {
    const state = {
        currentTable: null,
        operation: null,
        insertPayload: null,
        whereConditions: [],
    };

    const builder = {};

    // Map Svelte/Drizzle chain methods to query state
    const chainMethods = ['select', 'insert', 'values', 'where', 'returning'];
    for (const method of chainMethods) {
        builder[method] = (...args) => {
            if (method === 'select') state.operation = 'select';
            else if (method === 'insert') {
                state.operation = 'insert';
                state.currentTable = getTableName(args[0]);
            } else if (method === 'values') {
                state.insertPayload = args[0];
            } else if (method === 'where') {
                state.whereConditions.push(args[0]);
            }
            return builder;
        };
    }

    // Resolve builder as a Promise compatible with Drizzle destructuring
    builder.then = async (resolve, reject) => {
        try {
            let query = globalMockFrom(state.currentTable);

            // Translate Drizzle state to Supabase call chain
            if (state.operation === 'insert') {
                const insertResult = query.insert(state.insertPayload);
                // Fallback for non-chainable insert mock stubs
                query = (insertResult && typeof insertResult.select === 'function')
                    ? insertResult.select()
                    : insertResult;
            }

            // Bridge maybeSingle() / single() if defined on mock chain
            if (query) {
                if (typeof query.maybeSingle === 'function') query = query.maybeSingle();
                else if (typeof query.single === 'function') query = query.single();
            }

            const response = await query;
            if (response && response.error) {
                throw new Error(response.error.message);
            }

            const resultData = response && response.data !== undefined ? response.data : [];

            // Map and wrap nested join fields to array format
            if (Array.isArray(resultData)) {
                resolve(resultData.map(mapRowKeysToCamelCase));
            } else {
                resolve(resultData === null ? [] : [mapRowKeysToCamelCase(resultData)]);
            }
        } catch (err) {
            reject(err);
        }
    };

    return builder;
}
```
