# **Frontend directory tree (expanded)**

```
frontend/
├── app/
│   ├── layout.tsx                    # global shell: `<Header />` + providers; imports `../styles/globals.css`
│   ├── page.tsx                      # /         About screen (simple copy + description)
│   ├── form/
│   │   └── page.tsx                  # /form     Intake form page that renders `components/form/IntakeForm`
│   └── chat/
│       └── page.tsx                  # /chat     Chat surface page that renders `components/chat/ChatWindow`
│
├── components/
│   ├── common/
│   │   ├── Header.tsx                # title + minimal menu button and site title
│   │   └── MenuSheet.tsx             # small nav links (About / Form / Chat)
│   ├── form/
│   │   └── IntakeForm.tsx            # simple form with radios and text input; uses HTML inputs
│   └── chat/
│       ├── ChatWindow.tsx            # chat layout: messages area + input area
│       ├── MessageBubble.tsx         # small bubble component for message text
│       └── ChatInput.tsx             # input + send button (controlled behavior not yet wired)
│
├── ui/                               # small, reusable Tailwind-like primitives (lightweight)
│   ├── Button.tsx                     # simple button wrapper
│   ├── Card.tsx                       # card container
│   ├── Input.tsx                      # thin input wrapper
│   ├── RadioGroup.tsx                 # small native-radio based helper (can be extended for ARIA)
│   └── Badge.tsx                      # small inline tag component (label / count / status)
│
├── lib/
│   ├── api.ts                         # fetch helpers (apiBase and postQA helper)
│   ├── models.ts                      # shared TS types (QAResponse)
│   ├── validators.ts                  # zod schemas (IntakeSchema placeholder)
│   ├── storage.ts                     # sessionStorage helpers (load/save simple placeholders)
│   └── theme.ts                       # color tokens used by UI primitives
│
├── hooks/
│   ├── useIntake.ts                   # reads/writes intake to sessionStorage (simple hook)
│   └── useChat.ts                     # handles sending question via `lib/api.postQA` and storing messages
│
├── state/
│   └── chatStore.ts                   # (optional) placeholder zustand-like store shape (initialState)
│
├── styles/
│   └── globals.css                    # Tailwind imports placeholders (@tailwind base/components/utilities)
│
├── public/
│   ├── images/
│   │   └── `<addImage>`                   # placeholder — replace with real image
│   └── fonts/
│       └── README.md                  # guidance to add local fonts (Jost) or reference via CSS
│
├── tests/
│   ├── unit/
│   │   ├── validators.test.ts         # placeholder unit test
│   │   └── api.test.ts                # placeholder unit test
│   └── e2e/
│       └── chat.spec.ts               # placeholder e2e test
│
├── .env.local.example                 # NEXT_PUBLIC_API_BASE example
├── next.config.js                     # Next.js config (reactStrictMode)
├── tailwind.config.ts                 # Tailwind config (TS placeholder) — install types if using
├── postcss.config.js
├── tsconfig.json
└── package.json
```

# Descriptions (frontend)

- `app/layout.tsx`

  - Root layout for Next App Router. Renders the `Header` and wraps pages in a `<main>` area. Imports global CSS from `styles/globals.css`.
- `app/page.tsx`

  - Minimal About page used as the site root. Explains the app at a high level.
- `app/form/page.tsx`

  - Page that renders the `IntakeForm` component. The form is currently a simple HTML form with radio inputs and a text input.
- `app/chat/page.tsx`

  - Page that renders the `ChatWindow` component. The chat components are placeholders: the chat input calls `useChat` which posts to the backend `POST /api/qa` via `lib/api.postQA`.
- `components/common/Header.tsx`

  - Small header with a menu button and site title. Intended to host `MenuSheet` or other navigation UI in future iterations.
- `components/common/MenuSheet.tsx`

  - Minimal navigation links to About/Form/Chat. Can be replaced with a real mobile sheet or drawer UI.
- `components/form/IntakeForm.tsx`

  - Simple intake form with radio options for allergies and a single open-text concerns input. Uses `ui/*` primitives where appropriate.
- `components/chat/ChatWindow.tsx`

  - Layout with a scrollable messages area and `ChatInput` at the bottom. Renders `MessageBubble` components for messages. Hooked to `hooks/useChat.ts` for basic send/receive flow.
- `components/chat/MessageBubble.tsx`

  - Small presentational component responsible for rendering message text. Can be extended with author, timestamp, and styling variants.
- `components/chat/ChatInput.tsx`

  - Minimal input + send button UI. `useChat` provides a `send` method; currently the input is uncontrolled in the placeholder and should be wired to the hook for real use.
- `ui/*` (Button, Card, Input, RadioGroup, Badge)

  - Small, reusable primitives intended to keep styling consistent. Currently lightweight wrappers with Tailwind class names; these are suitable for incremental enhancement and theming via `lib/theme.ts`.
- `lib/api.ts`

  - `apiBase` reads `NEXT_PUBLIC_API_BASE` and `postQA` posts QA requests to the backend. Replace with more robust error handling and auth if needed.
- `lib/models.ts`

  - Types used across the frontend (e.g., `QAResponse`). Keep models in sync with backend schemas.
- `lib/validators.ts`

  - Zod schemas (e.g., `IntakeSchema`) to validate form payloads client-side before sending to backend.
- `lib/storage.ts`

  - Simple sessionStorage helpers: `loadSession(key)` and `saveSession(key, value)` used by `hooks/useIntake.ts`.
- `hooks/useIntake.ts`

  - Loads and saves intake state from sessionStorage (stateless feel). Exposes `data` and `save`.
- `hooks/useChat.ts`

  - Simple hook that posts questions to `lib/api.postQA` and appends responses into an in-memory `messages` array. Replace with streaming or WebSocket if desired.
- `state/chatStore.ts`

  - Placeholder for a shared chat store shape (for zustand or similar). Contains `Message` type and `initialState`.
- `styles/globals.css`

  - Contains Tailwind directives and basic global rules. Ensure Tailwind is configured and package installed to use these directives.
- `public/images/` and `public/fonts/README.md`

  - Placeholders for static assets. Add images and install local fonts or reference Google Fonts in CSS.
- `tests/` files

  - Very small placeholder tests to help scaffold CI/test runs. Replace with meaningful unit and e2e tests later.

# Notes & next steps

- Install frontend dependencies (Next, React, Tailwind, zod, types) to enable type checking and local dev. Example:

  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- Wire `ChatInput` to `hooks/useChat` and implement streaming or SSE for live responses.
- Add our logos/images and add font files for consistent branding.
- Add more robust tests for components and hooks.
- Refer to our Figma design and start changing the Frontend TSX code to reflect our actual design
- I just implemented a bare minimum code for the frontend to get it running so I need you guys to actually start on the code for it to be actually what it needs to look like.
