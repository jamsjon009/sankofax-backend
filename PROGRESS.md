# SankofaX — Development Progress Tracker

Single source of truth for what's **done** and what's **remaining**, based on the client
requirement documents. Full detail for each item is in
`Content/SankofaX_Website_ToDo_2026.docx`.

**Project:** SankofaX — frontend (Next.js) + backend (Django REST), one product.
**Last updated:** 2026-07-27

## Legend
- `[ ]` not started
- `[~]` in progress
- `[x]` done
- `[-]` skipped / not needed (with a note)

---

## ✅ Already built (baseline — no action needed)
- [x] Accounts, roles, JWT login, email verification, password reset
- [x] Business/company profiles (logo, cover, description, contact, website, verified flag)
- [x] Directory: live search, category/location/price/rating filters, pagination, grid + map
- [x] Listing detail: gallery, contact, reviews & ratings, map
- [x] Subscriptions: Global North/South pricing + Stripe checkout & portal
- [x] Blog, Events, Marketplace (external links), Newsletter, Testimonials
- [x] Admin: listing approval/reject workflow, stats dashboard, page-view analytics
- [x] Interactive maps (Leaflet), Contact page, Pricing page

---

## Phase 1 — Core requirement gaps + fixes (finish the MVP)

> **Priority A (1–7) ✅ and Priority B (8–11) ✅ complete.** Phase 1 MVP gaps all done — next up is Phase 2 (growth features, items 12+).

### Priority A — core gaps
- [x] **1. Ownership / Identity Badge system** (Women/Black/LGBTQ+/Asian-Owned…) — backend + frontend
  - Done: `IdentityBadge` model + `CompanyProfile.badges` M2M, admin management, `/api/badges/`, badges on listing cards & detail, and an "Ownership & Identity" directory filter. 8 default badges seeded.
  - Follow-up (small): let business owners pick their own badges from the dashboard (API already accepts `badges`; UI not added yet).
- [x] **2. "Connect" & "Collaborate" system** (+ inbox/messaging) — backend + frontend
  - Done: new `connections` app with `Connection` model, `/api/connections/` (inbox/sent list + create), accept/decline, unread count. Connect & Collaborate buttons + modal on listing detail; dashboard `/dashboard/inbox` with Received/Sent tabs and accept/decline.
- [x] **3. Business Type filter** in directory — backend + frontend
  - Done: `business_type` field on Listing (Product / Service / Both / Nonprofit), directory filter + sidebar UI, shown on listing detail, editable in create/edit wizard, admin filter, seeded.
- [x] **4. Founder Story** field on business profiles — backend + frontend
  - Done: `founder_story` on CompanyProfile, exposed via company + listing-detail APIs, shown as a "Founder Story" section on listing detail, settable in the New Company form + admin, seeded.
  - Follow-up (small): editing an existing company's founder story from the dashboard needs the company edit page (ties into #8).
- [x] **5. Company social links & services offered** — backend + frontend
  - Done: CompanyProfile gets `services` + 6 social URL fields (instagram/facebook/twitter/linkedin/youtube/tiktok), exposed via company API and on listing detail (`company_services`, `company_socials`). Shown as a "Services Offered" section + social icons; settable in the New Company form + admin; seeded.
- [x] **6. Live homepage statistics** (Businesses / Members / Partnerships) — backend + frontend
  - Done: public `GET /api/stats/` (businesses = published listings, members = users, partnerships = accepted connections, + countries). Hero now renders these live instead of hardcoded numbers.
- [x] **7. Role selection at sign-up** (Business Owner vs Visitor) — frontend
  - Done: register form now has a Visitor / Business Owner selector that sends `account_type`; backend maps it to the user role (verified: business → business_owner, visitor → visitor).

### Priority B — missing pages & broken links
- [x] **8. Company public profile page** `/company/[slug]` — frontend
  - Done: full public page (cover, logo, verified, badges, about, founder story, services, social links, contact) + a grid of the company's published listings. Backend: added `company` filter to the listings API.
  - Note: a dashboard **company-edit** page (to change founder story / services / socials after creation) is still missing — owners set these at creation or via admin. Good candidate for its own task.
- [x] **9. Standalone FAQ page** `/faqs` — frontend
  - Done: `/faqs` page (hero + admin-fed accordion, reuses FAQSection with an optional-heading toggle + Contact CTA). Fixes the footer dead link.
- [x] **10. Legal/static pages** (Terms, Privacy, Cookies) — frontend + admin content
  - Done: `/terms`, `/privacy`, `/cookies` frontend routes (thin pages sharing a `LegalPage` component that renders admin content + a "Last updated" date + Contact CTA). Backend already had the `Page` model + `/api/pages/<slug>/`; added `updated_at` to that response and a data migration (`0008_seed_legal_pages`) that seeds the three pages so the footer links always resolve. Admins edit copy in Django admin (Core → Pages). Also seeded `cookies` in `seed_demo`.
- [x] **11. Careers page** `/careers` (or link to Job Board) — frontend
  - Done: self-contained `/careers` page (hero, "Why work with us" values grid, "Open positions" section with an "Email us your CV" mailto CTA that uses the site contact email, and a Browse-the-Directory CTA). Frontend-only per the requirement; no Job Board dependency. Fixes the last footer dead link. When the Job Board (#13) ships, the "Open positions" section can link to it.

---

## Phase 2 — Business-plan growth features
- [x] **12. Verification tiers & workflow** (Level 1/2/3 + badge issuance) — backend + frontend
  - Done. **Backend:** `CompanyProfile` gains `verification_level` (0 None / 1 Basic-automated / 2 Verified-documents / 3 Certified-partner), `verified_at`, `verification_expires_at`; `is_verified` kept in sync. New `VerificationRequest` model + workflow (`grant/revoke/approve/reject`). APIs: `GET /api/verification/companies/<slug>/` (owner status + automated-check results + latest request), `GET/POST /api/verification/requests/` (Level 1 auto-resolves from automated checks; Levels 2/3 require a document upload → pending admin review). Admin approve/reject actions + grant/revoke tier actions. Tier exposed on company + listing card/detail serializers. `expire_verifications` management command for periodic re-verification. Data migration backfills existing `is_verified=True` → Level 2.
  - **Frontend:** `/dashboard/verification` page (current tier, "last granted/renews" dates, profile-completeness checks, per-tier request cards with document upload + admin-note feedback) + a `Verification` nav item. Tier-aware `VerificationBadge` component on listing cards, listing detail and the company page. Also fixed a latent bug: `myCompanies.list` now unwraps the paginated response.
- [~] **13. Job Board** — backend + frontend
  - **Deferred — blocked on client input.** Two scope decisions needed before building: (a) apply flow — external apply links only vs in-platform applications (employers review in dashboard) vs both; (b) posting flow — owners + admin review vs owners auto-publish vs admin-only. Resume once the client confirms.
- [x] **14. Discussion Forum / Community section** — backend + frontend
  - Done. **Backend:** new `community` app — `ForumCategory` (boards) → `Thread` → `Reply`. Public read, authenticated posting/replying, author/staff delete, admin pin/lock moderation. APIs: `GET /api/community/categories/`, `GET/POST /api/community/threads/` (filter `?category=&q=`), `GET/DELETE /api/community/threads/<slug>/` (view-count bump, `is_author` flag), `GET/POST /api/community/threads/<slug>/replies/` (locked → 400, unauth → 401, bumps `last_activity_at`). Data migration seeds 5 default boards; sample threads in `seed_demo`.
  - **Frontend:** `/community` (hero, board filter chips, search, thread cards), `/community/[slug]` (thread + replies + reply form / locked notice / sign-in prompt + author delete), `/community/new` (create form). Added **Community** to the header nav; API helpers + types.
  - **Bonus fix:** the shared `request()` helper was dropping `Content-Type` on every authed JSON POST/PATCH (the `...options` spread overwrote the merged headers → DRF 415 `text/plain`). Fixed — this also repairs connections/testimonials/reviews submits app-wide.
- [x] **15. Success Stories & Diaspora News** — backend + frontend
  - Done, built on the existing blog (as the ToDo suggested). **Backend:** data migration seeds two dedicated blog categories — `success-stories` ("Business Stories & Legacy") and `diaspora-news`; the blog list API already supports `?category__slug=`. Sample posts for both added to `seed_demo`. **Frontend:** shared `CategoryLanding` server component (hero + featured lead post + grid) powering `/stories` and `/news`; individual posts open in the existing `/blog/[slug]` reader. Added Success Stories, Diaspora News (and Community) to the footer Discover list.
- [x] **16. In-platform event ticketing / RSVP** — backend + frontend
  - Done. **Backend:** `Event` gains `rsvp_enabled`, `capacity` (blank = unlimited), `allow_waitlist`, `registration_deadline` + helper props (`confirmed_count`, `spots_left`, `is_full`, `registration_open`). New `EventRegistration` model (attendee, quantity, status confirmed/waitlisted/cancelled, unique `ticket_code`, check-in fields; partial unique constraint = one active RSVP per user/event). APIs on the events viewset: `POST/DELETE /api/events/<slug>/register/` (capacity → confirmed or waitlist; cancel **auto-promotes** the earliest waitlisted, FIFO, in a locked transaction), `GET /api/events/my-tickets/`, organizer-only `GET /api/events/<slug>/attendees/` + `POST /api/events/<slug>/attendees/<id>/check-in/`. Event serializer exposes RSVP fields + `my_registration`. Admin: `EventRegistration` admin + inline on Event + check-in actions. Seed enables RSVP + sample registrations (fills the capped event so the waitlist shows). Paid/external events keep the existing `ticket_url` fallback (Stripe-paid tickets can layer on later, alongside #17).
  - **Frontend:** event **detail page** `/events/[slug]` (new) with an RSVP sidebar (spots-left / full / waitlist states, ticket-code card, cancel, sign-in prompt) + an organizer-only collapsible **attendee panel** with check-in. Event cards now link to the detail page and show an RSVP / Get Tickets / Waitlist badge. New `/dashboard/tickets` "My Tickets" page + nav item. API helpers + types added. Verified end-to-end in the browser (RSVP→confirmed, full→waitlist, my-tickets, organizer check-in, no console errors).
- [ ] **17. Marketplace checkout / service booking** — backend + frontend
- [ ] **18. Story-promotion packages** (paid founder stories/features) — backend + frontend
- [ ] **19. Enterprise analytics API / data export** — backend
- [ ] **20. Real geocoding for the map** (auto lat/long from address) — backend

---

## Ongoing — content & data
- [ ] **21. Seed the 15 real businesses** from Company Descriptions 2025 — data/admin
- [ ] **22. Load website copy** (headlines, mission, FAQs, plan text) into admin — content
- [ ] **23. Confirm pricing** (North $15/$29/$49, South $7.50/$14.50/$24.50) + auto region — backend + content

---

## Work log
_Newest first. Each entry: date — what changed — which items._

- **2026-07-27** — Item **#16 (In-platform event ticketing / RSVP)** done and verified. **Backend:** RSVP fields on `Event` (`rsvp_enabled`/`capacity`/`allow_waitlist`/`registration_deadline` + count/spots/full/open helpers), new `EventRegistration` model (ticket code, statuses, check-in, one-active-RSVP-per-user constraint), register/cancel with capacity→waitlist and **auto-promotion on cancel** (locked txn), `my-tickets`, organizer attendees + check-in, admin + inline, seed. **Frontend:** new `/events/[slug]` detail page with RSVP sidebar + organizer attendee/check-in panel, cards link to detail with RSVP/Waitlist badges, `/dashboard/tickets` My Tickets page + nav. Verified end-to-end in the browser (confirm, waitlist, my-tickets, check-in; no console errors). External-ticket events keep the `ticket_url` fallback; Stripe-paid tickets deferred to layer on with #17.
- **2026-07-26** — Item **#15 (Success Stories & Diaspora News)** done and verified. Two dedicated blog categories (`success-stories`, `diaspora-news`) seeded via migration; shared `CategoryLanding` component powers `/stories` and `/news` (hero + featured + grid), posts open in the existing blog reader; footer links added. Sample posts in `seed_demo`.
- **2026-07-26** — Item **#14 (Discussion Forum / Community)** done and verified. New `community` app (ForumCategory → Thread → Reply), public read + authed posting + admin pin/lock moderation, 5 seeded boards. Frontend: `/community`, `/community/[slug]`, `/community/new` + Community nav item. Verified end-to-end via the UI (list, detail, create thread, reply, auth 401, locked 400). **Also fixed a latent app-wide bug**: `request()` dropped `Content-Type` on authed JSON POST/PATCH (415 text/plain) — now fixed. **#13 (Job Board) deferred** pending client decisions on apply/posting scope.
- **2026-07-26** — Item **#12 (Verification tiers & workflow)** done and verified — first Phase 2 feature. Backend: `verification_level` (0–3) + `verified_at`/`expires_at` on CompanyProfile, `VerificationRequest` model + submit→review workflow, Level-1 automated checks (auto-grant), Level-2/3 document review, admin approve/reject + grant/revoke actions, `expire_verifications` command, tier on listing/company APIs, backfill migration. Frontend: `/dashboard/verification` page + nav, tier-aware `VerificationBadge` on cards/detail/company page, dashboard CTA repointed. Also fixed `myCompanies.list` pagination unwrap. Verified end-to-end (L1 auto-grant, doc upload→pending, admin approve, revoke, expiry).
- **2026-07-26** — Item **#11 (Careers page)** done and verified — self-contained `/careers` (hero + values grid + "Email us your CV" mailto CTA using the site contact email + directory CTA). **Priority B (8–11) complete → Phase 1 MVP done.**
- **2026-07-26** — Item **#10 (Legal/static pages)** done and verified — `/terms`, `/privacy`, `/cookies` frontend routes (shared `LegalPage` component, admin-fed content + "Last updated"). Backend: `updated_at` added to `/api/pages/<slug>/`, data migration seeds the 3 pages, `cookies` added to `seed_demo`. Fixes the 3 footer dead links.
- **2026-07-26** — Item **#9 (FAQ page)** done. Plus **layout fixes**: listing-detail & company pages widened to `max-w-7xl` (edges align with the site), 12-col 8/4 grid, sticky sidebar. About page rebuilt (fixed mojibake em-dashes + hero, consistent with Contact/FAQ). Pricing page widened to `max-w-7xl`, 4-plan grid (`sm:grid-cols-2 lg:grid-cols-4`) so the 4th card no longer sits alone, and the comparison table now scrolls on mobile.
- **2026-07-26** — Item **#8 (Company profile page)** completed and verified — `/company/[slug]` public page + listings `company` filter. Fixes the dead link from listing detail.
- **2026-07-26** — Item **#7 (Signup role selection)** completed and verified — **Priority A (1–7) done**. Register sends `account_type`; role set correctly.
- **2026-07-26** — Item **#6 (Live homepage stats)** completed and verified (public /api/stats/ + hero renders live Businesses/Members/Partnerships).
- **2026-07-26** — Item **#5 (Social links & services offered)** completed and verified (company fields + APIs + listing-detail display + New Company form).
- **2026-07-26** — Item **#4 (Founder Story)** completed and verified (field + APIs + listing-detail section + New Company form).
- **2026-07-26** — Item **#3 (Business Type filter)** completed and verified (field + directory filter + detail display + create/edit forms).
- **2026-07-26** — Item **#2 (Connect & Collaborate system)** completed and verified (new `connections` app + endpoints, listing-detail buttons/modal, dashboard inbox). Also fixed the README to match the project.
- **2026-07-26** — Item **#1 (Identity Badge system)** completed and verified end-to-end (backend model/API/filter/seed + frontend cards, detail, directory filter).
- **2026-07-26** — Created progress tracker and gap-analysis document. No feature items started yet.
