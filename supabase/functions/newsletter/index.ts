// Newsletter double opt-in endpoints (spec §13.4).
//
// POST {base}/subscribe      {email, first_name?, source?, website?}  (website = honeypot)
// GET  {base}/confirm?token=<uuid>       → 302 to site
// GET  {base}/unsubscribe?token=<uuid>   → 302 to site
//
// Secrets: RESEND_API_KEY (send-only key), SITE_URL, FROM_EMAIL.
// SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are injected by the platform.

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const SITE_URL = Deno.env.get("SITE_URL") ?? "https://marathonlongevity.run";
const FROM_EMAIL = Deno.env.get("FROM_EMAIL") ?? "Longevity Marathon <newsletter@marathonlongevity.run>";

const CORS = {
  "Access-Control-Allow-Origin": SITE_URL,
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

async function db(method: string, path: string, body?: unknown, prefer?: string): Promise<Response> {
  return await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method,
    headers: {
      apikey: SERVICE_KEY,
      Authorization: `Bearer ${SERVICE_KEY}`,
      "Content-Type": "application/json",
      ...(prefer ? { Prefer: prefer } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

async function sendConfirmEmail(email: string, firstName: string | null, confirmToken: string, unsubToken: string) {
  const confirmUrl = `${SUPABASE_URL}/functions/v1/newsletter/confirm?token=${confirmToken}`;
  const unsubUrl = `${SUPABASE_URL}/functions/v1/newsletter/unsubscribe?token=${unsubToken}`;
  const hi = firstName ? `Hi ${firstName},` : "Hi,";
  const text = `${hi}

Confirm your subscription to the Longevity Marathon newsletter by opening this link:

${confirmUrl}

You'll get new Journal entries, meaningful data updates, plan changes, and the eventual marathon result. No daily spam.

If you didn't request this, ignore this email and nothing will be sent. To never hear from us: ${unsubUrl}`;

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: FROM_EMAIL,
      to: [email],
      subject: "Confirm your subscription — Longevity Marathon",
      text,
    }),
  });
  if (!resp.ok) {
    throw new Error(`Resend failed: ${resp.status} ${await resp.text()}`);
  }
}

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

function redirect(state: string): Response {
  return new Response(null, {
    status: 302,
    headers: { Location: `${SITE_URL}/newsletter/?state=${state}` },
  });
}

async function handleSubscribe(req: Request): Promise<Response> {
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return json(400, { error: "Invalid request." });
  }

  // Honeypot: bots fill the hidden "website" field; pretend success.
  if (typeof body.website === "string" && body.website.trim() !== "") {
    return json(200, { ok: true });
  }

  const email = String(body.email ?? "").trim().toLowerCase();
  const firstName = String(body.first_name ?? "").trim().slice(0, 100) || null;
  const source = String(body.source ?? "").trim().slice(0, 100) || null;
  if (!EMAIL_RE.test(email) || email.length > 254) {
    return json(400, { error: "That doesn't look like a complete email address." });
  }

  const existingResp = await db(
    "GET",
    `subscriber?email=eq.${encodeURIComponent(email)}&select=id,confirmed_at,unsubscribed_at,confirm_token,unsubscribe_token`,
  );
  const existing = (await existingResp.json())[0];

  let confirmToken: string;
  let unsubToken: string;

  if (!existing) {
    const ins = await db(
      "POST",
      "subscriber",
      [{ email, first_name: firstName, source }],
      "return=representation",
    );
    if (!ins.ok) throw new Error(`insert failed: ${ins.status} ${await ins.text()}`);
    const row = (await ins.json())[0];
    confirmToken = row.confirm_token;
    unsubToken = row.unsubscribe_token;
  } else if (existing.confirmed_at && !existing.unsubscribed_at) {
    // Already subscribed; nothing to send. Same generic response as everyone.
    return json(200, { ok: true });
  } else {
    // Unconfirmed, or resubscribing after an unsubscribe: fresh token + consent.
    confirmToken = crypto.randomUUID();
    unsubToken = existing.unsubscribe_token;
    const upd = await db("PATCH", `subscriber?id=eq.${existing.id}`, {
      first_name: firstName,
      source,
      consent_at: new Date().toISOString(),
      confirm_token: confirmToken,
      confirmed_at: null,
      unsubscribed_at: null,
    });
    if (!upd.ok) throw new Error(`update failed: ${upd.status} ${await upd.text()}`);
  }

  await sendConfirmEmail(email, firstName, confirmToken, unsubToken);
  return json(200, { ok: true });
}

async function handleConfirm(url: URL): Promise<Response> {
  const token = url.searchParams.get("token") ?? "";
  if (!/^[0-9a-f-]{36}$/.test(token)) return redirect("invalid");
  const upd = await db(
    "PATCH",
    `subscriber?confirm_token=eq.${token}&confirmed_at=is.null`,
    { confirmed_at: new Date().toISOString(), unsubscribed_at: null },
    "return=representation",
  );
  const rows = upd.ok ? await upd.json() : [];
  return redirect(rows.length > 0 ? "confirmed" : "invalid");
}

async function handleUnsubscribe(url: URL): Promise<Response> {
  const token = url.searchParams.get("token") ?? "";
  if (!/^[0-9a-f-]{36}$/.test(token)) return redirect("invalid");
  const upd = await db(
    "PATCH",
    `subscriber?unsubscribe_token=eq.${token}`,
    { unsubscribed_at: new Date().toISOString() },
    "return=representation",
  );
  const rows = upd.ok ? await upd.json() : [];
  return redirect(rows.length > 0 ? "unsubscribed" : "invalid");
}

Deno.serve(async (req: Request) => {
  const url = new URL(req.url);
  const route = url.pathname.split("/").filter(Boolean).pop();

  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

  try {
    if (req.method === "POST" && route === "subscribe") return await handleSubscribe(req);
    if (req.method === "GET" && route === "confirm") return await handleConfirm(url);
    if (req.method === "GET" && route === "unsubscribe") return await handleUnsubscribe(url);
  } catch (err) {
    console.error(err);
    return json(500, { error: "Something went wrong on our side. Please try again." });
  }
  return json(404, { error: "Not found." });
});
