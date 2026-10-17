#!/usr/bin/env python3
"""Lead radar: collects public signals (tenders, issues, questions, gigs), scores them against
product profiles, remembers what was already seen, writes a Markdown digest with draft openers.

Nothing is ever sent automatically. Drafts are for a human to paste.

Usage:
  python3 leads/radar.py                      # last 7 days, all profiles, digest to leads/digest/
  python3 leads/radar.py --days 3 --profiles lake,avroconvert
  python3 leads/radar.py --llm                # rate + draft openers with Anthropic/OpenAI (needs API key env)
  python3 leads/radar.py --sources ted,useme  # restrict sources

Env (optional): GITHUB_TOKEN (higher rate limits; also enables --llm via GitHub Models),
GITHUB_MODELS_TOKEN (a PAT with models:read if you want GitHub Models locally),
ANTHROPIC_API_KEY or OPENAI_API_KEY (alternative --llm providers, take precedence).
Only the standard library is used.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UA = "soltechnology-lead-radar/0.1 (+https://soltechnology.dev; contact@soltechnology.dev)"


# ----------------------------------------------------------------------------- model

@dataclass
class Lead:
    source: str
    uid: str              # stable id within source
    title: str
    url: str
    body: str = ""
    org: str = ""
    country: str = ""
    date: str = ""        # ISO date
    deadline: str = ""
    extra: dict = field(default_factory=dict)
    # filled by scoring
    profile: str = ""
    score: int = 0
    hits: list = field(default_factory=list)
    llm_score: int | None = None
    llm_reason: str = ""
    opener: str = ""

    @property
    def key(self) -> str:
        return f"{self.source}:{self.uid}"

    def text(self) -> str:
        return f"{self.title}\n{self.body}\n{self.org}".lower()


# ----------------------------------------------------------------------------- http

def http(url: str, *, method="GET", data: dict | None = None, headers: dict | None = None, retries=3, timeout=40) -> bytes:
    hdrs = {"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    if headers:
        hdrs.update(headers)
    payload = None
    if data is not None:
        payload = json.dumps(data).encode()
        hdrs["Content-Type"] = "application/json"
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=payload, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                return raw
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def http_json(url, **kw):
    return json.loads(http(url, **kw))


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def since_date(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


# ----------------------------------------------------------------------------- collectors
# Each collector: (days:int, log) -> list[Lead]. Collectors are profile-agnostic; scoring decides.

TED_CPV = ["72000000", "72200000", "72210000", "72212000", "72220000", "72230000", "72240000", "72250000",
           "72260000", "72300000", "72310000", "72320000", "72330000", "72400000", "48000000", "48600000",
           "48800000", "48810000", "48900000"]


def collect_ted(days: int, log) -> list[Lead]:
    """EU public procurement (TED). Anonymous Search API v3."""
    start = since_date(days).strftime("%Y%m%d")
    q = (f"(classification-cpv IN ({' '.join(TED_CPV)})) AND publication-date >= {start} "
         f"AND notice-type IN (cn-standard cn-social pin-cfc-standard pin-only pin-buyer qu-sy)")
    fields = ["publication-number", "notice-title", "publication-date", "buyer-name", "buyer-country",
              "links", "description-lot", "classification-cpv", "deadline-receipt-tender-date-lot",
              "estimated-value-lot", "estimated-value-cur-lot"]
    out, page = [], 1
    while True:
        d = http_json("https://api.ted.europa.eu/v3/notices/search",
                      method="POST", data={"query": q, "fields": fields, "limit": 250, "page": page, "scope": "ACTIVE"})
        for n in d.get("notices", []):
            def first(v):
                if isinstance(v, dict):
                    # prefer ENG, then POL, then anything
                    for lang in ("eng", "pol", "deu", "fra"):
                        if lang in v and v[lang]:
                            return " ".join(v[lang]) if isinstance(v[lang], list) else str(v[lang])
                    for val in v.values():
                        return " ".join(val) if isinstance(val, list) else str(val)
                if isinstance(v, list):
                    return " ".join(str(x) for x in v)
                return str(v or "")
            pn = n.get("publication-number", "")
            links = n.get("links", {}).get("html", {})
            url = links.get("ENG") or links.get("POL") or next(iter(links.values()), f"https://ted.europa.eu/en/notice/-/detail/{pn}")
            val = n.get("estimated-value-lot")
            cur = n.get("estimated-value-cur-lot")
            out.append(Lead(
                source="ted", uid=pn, title=first(n.get("notice-title")), url=url,
                body=first(n.get("description-lot"))[:1500], org=first(n.get("buyer-name")),
                country=first(n.get("buyer-country")), date=str(n.get("publication-date", ""))[:10],
                deadline=first(n.get("deadline-receipt-tender-date-lot"))[:10],
                extra={"cpv": sorted(set(n.get("classification-cpv", []) or [])),
                       "value": f"{first(val)} {first(cur)}".strip()},
            ))
        total = d.get("totalNoticeCount", 0)
        log(f"ted: page {page}, {len(out)}/{total}")
        if len(out) >= total or not d.get("notices") or page >= 8:
            break
        page += 1
        time.sleep(0.5)
    return out


GITHUB_ISSUE_QUERIES = [
    "avro language:csharp", "avro \".net\"", "\"schema registry\" \".net\"", "avrogen", "AvroConvert",
    "iceberg \".net\"", "iceberg c#", "\"delta lake\" \".net\"", "parquet language:csharp", "\"apache arrow\" c#",
    "adbc c#", "databricks \".net\"", "onelake \".net\"", "copybook c#", "ebcdic c#", "cobol \".net\"",
    "\"data masking\" c#", "anonymization \".net\" database",
]


def collect_github_issues(days: int, log) -> list[Lead]:
    """Open issues/discussions where people describe .NET + data problems. Unauthenticated: 10 req/min."""
    token = os.environ.get("GITHUB_TOKEN")
    hdrs = {"Accept": "application/vnd.github+json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    start = since_date(days).strftime("%Y-%m-%d")
    out, seen = [], set()
    for q in GITHUB_ISSUE_QUERIES:
        full = f"{q} is:issue created:>={start}"
        url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({"q": full, "sort": "created", "order": "desc", "per_page": 30})
        try:
            d = http_json(url, headers=hdrs)
        except Exception as e:  # noqa: BLE001
            log(f"github: '{q}' failed: {e}")
            time.sleep(8)
            continue
        for it in d.get("items", []):
            if it["html_url"] in seen:
                continue
            seen.add(it["html_url"])
            repo = it["repository_url"].split("/repos/")[-1]
            out.append(Lead(
                source="github_issues", uid=str(it["id"]), title=it["title"], url=it["html_url"],
                body=(it.get("body") or "")[:1500], org=repo.split("/")[0], date=it["created_at"][:10],
                extra={"repo": repo, "comments": it.get("comments", 0), "author": it["user"]["login"], "query": q},
            ))
        log(f"github: '{q}' -> {d.get('total_count', 0)}")
        time.sleep(1 if token else 7)
    return out


def collect_github_dependents(days: int, log) -> list[Lead]:
    """Public repos depending on AvroConvert: organisations here are licence-upgrade leads."""
    url = "https://github.com/AdrianStrugala/AvroConvert/network/dependents"
    out = []
    try:
        page = http(url).decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        log(f"dependents: {e}")
        return out
    for m in re.finditer(r'<a[^>]+data-hovercard-type="(?:organization|user)"[^>]+href="/([^"/]+)"[^>]*>\s*([^<]+)</a>\s*/\s*<a[^>]+href="/([^"]+)"', page):
        owner, _, repo = m.group(1), m.group(2), m.group(3)
        if owner.lower() == "adrianstrugala":
            continue
        out.append(Lead(source="github_dependents", uid=repo, title=f"{repo} depends on AvroConvert",
                        url=f"https://github.com/{repo}", org=owner, body="avro avroconvert dependent repository", date=""))
    log(f"dependents: {len(out)} repos on first page")
    return out


SE_TAG_SETS = [["c#", "avro"], ["c#", "apache-kafka"], [".net", "avro"], ["c#", "parquet"], ["c#", "apache-arrow"],
               ["c#", "apache-iceberg"], ["c#", "delta-lake"], ["c#", "databricks"], ["c#", "cobol"], ["c#", "ebcdic"],
               ["c#", "data-masking"], ["sql-server", "data-masking"], ["c#", "snowflake-cloud-data-platform"]]


def collect_stackexchange(days: int, log) -> list[Lead]:
    start = int(since_date(days).timestamp())
    out, seen = [], set()
    for tags in SE_TAG_SETS:
        url = ("https://api.stackexchange.com/2.3/questions?" + urllib.parse.urlencode({
            "order": "desc", "sort": "creation", "tagged": ";".join(tags), "site": "stackoverflow",
            "fromdate": start, "pagesize": 50, "filter": "withbody"}))
        try:
            d = http_json(url)
        except Exception as e:  # noqa: BLE001
            log(f"stackexchange {tags}: {e}")
            continue
        for q in d.get("items", []):
            if q["question_id"] in seen:
                continue
            seen.add(q["question_id"])
            out.append(Lead(source="stackexchange", uid=str(q["question_id"]), title=html.unescape(q["title"]),
                            url=q["link"], body=strip_html(q.get("body", ""))[:1500],
                            org=q.get("owner", {}).get("display_name", ""),
                            date=datetime.fromtimestamp(q["creation_date"], timezone.utc).strftime("%Y-%m-%d"),
                            extra={"tags": q.get("tags", []), "answers": q.get("answer_count", 0), "views": q.get("view_count", 0)}))
        log(f"stackexchange {'+'.join(tags)}: {len(d.get('items', []))}; quota {d.get('quota_remaining')}")
        if d.get("backoff"):
            time.sleep(d["backoff"])
    return out


REDDIT_FEEDS = [
    ("dotnet", "avro OR parquet OR iceberg OR kafka OR databricks OR \"schema registry\" OR arrow OR copybook OR mainframe OR masking"),
    ("csharp", "avro OR parquet OR iceberg OR kafka OR databricks OR copybook OR ebcdic"),
    ("dataengineering", "\".net\" OR \"c#\" OR dotnet"),
    ("apachekafka", "\".net\" OR \"c#\" OR dotnet"),
    ("humanresources", "\"pay transparency\" OR \"pay gap\""),
    ("Polska_rachunkowosc", "doręczenia"),
    ("ksiegowosc", "doręczenia"),
]


def collect_reddit(days: int, log) -> list[Lead]:
    """old.reddit RSS search; reddit.com JSON is blocked without OAuth."""
    out = []
    cutoff = since_date(days)
    for sub, q in REDDIT_FEEDS:
        url = f"https://old.reddit.com/r/{sub}/search.rss?" + urllib.parse.urlencode({"q": q, "restrict_sr": "on", "sort": "new", "t": "month"})
        try:
            xml = http(url).decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            log(f"reddit r/{sub}: {e}")
            continue
        n = 0
        for entry in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
            title = strip_html(re.search(r"<title>(.*?)</title>", entry, re.S).group(1)) if re.search(r"<title>", entry) else ""
            link = re.search(r'<link href="([^"]+)"', entry)
            updated = re.search(r"<updated>([^<]+)</updated>", entry)
            content = re.search(r"<content[^>]*>(.*?)</content>", entry, re.S)
            author = re.search(r"<name>([^<]+)</name>", entry)
            if not link:
                continue
            ts = updated.group(1)[:10] if updated else ""
            try:
                if ts and datetime.fromisoformat(ts).replace(tzinfo=timezone.utc) < cutoff:
                    continue
            except ValueError:
                pass
            out.append(Lead(source="reddit", uid=link.group(1).rstrip("/").split("/")[-2] if "/comments/" in link.group(1) else link.group(1),
                            title=title, url=link.group(1), body=strip_html(html.unescape(content.group(1)))[:1500] if content else "",
                            org=f"r/{sub}", date=ts, extra={"author": author.group(1) if author else ""}))
            n += 1
        log(f"reddit r/{sub}: {n}")
        time.sleep(2)
    return out


HN_QUERIES = ["\".NET\" kafka", "\".NET\" avro", "\".NET\" parquet", "\".NET\" iceberg", "c# \"data engineering\"",
              "cobol copybook", "ebcdic", "\"data masking\"", "\"pay transparency\"", "\"test data\" anonymization"]


def collect_hn(days: int, log) -> list[Lead]:
    start = int(since_date(days).timestamp())
    out, seen = [], set()
    for q in HN_QUERIES:
        url = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode({
            "query": q, "tags": "(story,comment,ask_hn)", "numericFilters": f"created_at_i>{start}", "hitsPerPage": 50})
        try:
            d = http_json(url)
        except Exception as e:  # noqa: BLE001
            log(f"hn '{q}': {e}")
            continue
        for h in d.get("hits", []):
            if h["objectID"] in seen:
                continue
            seen.add(h["objectID"])
            title = h.get("title") or h.get("story_title") or "(comment)"
            body = strip_html(h.get("story_text") or h.get("comment_text") or "")
            out.append(Lead(source="hn", uid=h["objectID"], title=title,
                            url=f"https://news.ycombinator.com/item?id={h['objectID']}", body=body[:1500],
                            org=h.get("author", ""), date=h.get("created_at", "")[:10], extra={"query": q}))
        log(f"hn '{q}': {len(d.get('hits', []))}")
    return out


USEME_CATEGORIES = [
    "https://useme.com/pl/jobs/category/programowanie-i-it,35/",
    "https://useme.com/pl/jobs/category/programowanie-i-it,35/oprogramowanie,100/",
    "https://useme.com/pl/jobs/category/programowanie-i-it,35/aplikacje-webowe,102/",
    "https://useme.com/pl/jobs/category/programowanie-i-it,35/projekty-it,103/",
    "https://useme.com/pl/jobs/category/prace-biurowe,40/bazy-danych,130/",
]


def collect_useme(days: int, log) -> list[Lead]:
    """Polish SME gig board. Public listing pages, polite single fetch per category."""
    out, seen = [], set()
    for cat in USEME_CATEGORIES:
        try:
            page = http(cat).decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            log(f"useme {cat}: {e}")
            continue
        for m in re.finditer(r'<a[^>]+href="(/pl/jobs/([a-z0-9-]+),(\d+)/)"[^>]*>([^<]{5,200})</a>(.*?)(?=<a[^>]+href="/pl/jobs/[a-z0-9-]+,\d+/"|$)', page, re.S):
            path, slug, jid, title, tail = m.groups()
            if jid in seen:
                continue
            seen.add(jid)
            desc = strip_html(tail)[:600]
            out.append(Lead(source="useme", uid=jid, title=html.unescape(title.strip()), url="https://useme.com" + path,
                            body=desc, org="useme", date=datetime.now(timezone.utc).strftime("%Y-%m-%d")))
        log(f"useme {cat.split('/')[-2]}: {len(seen)} total")
        time.sleep(2)
    return out


NFJ_QUERIES = ["Avro", "Kafka", "Databricks", "Snowflake", "Parquet", "Iceberg", "Delta Lake", "Spark",
               "Event Hubs", "Mainframe", "COBOL", "Big Data", "ETL"]
NFJ_DOTNET = {".net", "c#", "asp.net", "dotnet", ".net core", "entity framework", "blazor"}


def collect_nofluffjobs(days: int, log) -> list[Lead]:
    """Job ads = companies building with our stack right now. Public search API (PL/EU market)."""
    cutoff_ms = since_date(days).timestamp() * 1000
    out, seen = [], set()
    for q in NFJ_QUERIES:
        url = ("https://nofluffjobs.com/api/search/posting?pageTo=1&pageSize=100&withSalaryMatch=false"
               "&salaryCurrency=PLN&salaryPeriod=month&region=pl&language=en-US")
        postings = []
        for stack in (".NET", "C#"):
            try:
                d = http_json(url, method="POST", data={"criteriaSearch": {"requirement": [q, stack]}, "rawSearch": f"{q} {stack}"},
                              headers={"User-Agent": "Mozilla/5.0 (compatible; soltechnology-lead-radar)"})
                postings += d.get("postings", [])
            except Exception as e:  # noqa: BLE001
                log(f"nofluffjobs '{q} {stack}': {e}")
            time.sleep(0.7)
        n = 0
        for p in postings:
            dedupe = f"{p.get('title', '')}|{p.get('name', '')}".lower()
            if dedupe in seen or (p.get("posted") or 0) < cutoff_ms:
                continue
            tiles = [t["value"].lower() for t in p.get("tiles", {}).get("values", [])]
            seen.add(dedupe)
            loc = p.get("location", {})
            places = loc.get("places", [])
            country = (places[0].get("country", {}).get("code", "") if places else "")
            out.append(Lead(
                source="nofluffjobs", uid=p["id"], title=f"{p.get('title', '')} @ {p.get('name', '')}",
                url=f"https://nofluffjobs.com/job/{p.get('url', p['id'])}",
                body="hiring, requirements: " + ", ".join(tiles + [q.lower(), ".net"]), org=p.get("name", ""), country=country,
                date=datetime.fromtimestamp(p["posted"] / 1000, timezone.utc).strftime("%Y-%m-%d") if p.get("posted") else "",
                extra={"seniority": p.get("seniority"), "remote": loc.get("fullyRemote"), "query": q,
                       "salary": f"{p.get('salary', {}).get('from', '')}-{p.get('salary', {}).get('to', '')} {p.get('salary', {}).get('currency', '')}"},
            ))
            n += 1
        log(f"nofluffjobs '{q}' AND .NET/C#: {n} new of {len(postings)}")
    return out


COLLECTORS = {
    "ted": collect_ted,
    "github_issues": collect_github_issues,
    "github_dependents": collect_github_dependents,
    "stackexchange": collect_stackexchange,
    "reddit": collect_reddit,
    "hn": collect_hn,
    "useme": collect_useme,
    "nofluffjobs": collect_nofluffjobs,
}


# ----------------------------------------------------------------------------- scoring

DOTNET_SIGNAL = (".net", "c#", "dotnet", "csharp", "nuget", "asp.net", "f#", "entity framework", "blazor")
COMMUNITY_SOURCES = {"github_issues", "hn", "reddit", "stackexchange"}
POLISH_HINT = re.compile(r"[ąćęłńóśźż]", re.I)
NOISE = re.compile(r"daily hacker ?news|job radar|job posting|job finder|new job|who wants to be hired|resume|newsletter|digest \d|weekly links|awesome-", re.I)


def score_lead(lead: Lead, profile: dict) -> tuple[int, list[str]]:
    txt = lead.text()
    if NOISE.search(lead.title) or NOISE.search(lead.extra.get("repo", "")):
        return 0, []
    if profile.get("require_any") and not any(k in txt for k in profile["require_any"]):
        return 0, []
    for neg in profile.get("negative", []):
        if neg in txt:
            return 0, []
    # community posts must show .NET intent, otherwise we drown in Java/Python/Rust project issues
    if lead.source in COMMUNITY_SOURCES and profile.get("dotnet_required", True):
        repo = (lead.extra.get("repo") or "").lower()
        if not any(s in txt for s in DOTNET_SIGNAL) and not any(s in repo for s in ("dotnet", "csharp", "sharp", ".net")):
            return 0, []
    score, hits = 0, []
    for kw, w in profile["keywords"].items():
        c = txt.count(kw)
        if c:
            score += w * min(c, 3)
            hits.append(kw)
    # title hits count double
    for kw, w in profile["keywords"].items():
        if kw in lead.title.lower():
            score += w
    return score, hits


def apply_profiles(leads: list[Lead], profiles: dict, only_sources: set[str] | None) -> list[Lead]:
    out = []
    for lead in leads:
        best = None
        for name, p in profiles.items():
            if lead.source not in p["sources"]:
                continue
            if only_sources and lead.source not in only_sources:
                continue
            s, hits = score_lead(lead, p)
            if s >= p["min_score"] and (best is None or s > best[1]):
                best = (name, s, hits)
        if best:
            lead.profile, lead.score, lead.hits = best
            out.append(lead)
    return out


# ----------------------------------------------------------------------------- llm (optional)

LLM_PROMPT = """You help a solo .NET developer (author of AvroConvert, 5M NuGet downloads) find customers.
Product profile: {goal}
Lead (source {source}):
Title: {title}
Org/buyer: {org} {country}
Text: {body}

Return strict JSON: {{"score": 0-10 relevance as a sales lead for this profile, "reason": one sentence,
"opener": a 2-3 sentence first message in the lead's language (Polish if the lead is Polish, else English),
specific to their text, no flattery, ends with one concrete question}}"""


def llm_rate(lead: Lead, profile: dict, log) -> None:
    prompt = LLM_PROMPT.format(goal=profile["goal"], source=lead.source, title=lead.title, org=lead.org,
                               country=lead.country, body=lead.body[:1200])
    try:
        if os.environ.get("ANTHROPIC_API_KEY"):
            d = http_json("https://api.anthropic.com/v1/messages", method="POST",
                          headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
                          data={"model": os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"), "max_tokens": 400,
                                "messages": [{"role": "user", "content": prompt}]})
            text = d["content"][0]["text"]
        elif os.environ.get("OPENAI_API_KEY"):
            d = http_json("https://api.openai.com/v1/chat/completions", method="POST",
                          headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                          data={"model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), "temperature": 0.3,
                                "response_format": {"type": "json_object"},
                                "messages": [{"role": "user", "content": prompt}]})
            text = d["choices"][0]["message"]["content"]
        elif os.environ.get("GITHUB_MODELS_TOKEN") or os.environ.get("GITHUB_TOKEN"):
            # GitHub Models: free tier for any GitHub account, higher limits with Copilot; Actions GITHUB_TOKEN needs `models: read`
            tok = os.environ.get("GITHUB_MODELS_TOKEN") or os.environ["GITHUB_TOKEN"]
            d = http_json("https://models.github.ai/inference/chat/completions", method="POST",
                          headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"},
                          data={"model": os.environ.get("GITHUB_MODEL", "openai/gpt-4o-mini"), "temperature": 0.3,
                                "messages": [{"role": "user", "content": prompt}]})
            text = d["choices"][0]["message"]["content"]
        else:
            return
        m = re.search(r"\{.*\}", text, re.S)
        j = json.loads(m.group(0)) if m else {}
        lead.llm_score = int(j.get("score", 0))
        lead.llm_reason = str(j.get("reason", ""))[:300]
        lead.opener = str(j.get("opener", ""))[:800]
    except Exception as e:  # noqa: BLE001
        log(f"llm: {lead.key}: {e}")


# ----------------------------------------------------------------------------- state

def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE IF NOT EXISTS leads (
        key TEXT PRIMARY KEY, source TEXT, profile TEXT, score INT, llm_score INT, title TEXT, url TEXT,
        org TEXT, date TEXT, first_seen TEXT, status TEXT DEFAULT 'new', payload TEXT)""")
    return db


def remember(db: sqlite3.Connection, lead: Lead) -> bool:
    """Returns True if the lead is new."""
    cur = db.execute("SELECT 1 FROM leads WHERE key=?", (lead.key,))
    if cur.fetchone():
        return False
    db.execute("INSERT INTO leads(key,source,profile,score,llm_score,title,url,org,date,first_seen,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
               (lead.key, lead.source, lead.profile, lead.score, lead.llm_score, lead.title, lead.url, lead.org,
                lead.date, datetime.now(timezone.utc).isoformat(timespec="seconds"), json.dumps(asdict(lead), ensure_ascii=False)))
    return True


# ----------------------------------------------------------------------------- digest

def pick_opener(lead: Lead, p: dict) -> str:
    if lead.opener:
        return lead.opener
    if lead.source == "github_dependents" and p.get("opener_dependents"):
        tpl = p["opener_dependents"]
    else:
        polish = lead.source == "useme" or lead.country == "POL" or bool(POLISH_HINT.search(lead.title + lead.body[:300]))
        tpl = p.get("opener_pl" if polish else "opener_en") or p.get("opener_en") or p.get("opener", "")
    return tpl.format(topic=", ".join(lead.hits[:2]) or "this", title=lead.title[:80], org=lead.org)


def write_digest(path: Path, new: list[Lead], profiles: dict, stats: dict, days: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by = {}
    for l in new:
        by.setdefault(l.profile, []).append(l)
    lines = [f"# Lead radar – {datetime.now().date()} – last {days} days", ""]
    lines.append("Collected: " + ", ".join(f"{k} {v}" for k, v in stats.items()) + f". New matches: **{len(new)}**.")
    lines.append("")
    lines.append("Nothing was sent. Each entry has a draft opener to adapt and paste by hand.")
    lines.append("")
    for pname, p in profiles.items():
        items = by.get(pname, [])
        if not items:
            continue
        items.sort(key=lambda l: ((l.llm_score or 0), l.score), reverse=True)
        lines.append(f"## {p['title']} ({len(items)})")
        lines.append("")
        for l in items:
            badge = f"llm {l.llm_score}/10 · " if l.llm_score is not None else ""
            meta = " · ".join(x for x in [l.source, l.date, l.org, l.country, l.extra.get("value", ""), l.extra.get("salary", ""),
                                          f"deadline {l.deadline}" if l.deadline else ""] if x)
            lines.append(f"### [{l.title.strip()[:140]}]({l.url})")
            lines.append(f"{badge}score {l.score} ({', '.join(l.hits[:6])}) · {meta}")
            if l.body:
                lines.append("")
                lines.append("> " + l.body[:400].replace("\n", " "))
            if l.llm_reason:
                lines.append("")
                lines.append(f"_{l.llm_reason}_")
            opener = pick_opener(l, p)
            lines.append("")
            lines.append("**Draft:** " + opener)
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--profiles", default="", help="comma list; default all")
    ap.add_argument("--sources", default="", help="comma list; default all used by selected profiles")
    ap.add_argument("--llm", action="store_true", help="rate and draft with LLM (needs ANTHROPIC_API_KEY or OPENAI_API_KEY)")
    ap.add_argument("--llm-max", type=int, default=40, help="max leads to send to LLM per run")
    ap.add_argument("--out", default=str(ROOT / "digest"))
    ap.add_argument("--db", default=str(ROOT / "state" / "leads.sqlite"))
    ap.add_argument("--all", action="store_true", help="include already-seen leads in the digest")
    args = ap.parse_args()

    log = lambda m: print(m, file=sys.stderr)  # noqa: E731
    profiles = json.loads((ROOT / "profiles.json").read_text(encoding="utf-8"))
    if args.profiles:
        wanted = {p.strip() for p in args.profiles.split(",")}
        profiles = {k: v for k, v in profiles.items() if k in wanted}
    sources = {s for p in profiles.values() for s in p["sources"]}
    if args.sources:
        sources &= {s.strip() for s in args.sources.split(",")}

    raw, stats = [], {}
    for name in sorted(sources):
        try:
            got = COLLECTORS[name](args.days, log)
        except Exception as e:  # noqa: BLE001
            log(f"{name}: FAILED {e}")
            got = []
        stats[name] = len(got)
        raw.extend(got)

    matched = apply_profiles(raw, profiles, sources)
    log(f"matched {len(matched)} of {len(raw)}")

    db = open_db(Path(args.db))
    new = []
    for lead in matched:
        is_new = remember(db, lead)
        if is_new or args.all:
            new.append(lead)
    db.commit()

    if args.llm and new:
        new.sort(key=lambda l: l.score, reverse=True)
        for lead in new[: args.llm_max]:
            llm_rate(lead, profiles[lead.profile], log)
            db.execute("UPDATE leads SET llm_score=?, payload=? WHERE key=?",
                       (lead.llm_score, json.dumps(asdict(lead), ensure_ascii=False), lead.key))
        db.commit()

    out = Path(args.out) / f"{datetime.now().date()}.md"
    write_digest(out, new, profiles, stats, args.days)
    log(f"wrote {out} ({len(new)} new)")
    print(out)


if __name__ == "__main__":
    main()
