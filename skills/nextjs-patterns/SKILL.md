---
name: nextjs-patterns
description: Production Next.js 14+ patterns — App Router, Server Components, data fetching, caching, performance, and deployment best practices
version: 1.0.0
tags: [nextjs, react, typescript, frontend, fullstack, web]
agents: [claude, cursor, codex, gemini]
---

## When to Use
Apply when building or reviewing Next.js 14+ applications using the App Router. Covers everything from component architecture to deployment.

## Core Rules

- Default to Server Components — add `'use client'` only when you need interactivity, browser APIs, or React hooks
- Never `fetch` in Client Components unless it's a user-triggered action — data belongs on the server
- Co-locate page files: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx` in the same folder
- Use `next/image` for every image — never a bare `<img>` tag
- Use `next/link` for navigation — never `<a href>`
- Validate all route params and search params with Zod before use

## App Router Architecture

```
app/
  layout.tsx           # root layout (html, body)
  page.tsx             # homepage
  (auth)/              # route group — no URL segment
    login/page.tsx
    register/page.tsx
  dashboard/
    layout.tsx         # nested layout — sidebar, nav
    page.tsx           # /dashboard
    [id]/
      page.tsx         # /dashboard/123
      loading.tsx      # streaming skeleton
      error.tsx        # error boundary
  api/
    users/route.ts     # API route handler
```

## Server vs Client Components

```typescript
// Server Component (default) — runs on server, has async, no hooks
async function UserProfile({ userId }: { userId: string }) {
  const user = await db.user.findUnique({ where: { id: userId } });
  return <div>{user?.name}</div>;
}

// Client Component — interactive, uses hooks, browser APIs
'use client';
function LikeButton({ postId }: { postId: string }) {
  const [liked, setLiked] = useState(false);
  return <button onClick={() => setLiked(l => !l)}>{liked ? '❤️' : '🤍'}</button>;
}
```

## Data Fetching & Caching

```typescript
// Server Component data fetching
async function Posts() {
  // Cached by default, revalidates every 60s
  const posts = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 }
  }).then(r => r.json());

  // Or: no cache for real-time data
  const live = await fetch('...', { cache: 'no-store' });
}

// Server Actions for mutations
'use server';
async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  await db.post.create({ data: { title } });
  revalidatePath('/posts');
}
```

## Performance

- Use `<Suspense>` boundaries to stream slow data — fast content renders first
- `generateStaticParams` for static generation of dynamic routes
- `loading.tsx` for automatic loading UI — avoids layout shift
- `dynamic('...', { ssr: false })` only for components that truly need browser-only rendering
- Keep Client Component trees small — push state down, not up

## Route Handlers

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const page = Number(searchParams.get('page') ?? '1');
  const users = await db.user.findMany({ skip: (page - 1) * 20, take: 20 });
  return NextResponse.json({ users, page });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const parsed = UserCreateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error }, { status: 400 });
  const user = await db.user.create({ data: parsed.data });
  return NextResponse.json(user, { status: 201 });
}
```

## Error Handling

```typescript
// app/dashboard/error.tsx
'use client';
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```
