# AI SupportOps — authentication, multilingual tickets and visual evidence update

These changes are on the `feature/rbac-vision-multilingual` branch. They do not replace `main`.

## New access model

| Role | Allowed operations |
|---|---|
| Customer | Register/login, create tickets, view only their own tickets, add messages, submit a photo for their own ticket, run the AI workflow on their own tickets |
| Support | View and manage tickets, use the knowledge base, process tickets, view pending approvals, approve/reject approval requests |
| Admin | Support permissions plus provision support-team accounts |

The role is read from the database after JWT validation. A browser-supplied role is never trusted. Public registration always creates a customer account. There is no public support/admin registration.

### First administrator

1. Configure the backend `.env` and database connection.
2. Apply the PostgreSQL migration below when upgrading an existing database.
3. Run this once from the repository root:

```powershell
python -m app.create_admin
```

4. Sign in through the React login screen with that admin account.
5. An administrator can create support accounts with the authenticated endpoint:

```
POST /api/v1/admin/users/support
Authorization: Bearer <admin access token>
Content-Type: application/json

{
  "email": "agent@example.com",
  "password": "a-long-unique-password"
}
```

The first administrator is provisioned locally rather than through an unauthenticated public endpoint. Existing customer rows are not automatically linked to new accounts based on email alone; that would allow account takeover without proving email ownership. Such legacy accounts need a verified account-linking workflow before customer self-service login.

## Environment and dependencies

Create/update the backend `.env` from `.env.example`. Set a unique JWT secret. Generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set `JWT_SECRET_KEY` to the generated value. Do not commit `.env` or the secret. Configure `DATABASE_URL`, `GROQ_API_KEY`, and `CORS_ORIGINS` for your environment. For production, set `ENVIRONMENT=production` and use the generated JWT secret; startup refuses the development default or a secret shorter than 32 characters.

Install backend dependencies:

```powershell
pip install -r requirements.txt
```

The frontend currently uses `sessionStorage` for its short-lived bearer token. This is suitable for the local portfolio demo but is readable by JavaScript; for production, prefer an HTTP-only, Secure, SameSite cookie or an established OIDC provider, add email verification and password recovery, and consider rate limiting and MFA. Set `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then run the usual backend and frontend development commands.

## Existing PostgreSQL database migration

SQLAlchemy `create_all` creates new tables but does not add columns to an existing table. Apply this migration once before starting the updated backend:

```bash
psql "$DATABASE_URL" -f migrations/20261125_auth_multilingual_vision.sql
```

It creates the `users` table and adds normalized text and preferred-language columns to `tickets`. Do not run it against a fresh database if the new schema has already been created; the statements are idempotent for these objects.

## Multilingual workflow

- The customer selects a preferred language or chooses auto-detect.
- The original subject and description remain in `tickets.subject` and `tickets.description`.
- The translation service detects the language and stores internal English-normalized copies in `normalized_subject` and `normalized_description`.
- The existing LangGraph agents use the normalized text.
- The generated customer response is translated back into the saved preferred language before it is stored as an agent message.

If translation inference is unavailable, the original text is preserved rather than discarded. In that fallback case the ticket may not be normalized for the English-focused agents, so verify the response before relying on it.

The initial UI offers English, Hindi, Telugu, Tamil, Kannada, Malayalam, Bengali, Marathi, Gujarati, Urdu and Punjabi, plus automatic detection. Actual translation quality depends on the configured LLM.

## Camera and Mirage workflow

- The customer can upload a JPEG, PNG or WebP image, or grant browser camera permission and capture a still frame.
- The frontend sends the image to `POST /api/v1/vision/tickets/{ticket_id}/analyze`.
- FastAPI validates the image type and size, writes it to a temporary file and calls `cactus.Mirage().describe(path)`.
- The temporary image is removed after analysis. The visual description is saved as ticket evidence, not the original image.
- The next agent run includes that visual evidence in the ticket description before classification, retrieval, troubleshooting, response generation and escalation.

Install `cactus-compute` in the backend environment. Mirage runs where the FastAPI backend is running; it is not executed in the browser. The backend host must support Cactus's native runtime and model download/cache. Validate this separately before deploying the Mirage feature to a managed host. Browser camera access requires localhost or HTTPS and the customer's permission.

Visual descriptions identify visible symptoms; they do not guarantee a root-cause diagnosis. The existing agents and support team must verify the cause. Human approval still records a review decision; it does not itself execute a refund, account update or subscription change.

## API access changes

- `POST /api/v1/auth/register` — customer registration
- `POST /api/v1/auth/login` — login; returns a short-lived JWT bearer token
- `GET /api/v1/auth/me` — current account
- `POST /api/v1/admin/users/support` — admin-only staff provisioning
- `GET /api/v1/tickets/` — customers see only their own tickets; support/admin see all
- `GET /api/v1/approvals/pending` — support/admin only
- `POST /api/v1/approvals/{approval_id}/decision` — support/admin only; reviewer identity comes from the authenticated account
- `POST /api/v1/vision/tickets/{ticket_id}/analyze` — authenticated owner or support/admin

The former approval API-key login and session routes have been removed. All protected endpoints use the same bearer-token authentication and enforce roles in FastAPI.
