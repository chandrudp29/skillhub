---
name: typescript-patterns
description: Modern TypeScript best practices — strict types, utility types, generics, discriminated unions, and build tooling for production codebases
version: 1.0.0
tags: [typescript, javascript, types, frontend, backend]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when writing, reviewing, or refactoring any TypeScript code. Works for Node.js backends, React frontends, and full-stack projects.

## Core Rules

- Always use `strict: true` in tsconfig — never disable it to fix an error
- Prefer `type` for unions and intersections, `interface` for object shapes that extend
- Use `unknown` over `any` at boundaries; narrow with type guards before use
- Never use `as` casts to silence errors — fix the type instead
- Avoid `!` non-null assertions unless you've verified the value exists

## Type Design

```typescript
// Discriminated unions over boolean flags
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

// Utility types — use them, don't reinvent
type UserPreview = Pick<User, 'id' | 'name' | 'email'>;
type PartialConfig = Partial<Config>;
type ReadonlyUser = Readonly<User>;

// Branded types for semantic safety
type UserId = string & { readonly __brand: 'UserId' };
type EmailAddress = string & { readonly __brand: 'EmailAddress' };

// Const assertions for literal inference
const ROLES = ['admin', 'editor', 'viewer'] as const;
type Role = typeof ROLES[number]; // 'admin' | 'editor' | 'viewer'
```

## Generics

```typescript
// Constrain generics — never leave them open if you can help it
function first<T>(arr: readonly T[]): T | undefined {
  return arr[0];
}

// Conditional types for inference
type Awaited<T> = T extends Promise<infer U> ? U : T;

// Template literal types for string APIs
type EventName = `on${Capitalize<string>}`;
```

## Runtime Safety

```typescript
// Type guards at system boundaries
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    typeof (value as User).id === 'string'
  );
}

// Zod for schema validation at API boundaries
import { z } from 'zod';
const UserSchema = z.object({ id: z.string(), email: z.string().email() });
type User = z.infer<typeof UserSchema>;
```

## Error Handling

```typescript
// Typed error classes
class ApiError extends Error {
  constructor(
    message: string,
    public readonly statusCode: number,
    public readonly code: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Result pattern for expected failures
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };
```

## Tooling

- `tsc --noEmit` in CI — type-check without building
- `tsx` for running TypeScript directly in development
- `tsup` for library bundling (handles CJS/ESM dual output)
- ESLint with `@typescript-eslint/recommended-type-checked` — uses type info for deeper rules
- `verbatimModuleSyntax: true` in tsconfig — explicit `import type` for clarity
