---
name: react-patterns
description: React production patterns — hooks, state management, performance optimization, and component design. Use when building React components, reviewing React code, or fixing React performance issues.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [react, frontend, hooks, state, performance, typescript]
triggers: ['react', 'component', 'hooks', 'jsx', 'frontend', 'next.js', 'react 18']
---

# React Patterns

Modern React (18+) patterns for production. TypeScript assumed.

## When to Use

- Building new React components or pages
- Reviewing React code for quality or performance
- Debugging re-renders or stale state
- Deciding where to put state

## Component Design

**Small, focused, composable:**

```tsx
// Bad — one component doing too much
function UserDashboard({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [notifications, setNotifications] = useState([]);
  // 300 lines of JSX mixing user info, orders table, notification bell...
}

// Good — composed from focused pieces
function UserDashboard({ userId }: { userId: string }) {
  return (
    <DashboardLayout>
      <UserProfile userId={userId} />
      <OrderHistory userId={userId} />
      <NotificationCenter userId={userId} />
    </DashboardLayout>
  );
}
```

## Hooks Patterns

### Data Fetching

```tsx
// Custom hook — logic separate from UI
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;   // prevent state update after unmount
    setLoading(true);
    fetchUser(userId)
      .then(data => { if (!cancelled) setUser(data); })
      .catch(err => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [userId]);

  return { user, loading, error };
}

// Use it in the component — clean separation
function UserProfile({ userId }: { userId: string }) {
  const { user, loading, error } = useUser(userId);
  if (loading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!user) return null;
  return <div>{user.name}</div>;
}
```

Use **React Query / TanStack Query** instead of manual useEffect for data fetching in real apps:

```tsx
import { useQuery } from "@tanstack/react-query";

function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
  // handles caching, deduplication, background refresh automatically
}
```

### State Management

**Where to put state:**

| State type | Where |
|---|---|
| UI state (open/closed, selected tab) | `useState` in the component |
| Shared UI state (theme, sidebar) | React Context |
| Server state (user data, API responses) | React Query / SWR |
| Complex client state | Zustand / Jotai |

```tsx
// Context for shared UI state — not for server data
const ThemeContext = createContext<{ theme: "light" | "dark"; toggle: () => void } | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const toggle = useCallback(() => setTheme(t => t === "light" ? "dark" : "light"), []);
  return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be inside ThemeProvider");
  return ctx;
}
```

## Performance

**useCallback and useMemo — only when there's a measurable problem:**

```tsx
// Use useMemo for expensive computations
const sortedItems = useMemo(
  () => items.sort((a, b) => b.score - a.score),
  [items]  // recalculate only when items changes
);

// Use useCallback for functions passed to memoized children
const handleSelect = useCallback((id: string) => {
  setSelectedIds(prev => [...prev, id]);
}, []);  // stable reference — won't trigger child re-renders
```

Don't add `useMemo`/`useCallback` everywhere "just in case". Profile first with React DevTools.

**Avoid re-renders:**

```tsx
// BAD — new object created on every render
<Component style={{ color: "red" }} />

// GOOD — stable reference
const style = { color: "red" } as const;
<Component style={style} />

// Or with useMemo if it depends on props/state
const style = useMemo(() => ({ color: isError ? "red" : "green" }), [isError]);
```

**List rendering:**

```tsx
// Always key by stable, unique ID — never array index for dynamic lists
{items.map(item => (
  <Item key={item.id} item={item} />  // id, not index
))}
```

## TypeScript Patterns

```tsx
// Props: explicit interface, not inline type
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
}

// Component return type
function Button({ label, onClick, variant = "primary", disabled = false }: ButtonProps): JSX.Element {
  return (
    <button
      className={styles[variant]}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
}

// Event handlers
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

// Ref typing
const inputRef = useRef<HTMLInputElement>(null);
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| `useEffect` with missing deps | Add missing deps or use `useCallback` to stabilize functions |
| State update after unmount | Add cleanup in useEffect with `cancelled` flag or AbortController |
| Index as list key | Use stable unique IDs |
| Fetching in `useEffect` directly | Use React Query or similar |
| Context for server data | Use React Query — Context causes full subtree re-renders |
