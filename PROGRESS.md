# SankofaX — Development Progress Tracker

Single source of truth for what's **done** and what's **remaining**, based on the client
requirement documents. Full detail for each item is in
`Content/SankofaX_Website_ToDo_2026.docx`.

**Project:** SankofaX — frontend (Next.js) + backend (Django REST), one product.
**Last updated:** 2026-07-26

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
- [ ] **12. Verification tiers & workflow** (Level 1/2/3 + badge issuance) — backend + frontend
- [ ] **13. Job Board** — backend + frontend
- [ ] **14. Discussion Forum / Community section** — backend + frontend
- [ ] **15. Success Stories & Diaspora News** — backend + frontend
- [ ] **16. In-platform event ticketing / RSVP** — backend + frontend
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
