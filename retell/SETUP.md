# Retell AI Setup Guide for Air Reservations

## Step 1 — Create three Knowledge Bases

In the Retell dashboard (app.retellai.com → Knowledge Base):

| Name | Purpose |
|------|---------|
| Air Homes | All home/hotel listings (user-added + Google Places imports) |
| Air Experiences | Guided tours, activities, classes |
| Air Events | Parties, concerts, festivals |

Leave them empty — the backfill script fills them automatically.
Copy each `knowledge_base_id` into your `.env`.

---

## Step 2 — Create a Retell LLM

1. Go to **LLM → Create New LLM**
2. Paste the contents of `retell/master_prompt.md` into the **System Prompt** field
3. Under **Knowledge Bases**, add the three KB IDs from Step 1
4. Under **Tools / General Tools**, paste the contents of `retell/tools.json`
   - Replace every `{{PUBLIC_BASE_URL}}` with your deployed site URL
     (e.g. `https://air.yourdomain.com`)
5. Save and copy the `llm_id`

---

## Step 3 — Create a Retell Agent

1. Go to **Agent → Create New Agent**
2. Set **Response Engine** → select the LLM from Step 2
3. Set **Webhook URL** → `https://YOUR-SITE-URL/api/retell/events`
4. Save and copy the `agent_id` and the **Webhook Signing Secret**

---

## Step 4 — Fill in `.env`

```
RETELL_AGENT_ID=           # from Step 3
RETELL_LLM_ID=             # from Step 2
RETELL_KB_HOMES_ID=        # from Step 1
RETELL_KB_EXPERIENCES_ID=  # from Step 1
RETELL_KB_PARTIES_ID=      # from Step 1
RETELL_WEBHOOK_SECRET=     # signing secret from Step 3
PUBLIC_BASE_URL=https://your-deployed-site.com
```

---

## Step 5 — Backfill existing listings (run once)

After deploying the app with the new env vars:

```bash
python -m app.scripts.backfill_kb
```

This walks every published listing in Firestore and adds it to the right KB.
Each listing gets a `retellSourceId` written back to its Firestore document —
future edits use this to replace the correct KB entry.

---

## Step 6 — Test

1. Open any home listing on the site and click **Start Voice Call**
2. The agent should greet you and mention the listing by name
3. Ask "how much per night?" — it should quote the correct price from the KB
4. Say a check-in date — it should call `check_availability`
5. Proceed to booking — confirm a `kb_sync_failures`-free Firestore booking doc is created
6. End the call — within ~30 s a `call_logs` document should appear in Firestore

---

## How live sync works (automatic, no action needed)

Every time a listing is created, edited, or deleted via the app:
- `listing_sync.sync_listing()` is called automatically
- It adds/replaces/removes the matching source in the Retell KB
- The `retellSourceId` on the Firestore doc is kept up to date
- Google Places imports are synced the same way

If Retell is temporarily down, the listing save succeeds and a
`kb_sync_failures` document is written to Firestore for retry later.
