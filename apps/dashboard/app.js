// life-crm dashboard: overview of every timeline on one roadmap (with a 13-week zoom whose year
// strip can be dragged), a page per timeline, and a sidebar leading to the collection pages defined
// in the spreadsheet's Collections tab.
// All data comes from the inline #data JSON (built from the spreadsheet by apps/build.py).
// "Today" is computed here, so the page stays correct between builds.
// Testing aid: ?today=YYYY-MM-DD pretends the current date.
(() => {
  "use strict";

  const DATA = JSON.parse(document.getElementById("data").textContent);
  const app = document.getElementById("app");
  const NAMED_COLORS = new Set(["teal", "indigo", "amber", "blue", "pink", "green", "violet", "red", "orange", "gray"]);
  const DAY = 86400000, WEEK = 7 * DAY, ZOOM_WEEKS = 13;
  const ROW_H = 32, ITEM_H = 26, LANE_PAD = 7, GAP = 12;

  // ---------- dates ----------
  const iso = (s) => { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); };
  const midnight = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate());
  const qToday = new URLSearchParams(location.search).get("today");
  const TODAY = qToday && /^\d{4}-\d{2}-\d{2}$/.test(qToday) ? iso(qToday) : midnight(new Date());
  const daysBetween = (a, b) => Math.round((b - a) / DAY);
  const addDays = (x, n) => new Date(x.getFullYear(), x.getMonth(), x.getDate() + n);
  const addMonths = (x, n) => new Date(x.getFullYear(), x.getMonth() + n, 1);
  const monthOf = (x) => new Date(x.getFullYear(), x.getMonth(), 1);
  const mondayOf = (x) => addDays(midnight(x), -((x.getDay() + 6) % 7));
  const toIso = (x) => `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, "0")}-${String(x.getDate()).padStart(2, "0")}`;

  const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const MONTH = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const WEEKDAY = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  // A range is the time span a roadmap shows: whole months ("month") or whole weeks ("week").
  function makeRange(start, end, unit) {
    const pct = (date) => ((date - start) / (end - start)) * 100;
    const todayPct = pct(addDays(TODAY, 0.5));
    const months = (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth();
    return { start, end, unit, months, pct, todayPct, todayVisible: todayPct >= 0 && todayPct <= 100 };
  }
  const monthRange = (start, months) => makeRange(start, addMonths(start, months), "month");
  const weekRange = (start, weeks) => makeRange(start, addDays(start, 7 * weeks), "week");

  // Overview year: from Settings.window_start (default this month) for window_months.
  const YEAR = (() => {
    const ws = DATA.settings.window_start;
    const start = ws ? new Date(+ws.slice(0, 4), +ws.slice(5, 7) - 1, 1) : monthOf(TODAY);
    return monthRange(start, DATA.settings.window_months || 12);
  })();

  function rangeLabel(r) {
    if (r.unit === "week") {
      const last = addDays(r.end, -1);
      const y = (x) => (x.getFullYear() !== TODAY.getFullYear() || r.start.getFullYear() !== last.getFullYear() ? ` ${x.getFullYear()}` : "");
      return `${r.start.getDate()} ${MON[r.start.getMonth()]}${y(r.start)} – ${last.getDate()} ${MON[last.getMonth()]}${y(last)}`;
    }
    const last = addMonths(r.end, -1);
    return `${MONTH[r.start.getMonth()]} ${r.start.getFullYear()} – ${MONTH[last.getMonth()]} ${last.getFullYear()}`;
  }
  function fmtDate(s, approx) {
    const x = iso(s);
    if (approx) return `${MON[x.getMonth()]} ${x.getFullYear()}`;
    return `${MON[x.getMonth()]} ${x.getDate()}` + (x.getFullYear() !== TODAY.getFullYear() ? `, ${x.getFullYear()}` : "");
  }
  function fmtDue(s, approx) {
    if (approx) return fmtDate(s, true);
    const n = daysBetween(TODAY, iso(s));
    if (n < 0) return n === -1 ? "1 day late" : `${-n} days late`;
    if (n === 0) return "Today";
    if (n === 1) return "Tomorrow";
    if (n < 7) { const x = iso(s); return `${WD[x.getDay()]} ${x.getDate()}`; }
    return fmtDate(s, false);
  }
  function countdown(s) {
    const n = daysBetween(TODAY, iso(s));
    if (n < 14) return [n, n === 1 ? "day" : "days"];
    if (n < 70) return [Math.round(n / 7), "weeks"];
    return [Math.max(2, Math.round(n / 30.44)), "months"];
  }
  const relTime = (stamp) => {
    const mins = Math.round((Date.now() - new Date(stamp)) / 60000);
    if (mins < 2) return "just now";
    if (mins < 90) return `${mins} min ago`;
    const hrs = Math.round(mins / 60);
    return hrs < 36 ? `${hrs} h ago` : `${Math.round(hrs / 24)} days ago`;
  };

  // ---------- data helpers ----------
  const timelines = DATA.timelines;
  const byId = new Map(timelines.map((t) => [t.id, t]));
  const steps = DATA.steps.map((s, i) => ({ ...s, i }));
  const stepsOf = (tid) => steps.filter((s) => s.timeline === tid);
  const keyDate = (s) => s.date || s.start || null; // when it starts/happens: sorting and "next"
  // when it is due: a period that already started is due at its end
  const dueDate = (s) => (s.kind === "period" && s.start ? (iso(s.start) > TODAY ? s.start : s.end) : s.date || null);
  const endDate = (s) => s.end || s.date || s.start || null; // when it finished
  const isDated = (s) => !!keyDate(s);
  const isOpen = (s) => s.status !== "done";
  const byDue = (a, b) => (dueDate(a) < dueDate(b) ? -1 : dueDate(a) > dueDate(b) ? 1 : a.i - b.i);
  const nextStep = (tid) => stepsOf(tid).filter((s) => isOpen(s) && dueDate(s)).sort(byDue)[0] || null;
  const doneCount = (tid) => { const all = stepsOf(tid); return [all.filter((s) => s.status === "done").length, all.length]; };
  const undatedOpen = (items) => items.filter((s) => isOpen(s) && !isDated(s));

  function colorProps(t) {
    if (NAMED_COLORS.has(t.color)) return { class: `c-${t.color}` };
    const hex = /^#?[0-9a-f]{6}$/i.test(t.color) ? (t.color[0] === "#" ? t.color : `#${t.color}`) : null;
    return hex ? { style: `--c:${hex}` } : { class: "c-gray" };
  }

  // ---------- view state ----------
  const store = {
    get(key, fallback) { try { const v = localStorage.getItem(key); return v == null ? fallback : JSON.parse(v); } catch { return fallback; } },
    set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* private mode */ } },
  };
  const hidden = new Set(store.get("lifecrm.hidden", []));
  const visibleTimelines = () => timelines.filter((t) => !hidden.has(t.id));
  let zoom = store.get("lifecrm.zoom", "year") === "weeks" ? "weeks" : "year";
  let weekShift = 0; // weeks from the current week; not saved, every visit starts at today

  // 13-week range inside a context range (the year strip), clamped so the frame stays inside it.
  function weeksIn(ctx) {
    const base = mondayOf(TODAY);
    const lo = Math.ceil((mondayOf(ctx.start) - base) / WEEK);
    const hi = Math.floor((ctx.end - base) / WEEK) - ZOOM_WEEKS;
    weekShift = hi < lo ? lo : Math.min(hi, Math.max(lo, weekShift));
    return weekRange(addDays(base, 7 * weekShift), ZOOM_WEEKS);
  }

  // ---------- DOM ----------
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === "class") el.className = [el.className, v].filter(Boolean).join(" ");
      else if (k === "style") el.style.cssText += ";" + v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids.flat(Infinity)) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : String(kid));
    return el;
  }
  const withColor = (t, attrs = {}) => {
    const c = colorProps(t);
    return { ...attrs, class: [attrs.class, c.class].filter(Boolean).join(" "), style: [attrs.style, c.style].filter(Boolean).join(";") };
  };
  const dot = () => h("span", { class: "dot" });
  const go = (tid) => { location.hash = tid ? `t/${encodeURIComponent(tid)}` : ""; };
  // Links to the spreadsheet only appear when Settings.sheet_url is set.
  const sheetLink = (label, cls = "btn") => (DATA.sheet_url ? h("a", { class: cls, href: DATA.sheet_url, target: "_blank", rel: "noopener" }, label) : null);

  const AVATAR_COLORS = ["#1f5f5b", "#111827", "#c2410c", "#0369a1", "#6d28d9", "#be185d", "#15803d", "#9a3412"];
  function avatar(owner) {
    if (!owner) return null;
    const initials = owner.split(/\s+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
    let hash = 0;
    for (const ch of owner.toLowerCase()) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
    return h("span", { class: "av", style: `background:${AVATAR_COLORS[hash % AVATAR_COLORS.length]}`, title: owner }, initials);
  }

  // ---------- tooltip ----------
  let tipEl = null;
  function describe(s) {
    const when = s.kind === "period" && s.start
      ? `${fmtDate(s.start, s.approx)} – ${fmtDate(s.end, s.approx)}`
      : s.date ? fmtDate(s.date, s.approx) : "No date yet";
    const status = { todo: "To do", doing: "In progress", done: "Done", "to book": "To book", waiting: "Waiting", stuck: "Stuck" }[s.status];
    return [s.title, [when, status, s.owner].filter(Boolean).join(" · "), s.notes];
  }
  function showTip(ev, lines) {
    hideTip();
    const [title, ...rest] = lines;
    tipEl = h("div", { class: "tip", role: "tooltip" }, h("b", {}, title), rest.filter(Boolean).map((l) => h("span", {}, l)));
    document.body.append(tipEl);
    const r = ev.currentTarget.getBoundingClientRect();
    const tw = tipEl.offsetWidth, th = tipEl.offsetHeight;
    tipEl.style.left = `${Math.max(8, Math.min(window.innerWidth - tw - 8, r.left))}px`;
    tipEl.style.top = `${r.top - th - 8 > 8 ? r.top - th - 8 : r.bottom + 8}px`;
  }
  function hideTip() { if (tipEl) { tipEl.remove(); tipEl = null; } }
  window.addEventListener("scroll", hideTip, { passive: true });
  const stepTip = (s) => { const [title, meta, notes] = describe(s); return [title, `${byId.get(s.timeline).name} · ${meta}`, notes]; };

  // ---------- text measuring for label placement ----------
  const ctx2d = document.createElement("canvas").getContext("2d");
  const FONT_FAMILY = getComputedStyle(document.body).fontFamily;
  const textW = (s, weight) => { ctx2d.font = `${weight} 12px ${FONT_FAMILY}`; return Math.ceil(ctx2d.measureText(s).width); };

  // ---------- roadmap engine ----------
  // lanes: { t, items, label, onLabel?, empty? } | { type: "group", text } | { type: "phase", bands: [{ text, from, to, t }] }
  // undated: how open steps without a date appear, just after the today line:
  //   "count" = one dashed pill per lane ("3 to schedule"), "each" = one dashed pill per step.
  function roadmap({ lanes, range, onItem, onUndated, undated = "count", addRow = null }) {
    const wk = range.unit === "week";
    const rm = h("div", {
      class: `rm${wk ? " wk" : ""}${range.todayVisible ? "" : " no-today"}`,
      style: `--now:${range.todayPct}%` + (range.months > 12 && !wk ? `;min-width:calc(var(--lab) + ${range.months * 74}px)` : ""),
    });
    const scroll = h("div", { class: "rm-scroll" }, rm);

    // header: months (year view) or months + week start days (13-week view)
    const headTrk = h("div", { class: "rm-trk" });
    if (wk) {
      for (let m = monthOf(range.start); m < range.end; m = addMonths(m, 1)) {
        const x = Math.max(0, range.pct(m));
        if (x > 90 || (x === 0 && range.pct(addMonths(m, 1)) < 8)) continue; // no room for the label
        headTrk.append(h("span", { class: "rm-m y", style: `left:${x}%` }, `${MONTH[m.getMonth()]}${m.getMonth() === 0 ? ` ${m.getFullYear()}` : ""}`));
      }
      for (let d = range.start; d < range.end; d = addDays(d, 7)) headTrk.append(h("span", { class: "rm-d", style: `left:${range.pct(d)}%` }, d.getDate()));
    } else {
      for (let i = 0; i < range.months; i++) {
        const m = addMonths(range.start, i);
        const jan = m.getMonth() === 0;
        headTrk.append(h("span", { class: `rm-m${i === 0 || jan ? " y" : ""}`, style: `left:${range.pct(m)}%` },
          jan ? `${MON[0]} '${String(m.getFullYear()).slice(2)}` : MON[m.getMonth()]));
      }
    }
    headTrk.append(h("span", { class: "rm-todaytag" }, "TODAY"));
    rm.append(h("div", { class: "rm-row rm-head" }, h("div", { class: "rm-lab" }, wk ? h("small", { class: "rm-wkof" }, "Week of") : null), headTrk));

    const gridDates = [];
    if (wk) for (let d = addDays(range.start, 7); d < range.end; d = addDays(d, 7)) gridDates.push(d);
    else for (let i = 1; i < range.months; i++) gridDates.push(addMonths(range.start, i));

    const laid = [];
    for (const lane of lanes) {
      if (lane.type === "group") {
        rm.append(h("div", { class: "rm-row rm-group" }, h("div", { class: "rm-lab" }, lane.text), h("div", { class: "rm-trk" })));
        continue;
      }
      if (lane.type === "phase") {
        const trk = h("div", { class: "rm-trk" });
        for (const b of lane.bands) {
          const l = Math.max(0, range.pct(b.from)), r = Math.min(100, range.pct(b.to));
          if (r > l) trk.append(h("span", withColor(b.t, { class: "phase", style: `left:${l}%;width:${r - l}%`, title: b.text }), b.text));
        }
        rm.append(h("div", { class: "rm-row rm-phase" }, h("div", { class: "rm-lab" }, "Phase"), trk));
        continue;
      }
      const trk = h("div", { class: "rm-trk" });
      const lab = lane.onLabel
        ? h("button", { class: "rm-lab", type: "button", onclick: lane.onLabel }, lane.label)
        : h("div", { class: "rm-lab" }, lane.label);
      rm.append(h("div", withColor(lane.t, { class: "rm-row rm-lane" }), lab, trk));
      laid.push({ lane, trk, lab });
    }
    if (addRow) rm.append(addRow);

    let scrolled = false;
    function layout() {
      const W = headTrk.clientWidth;
      if (!W) return;
      const todayX = (range.todayPct / 100) * W;
      for (const { lane, trk, lab } of laid) {
        trk.replaceChildren();
        const placed = [];
        let before = 0, after = 0;
        for (const s of lane.items) {
          if (!isDated(s)) continue;
          const g = geometry(s, W, range);
          if (g) placed.push({ s, ...g });
          else (endDate(s) < toIso(range.start) ? before++ : after++);
        }
        // open steps without a date: dashed pills chained after the today line
        const pending = undatedOpen(lane.items);
        if (pending.length && range.todayVisible) {
          const pills = undated === "each"
            ? pending.map((s) => ({ text: s.title, steps: [s], book: s.status === "to book" }))
            : [{ text: pending.every((s) => s.status === "to book") ? `${pending.length} to book` : `${pending.length} to schedule`,
              steps: pending, book: pending.every((s) => s.status === "to book") }];
          // they share a zone just after today and wrap onto new rows, so their position never reads as a date
          const x0 = Math.min(todayX + 8, W - 40), zoneEnd = Math.min(W, x0 + Math.max(280, W * 0.24));
          let x = x0;
          for (const p of pills) {
            const w = Math.min(textW(p.text, 600) + 24, 240, W - x0); // long titles get an ellipsis; full text in the hover box
            if (x + w > zoneEnd && x > x0) x = x0;
            placed.push({ type: "todo", pill: p, x, w, x0: x, x1: x + w });
            x += w + GAP; // same gap the row packing uses, so a chain stays on one row
          }
        }
        // greedy interval packing: first row whose last extent ends before this one starts
        placed.sort((a, b) => a.x0 - b.x0);
        const rowEnds = [];
        for (const p of placed) {
          let r = rowEnds.findIndex((end) => end + GAP <= p.x0);
          if (r === -1) { r = rowEnds.length; rowEnds.push(p.x1); } else rowEnds[r] = p.x1;
          p.row = r;
        }
        const rows = Math.max(1, rowEnds.length);
        const height = Math.max(48, rows * ROW_H + LANE_PAD * 2 - (ROW_H - ITEM_H));
        trk.style.height = lab.style.height = `${height}px`;
        for (const d of gridDates) trk.append(h("span", { class: `rm-gridline${wk && d.getDate() <= 7 ? " mo" : ""}`, style: `left:${range.pct(d)}%` }));
        if (range.todayVisible) trk.append(h("span", { class: "rm-nowline", style: `left:${range.todayPct}%` }));
        const offsetTop = rows === 1 ? (height - ITEM_H) / 2 : LANE_PAD;
        for (const p of placed) trk.append(p.type === "todo"
          ? drawPill(p, offsetTop + p.row * ROW_H, lane.t, onUndated || onItem)
          : drawItem(p, offsetTop + p.row * ROW_H, onItem));
        if (!placed.length) {
          const outside = [before && `${before} earlier`, after && `${after} later`].filter(Boolean).join(", ");
          trk.append(h("span", { class: "rm-empty", style: range.todayVisible && range.todayPct < 70 ? `left:calc(${range.todayPct}% + 10px)` : null },
            outside ? `Nothing in these ${wk ? "weeks" : "months"} · ${outside}` : lane.empty || "No steps yet"));
        }
      }
      // a range wider than the screen opens with today near the left edge
      if (!scrolled && range.todayVisible && scroll.scrollWidth > scroll.clientWidth) {
        scroll.scrollLeft = Math.max(0, todayX - (scroll.clientWidth - headTrk.offsetLeft) * 0.2);
        scrolled = true;
      }
    }
    return { el: scroll, layout };
  }

  function geometry(s, W, range) {
    const t = byId.get(s.timeline);
    if (s.kind === "period" && s.start && s.end) {
      const a = range.pct(iso(s.start)), b = range.pct(addDays(iso(s.end), 1));
      if (b <= 0 || a >= 100) return null;
      const x0 = (Math.max(0, a) / 100) * W, x1 = (Math.min(100, b) / 100) * W;
      const w = Math.max(8, x1 - x0);
      const tw = textW(s.title, 650);
      let label = "in", e0 = x0, e1 = x0 + w;
      if (tw + 20 > w) {
        if (x0 + w + 8 + tw <= W) { label = "right"; e1 = x0 + w + 8 + tw; }
        else if (x0 - 8 - tw >= 0) { label = "left"; e0 = x0 - 8 - tw; }
      }
      return { t, type: "bar", x: x0, w, cutL: a < 0, cutR: b > 100, label, tw, x0: e0, x1: e1 };
    }
    if (!s.date) return null;
    const p = range.pct(addDays(iso(s.date), 0.5));
    if (p < 0 || p > 100) return null;
    // Keep the diamond (rotated, with its white ring) fully inside the lane for dates at the very
    // start or end of the window.
    const x = Math.min(Math.max((p / 100) * W, 16), W - 16);
    const tw = textW(s.title, 700) + 7 + 14;
    if (x + tw - 7 <= W) return { t, type: "ms", x, side: "right", tw, x0: x - 7, x1: x - 7 + tw };
    return { t, type: "ms", x, side: "left", tw, x0: x + 7 - tw, x1: x + 7 };
  }

  const interactive = (tipLines, act) => ({
    tabindex: "0",
    onmouseenter: (ev) => showTip(ev, tipLines), onmouseleave: hideTip, onfocus: (ev) => showTip(ev, tipLines), onblur: hideTip,
    onclick: () => { hideTip(); act(); },
    onkeydown: (ev) => { if (ev.key === "Enter") { hideTip(); act(); } },
  });

  function drawItem(p, top, onItem) {
    const s = p.s;
    const common = (attrs) => withColor(p.t, { ...attrs, ...interactive(stepTip(s), () => onItem && onItem(s)) });
    if (p.type === "bar") {
      const late = isOpen(s) && iso(s.end) < TODAY;
      const bar = h("div", common({
        class: `it bar${p.cutL ? " cut-l" : ""}${p.cutR ? " cut-r" : ""}${s.status === "done" ? " done" : ""}`,
        style: `left:${p.x}px;width:${p.w}px;top:${top}px${late ? ";--c:var(--amber)" : ""}`,
      }));
      if (s.progress != null) bar.append(h("span", { class: "pct", style: `width:${s.progress}%` }));
      if (p.label === "in") { bar.append(h("span", {}, s.title)); return bar; }
      const frag = document.createDocumentFragment();
      frag.append(bar, h("div", common({
        class: "it blabel",
        style: `top:${top}px;` + (p.label === "right" ? `left:${p.x + p.w + 8}px` : `left:${p.x - 8 - p.tw}px`),
      }), s.title));
      return frag;
    }
    const late = isOpen(s) && iso(s.date) < TODAY;
    const cls = s.status === "done" ? " done" : s.status === "to book" ? " open" : late ? " late" : "";
    return h("div", common({
      class: `it ms${s.kind === "task" ? " task" : ""}${cls}${p.side === "left" ? " left" : ""}`,
      style: `top:${top}px;` + (p.side === "right" ? `left:${p.x - 7}px` : `left:${p.x + 7 - p.tw}px;width:${p.tw}px`),
    }), h("i"), s.title);
  }

  function drawPill(p, top, t, act) {
    const { pill } = p;
    const lines = pill.steps.length === 1
      ? [...stepTip(pill.steps[0]).slice(0, 1), "No date yet: add one in the spreadsheet", pill.steps[0].notes]
      : [pill.text, ...pill.steps.slice(0, 8).map((s) => `· ${s.title}`), pill.steps.length > 8 ? `+ ${pill.steps.length - 8} more` : ""];
    return h("div", withColor(t, {
      class: `it undated${pill.book ? " book" : ""}`, style: `left:${p.x}px;width:${p.w}px;top:${top}px`,
      ...interactive(lines, () => act && act(pill.steps[0])),
    }), pill.text);
  }

  // ---------- year strip with draggable 13-week frame ----------
  // ctx: month range of the strip; rows: [{ t, dim }]; frame: week range or null.
  function yearStrip({ ctx, rows, frame, onRowClick }) {
    const body = h("div", { class: "mini-rows" });
    for (const { t, dim } of rows) {
      const row = h("div", withColor(t, { class: `mini-row${dim ? " dim" : ""}`, title: t.name, onclick: frame ? null : () => onRowClick && onRowClick(t) }));
      for (const s of stepsOf(t.id)) {
        if (s.kind === "period" && s.start) {
          const a = Math.max(0, ctx.pct(iso(s.start))), b = Math.min(100, ctx.pct(addDays(iso(s.end), 1)));
          if (b > a) row.append(h("i", { style: `left:${a}%;width:${b - a}%` }));
        } else if (s.date) {
          const p = ctx.pct(addDays(iso(s.date), 0.5));
          if (p >= 0 && p <= 100) row.append(h("i", { class: "pt", style: `left:${p}%` }));
        }
      }
      body.append(row);
    }
    if (ctx.todayVisible) body.append(h("div", { class: "mini-today", style: `left:${ctx.todayPct}%` }));

    const months = h("div", { class: "mini-months", style: `grid-template-columns:repeat(${ctx.months},1fr)` });
    const every = ctx.months > 18 ? 3 : ctx.months > 13 ? 2 : 1;
    for (let i = 0; i < ctx.months; i++) {
      const m = addMonths(ctx.start, i);
      months.append(h("span", {}, i % every ? "" : m.getMonth() === 0 || i === 0 ? `${MON[m.getMonth()]} '${String(m.getFullYear()).slice(2)}` : MON[m.getMonth()]));
    }
    const wrap = h("div", { class: `mini${frame ? " has-frame" : ""}` }, body, months);
    if (!frame) return wrap;

    const left = Math.max(0, ctx.pct(frame.start)), width = Math.min(100, ctx.pct(frame.end)) - left;
    const brush = h("div", { class: "brush", style: `left:${left}%;width:${width}%`, title: "Drag to move through the year" });
    body.append(brush); // inside the rows box, so its % positions match the bars
    // Dragging previews the frame; releasing snaps to whole weeks and re-renders.
    const span = ctx.end - ctx.start, frameMs = ZOOM_WEEKS * WEEK;
    let grab = null;
    const dateAt = (clientX) => {
      const r = body.getBoundingClientRect();
      return new Date(+ctx.start + Math.max(0, Math.min(1, (clientX - r.left) / r.width)) * span);
    };
    const place = (startMs) => {
      const clamped = Math.max(+ctx.start - 6 * DAY, Math.min(+ctx.end - frameMs, startMs));
      brush.style.left = `${((clamped - ctx.start) / span) * 100}%`;
      return clamped;
    };
    let pendingStart = +frame.start;
    wrap.addEventListener("pointerdown", (ev) => {
      if (ev.button !== 0) return;
      const at = +dateAt(ev.clientX);
      const onBrush = ev.target === brush;
      grab = onBrush ? at - +frame.start : frameMs / 2;
      pendingStart = place(at - grab);
      wrap.setPointerCapture(ev.pointerId);
      wrap.classList.add("dragging");
      ev.preventDefault();
    });
    wrap.addEventListener("pointermove", (ev) => { if (grab != null) pendingStart = place(+dateAt(ev.clientX) - grab); });
    const release = () => {
      if (grab == null) return;
      grab = null;
      wrap.classList.remove("dragging");
      weekShift = Math.round((pendingStart - mondayOf(TODAY)) / WEEK);
      render();
    };
    wrap.addEventListener("pointerup", release);
    wrap.addEventListener("pointercancel", release);
    return wrap;
  }

  // ---------- zoom controls ----------
  function zoomTools() {
    const set = (z) => () => { zoom = z; weekShift = 0; store.set("lifecrm.zoom", z); render(); };
    const seg = h("span", { class: "seg", role: "group", "aria-label": "Zoom" },
      // The overview spans window_months (12 by default): call it "Year" only when it is one.
      h("button", { type: "button", class: zoom === "year" ? "on" : "", onclick: set("year") },
        (DATA.settings.window_months || 12) === 12 ? "Year" : `${DATA.settings.window_months} months`),
      h("button", { type: "button", class: zoom === "weeks" ? "on" : "", onclick: set("weeks") }, "13 weeks"));
    if (zoom !== "weeks") return [seg];
    const move = (n) => () => { weekShift += n; render(); };
    return [
      h("span", { class: "nav" },
        h("button", { type: "button", class: "arrow", title: "4 weeks back", onclick: move(-4) }, "‹"),
        h("button", { type: "button", class: "btn", onclick: () => { weekShift = 0; render(); } }, "Today"),
        h("button", { type: "button", class: "arrow", title: "4 weeks ahead", onclick: move(4) }, "›")),
      seg,
    ];
  }

  // ---------- shared bits ----------
  function warningsBox() {
    if (!DATA.warnings.length) return null;
    return h("details", { class: "warn" },
      h("summary", {}, `${DATA.warnings.length} row${DATA.warnings.length > 1 ? "s" : ""} in the spreadsheet need fixing`),
      h("ul", {}, DATA.warnings.map((w) => h("li", {}, w))));
  }
  function footer() {
    return h("div", { class: "foot" },
      h("span", {}, "Data: ", DATA.sheet_url ? h("a", { href: DATA.sheet_url, target: "_blank", rel: "noopener" }, "your spreadsheet") : "your spreadsheet",
        ` · last change ${relTime(DATA.synced_at)}`),
      h("span", {}, "Change the spreadsheet; this page follows at the next update"));
  }
  const todayText = () => `today is ${WEEKDAY[TODAY.getDay()]}, ${TODAY.getDate()} ${MONTH[TODAY.getMonth()]}`;

  // Focus range: from the timeline's first date (or this month) to its last date (at least 3 months
  // ahead), at most 30 months, keeping the most recent part when it is longer.
  function rangeFor(items) {
    const dates = items.flatMap((s) => [s.start, s.end, s.date]).filter(Boolean).sort();
    if (!dates.length) return YEAR;
    const first = iso(dates[0]), last = iso(dates[dates.length - 1]);
    let start = new Date(Math.min(monthOf(TODAY), monthOf(first)));
    const end = new Date(Math.max(addMonths(TODAY, 4), addMonths(last, 1)));
    let months = (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth();
    if (months > 30) { start = addMonths(end, -30); months = 30; }
    return monthRange(start, months);
  }

  // ---------- overview (C1) ----------
  function overview() {
    const vis = visibleTimelines();
    const range = zoom === "weeks" ? weeksIn(YEAR) : YEAR;
    const top = h("div", { class: "top" },
      h("div", {}, h("h1", {}, zoom === "weeks" ? "Next weeks" : DATA.title),
        h("p", {}, `${rangeLabel(range)} · ${todayText()}`)),
      h("div", { class: "tools" }, zoomTools(), sheetLink("Edit roadmap ↗"), sheetLink("＋ New timeline", "btn dark")));

    // countdown cards: pinned upcoming first, then the next dated ones
    const upcoming = steps.filter((s) => isOpen(s) && s.date && iso(s.date) >= TODAY && !hidden.has(s.timeline)).sort(byDue);
    const picks = [...upcoming.filter((s) => s.pin), ...upcoming.filter((s) => !s.pin)].slice(0, 4).sort(byDue);
    const keys = picks.length ? h("div", { class: "keys" }, picks.map((s) => {
      const [n, unit] = countdown(s.date);
      return h("button", withColor(byId.get(s.timeline), { class: "key", type: "button", onclick: () => go(s.timeline) }),
        h("span", { class: "key-n" }, h("b", {}, n), h("small", {}, unit)),
        h("span", { class: "key-t" }, h("strong", {}, s.title), h("span", {}, `${s.kind === "milestone" ? "" : "Due "}${fmtDate(s.date, s.approx)} · ${byId.get(s.timeline).name}`)));
    })) : null;

    const filters = h("div", { class: "filters" }, h("span", { class: "lbl" }, "Show:"), timelines.map((t) =>
      h("button", withColor(t, {
        class: "chip", type: "button", "aria-pressed": String(!hidden.has(t.id)),
        onclick: () => { hidden.has(t.id) ? hidden.delete(t.id) : hidden.add(t.id); store.set("lifecrm.hidden", [...hidden]); render(); },
      }), dot(), t.name)));

    const strip = zoom === "weeks"
      ? [h("div", { class: "mini-h" }, h("span", {}, "The whole roadmap · drag the frame"), h("span", {}, rangeLabel(YEAR))),
        yearStrip({ ctx: YEAR, rows: vis.map((t) => ({ t, dim: false })), frame: range })]
      : null;

    // lanes, grouped in timeline order
    const lanes = [];
    let group = null;
    // No heading when every lane sits in one group (e.g. none set, so all are "Other").
    const oneGroup = new Set(vis.map((t) => t.group)).size === 1;
    for (const t of vis) {
      if (t.group !== group) { group = t.group; if (!oneGroup) lanes.push({ type: "group", text: group }); }
      lanes.push({
        t, items: stepsOf(t.id),
        label: [dot(), h("span", { class: "rm-name" }, t.name, t.goal ? h("small", {}, t.goal) : null)],
        onLabel: () => go(t.id),
      });
    }
    const add = h(DATA.sheet_url ? "a" : "div", { class: "rm-add", href: DATA.sheet_url || null, target: DATA.sheet_url ? "_blank" : null, rel: "noopener" }, h("b", {}, "＋"),
      "New timeline: add a row to the Timelines tab of the spreadsheet (a trip, a course, an exam…)");
    const rmap = roadmap({ lanes, range, onItem: (s) => go(s.timeline), undated: zoom === "weeks" ? "each" : "count", addRow: add });

    // cards
    const weekEnd = addDays(TODAY, 7);
    const dueSoon = steps.filter((s) => isOpen(s) && !hidden.has(s.timeline) && dueDate(s) && iso(dueDate(s)) <= weekEnd).sort(byDue);
    const toBook = steps.filter((s) => s.status === "to book" && !isDated(s) && !hidden.has(s.timeline));
    const weekItems = [...dueSoon, ...toBook];
    const li = (s, right, hot) => h("li", withColor(byId.get(s.timeline), { class: "click", onclick: () => go(s.timeline) }),
      dot(), h("span", {}, s.title), h("span", { class: `w${hot ? " hot" : ""}` }, right));
    const week = h("div", { class: "card" }, h("h3", {}, "This week, all timelines"),
      weekItems.length ? h("ul", { class: "list" }, weekItems.slice(0, 8).map((s) => {
        const due = dueDate(s);
        if (!due) return li(s, "to book", false);
        const label = s.kind === "period" && iso(s.start) <= TODAY ? `ends ${fmtDue(due, s.approx)}` : fmtDue(due, s.approx);
        return li(s, label, daysBetween(TODAY, iso(due)) <= 1);
      })) : h("p", { class: "none" }, "Nothing due in the next 7 days."),
      weekItems.length > 8 ? h("p", { class: "none" }, `+ ${weekItems.length - 8} more`) : null);

    const progress = h("div", { class: "card" }, h("h3", {}, "Progress by timeline"),
      h("div", { class: "prog" }, vis.filter((t) => doneCount(t.id)[1] > 0).map((t) => {
        const [d, n] = doneCount(t.id);
        return [h("span", { onclick: () => go(t.id) }, t.name), h("span", withColor(t, { class: "pbar" }), h("i", { style: `width:${(d / n) * 100}%` })), h("span", {}, `${d}/${n}`)];
      })));

    const doneItems = steps.filter((s) => s.status === "done" && !hidden.has(s.timeline))
      .sort((a, b) => ((endDate(b) || "") < (endDate(a) || "") ? -1 : 1)).slice(0, 5);
    const recent = h("div", { class: "card" }, h("h3", {}, "Recently done"),
      doneItems.length ? h("ul", { class: "list" }, doneItems.map((s) => li(s, endDate(s) ? fmtDate(endDate(s), s.approx) : "", false)))
        : h("p", { class: "none" }, "Nothing marked done yet."));

    const unscheduled = vis.map((t) => [t, undatedOpen(stepsOf(t.id)).filter((s) => s.status !== "to book")]).filter(([, l]) => l.length);
    const toSchedule = unscheduled.length ? h("div", { class: "card", style: "margin-top:16px" },
      h("h3", {}, `To schedule · ${unscheduled.reduce((n, [, l]) => n + l.length, 0)} steps without a date`, sheetLink("Add dates ↗", "")),
      h("div", { style: "columns: 3 240px; column-gap: 28px" }, unscheduled.map(([t, l]) =>
        h("div", { style: "break-inside: avoid; margin-bottom: 10px" },
          h("ul", { class: "list" }, l.map((s) => h("li", withColor(t, { class: "click", onclick: () => go(t.id) }),
            dot(), h("span", {}, s.title), h("span", { class: "w" }, t.name)))))))) : null;

    const panel = h("div", { class: "panel ov" }, top, keys, filters, strip, rmap.el,
      h("div", { class: "row3" }, week, progress, recent), toSchedule, warningsBox(), footer());
    return { el: h("div", { class: "page" }, panel), layout: rmap.layout };
  }

  // ---------- timeline focus (C2) ----------
  function focus(tid) {
    const t = byId.get(tid);
    const own = stepsOf(tid);
    const span = rangeFor(own);
    const range = zoom === "weeks" ? weeksIn(span) : span;

    const mini = [
      h("div", { class: "mini-h" }, h("span", {}, zoom === "weeks" ? "Whole span · drag the frame" : "Whole span"), h("span", {}, rangeLabel(span))),
      yearStrip({ ctx: span, rows: timelines.map((x) => ({ t: x, dim: x.id !== tid })), frame: zoom === "weeks" ? range : null, onRowClick: (x) => go(x.id) }),
    ];

    const title = h("div", withColor(t, { class: "ftitle" }),
      h("div", {}, h("small", {}, dot(), t.name), h("h1", {}, t.goal || t.name), t.description ? h("p", {}, t.description) : null),
      h("div", { class: "tools" }, zoomTools(),
        t.drive_link ? h("a", { class: "btn", href: t.drive_link, target: "_blank", rel: "noopener" }, "Open in Drive ↗") : null,
        sheetLink("＋ Add step", "btn dark")));

    // lanes per track, optional phase band
    const tracks = [...new Set(own.map((s) => s.track))];
    const lanes = [];
    const bands = [...new Set(own.filter((s) => s.phase).map((s) => s.phase))].map((name) => {
      const ds = own.filter((s) => s.phase === name).flatMap((s) => [s.start, s.end, s.date]).filter(Boolean).sort();
      return ds.length ? { text: name, from: iso(ds[0]), to: addDays(iso(ds[ds.length - 1]), 1), t } : null;
    }).filter(Boolean);
    if (bands.length) lanes.push({ type: "phase", bands });
    for (const tr of tracks) {
      const items = own.filter((s) => s.track === tr);
      lanes.push({ t, items, label: [dot(), h("span", { class: "rm-name" }, tr, h("small", {}, `${items.length} step${items.length > 1 ? "s" : ""}`))] });
    }
    const highlight = (s) => {
      const row = document.getElementById(`step-${s.i}`);
      if (!row) return;
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      row.animate([{ background: "var(--t)" }, { background: "transparent" }], { duration: 1600 });
    };
    const rmap = roadmap({ lanes, range, onItem: highlight, undated: "each" });

    // step list: open steps by due date, then undated open, then done (most recent first)
    const open = own.filter(isOpen);
    const list = [
      ...open.filter((s) => dueDate(s)).sort(byDue),
      ...open.filter((s) => !dueDate(s)),
      ...own.filter((s) => !isOpen(s)).sort((a, b) => ((endDate(b) || "") < (endDate(a) || "") ? -1 : 1)),
    ];
    let num = 0;
    const stepCard = h("div", withColor(t, { class: "card" }), h("h3", {}, `Steps · ${doneCount(tid)[0]} of ${own.length} done`, sheetLink("Edit ↗", "")),
      list.length ? h("ol", { class: "steps" }, list.map((s) => {
        const kd = keyDate(s), due = dueDate(s);
        const late = due && isOpen(s) && iso(due) < TODAY;
        const when = !kd ? "no date"
          : s.kind === "period" ? `${fmtDate(s.start, s.approx)} – ${fmtDate(s.end, s.approx)}`
          : s.status === "done" ? fmtDate(kd, s.approx) : fmtDue(kd, s.approx);
        return h("li", { class: s.status === "to book" || s.status === "waiting" || s.status === "stuck" ? "todo" : s.status, id: `step-${s.i}` },
          h("span", { class: "n" }, s.status === "done" ? "✓" : ++num),
          h("span", { class: "s-b" },
            h("span", { class: "s-t" }, s.title,
              s.status === "doing" ? h("span", { class: "s-tag" }, "in progress") : null,
              s.status === "to book" ? h("span", { class: "s-tag book" }, "to book") : null,
              s.status === "waiting" ? h("span", { class: "s-tag wait" }, "waiting") : null,
              s.status === "stuck" ? h("span", { class: "s-tag stuck" }, "stuck") : null),
            h("span", { class: "s-n" }, [s.track !== "General" ? s.track : "", s.notes].filter(Boolean).join(" · "))),
          h("span", { class: `w${late ? " hot" : ""}` }, when),
          avatar(s.owner));
      })) : h("p", { class: "none" }, "No steps yet. Add rows to the Steps tab with this timeline's id: ", h("code", {}, t.id)));

    const owners = [...new Set(own.map((s) => s.owner || "Unassigned"))];
    const who = h("div", { class: "card" }, h("h3", {}, "Who does what"),
      h("div", { class: "who" }, owners.map((o) => {
        const mine = own.filter((s) => (s.owner || "Unassigned") === o);
        const openMine = mine.filter(isOpen);
        const next = [...openMine.filter((s) => dueDate(s)).sort(byDue), ...openMine.filter((s) => !dueDate(s))][0];
        return h("div", {}, avatar(o === "Unassigned" ? "?" : o),
          h("span", {}, h("b", {}, o), h("span", { class: "d" },
            openMine.length ? `${openMine.length} open · next: ${next.title}` : `${mine.length} done`)));
      })));

    const main = h("div", { class: "main" }, mini, title, rmap.el, h("div", { class: "row2" }, stepCard, who), warningsBox(), footer());
    return { el: h("div", { class: "page" }, h("div", { class: "panel fx" }, main)), layout: rmap.layout };
  }

  // ---------- sidebar pages (collections) ----------
  // Each page is a row of the Collections tab and reads its own tab. The site is read-only:
  // decisions (shortlisting, marking paid, ...) happen in the spreadsheet.
  const pageState = {};
  const ICONS = {
    roadmap: '<path d="M3 6h7M3 12h12M3 18h5"/><path d="M14 6h7M18 12h3M11 18h10"/>',
    bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21a2 2 0 0 0 4 0"/>',
    building: '<path d="M3 21h18M5 21V10l7-5 7 5v11M9 21v-6h6v6"/>',
    document: '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
    star: '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
    folder: '<path d="M3 7h6l2 2h10v10H3z"/>',
    wallet: '<path d="M3 7h16a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 7l12-4v4M16 13h2"/>',
    heart: '<path d="M12 20s-8-5-8-11a4 4 0 0 1 8-1 4 4 0 0 1 8 1c0 6-8 11-8 11z"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>',
  };
  const icon = (key) => {
    const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    s.setAttribute("viewBox", "0 0 24 24"); s.setAttribute("aria-hidden", "true"); s.innerHTML = ICONS[key] || ICONS.list;
    return s;
  };
  const ext = (url, lbl = "Open ↗") => (url && /^https?:\/\//.test(url) ? h("a", { href: url, target: "_blank", rel: "noopener" }, lbl) : null);
  const tag = (text, cls = "") => h("span", { class: `tg${cls ? " tg-" + cls : ""}` }, text);
  // Status colors by meaning, so any vocabulary works: good / in motion / bad / neutral.
  const GOOD = /^(done|ok|paid|accepted|published|shortlisted|picked|normal|complete|completed|approved|received|booked)$/;
  const BUSY = /^(doing|applied|writing|submitted|scheduled|in progress|pending|sent|waiting)$/;
  const BAD = /^(rejected|dropped|overdue|late|missed|high|cancelled|canceled|declined|failed)$/;
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const statusTag = (s) => (s ? tag(cap(s), GOOD.test(s) ? "ok" : BUSY.test(s) ? "ind" : BAD.test(s) ? "no" : "") : null);
  // Only deadline-like date columns ("deadline", "due", "apply by") get flagged once passed.
  const isDeadline = (c) => /deadline|due|apply/.test(c.date_field);
  const COLLECTIONS = DATA.collections || [];
  const colById = new Map(COLLECTIONS.map((c) => [c.id, c]));
  // Column label: the header as typed in the sheet; "intl_grads" style headers become "Intl grads".
  const label = (c, f) => (c.labels[f] || f).replace(/_/g, " ").replace(/^./, (x) => x.toUpperCase());
  const recentCount = (c) => c.items.filter((i) => i.date && daysBetween(iso(i.date), TODAY) <= 7).length;
  const fmtItemDate = (i) => (i.date ? fmtDate(i.date, i.approx) : "");
  // "Open" = not yet in a final good or bad status; used to flag passed dates.
  const isOpenLike = (i) => !i.status || !(GOOD.test(i.status) || BAD.test(i.status));

  function emptyState(c) {
    return h("div", { class: "empty" }, h("b", {}, `No ${c.name.toLowerCase()} yet`),
      h("p", {}, c.empty || `Rows added to the ${c.tab} tab of the spreadsheet appear here.`),
      DATA.sheet_url ? h("p", { class: "small" }, sheetLink("Open the spreadsheet ↗", "")) : null);
  }
  function pageShell(title, sub, body, { sheet = true } = {}) {
    return h("div", { class: "page" }, h("div", { class: "panel ov" },
      h("div", { class: "top" }, h("div", {}, h("h1", {}, title), sub ? h("p", {}, sub) : null),
        sheet && DATA.sheet_url ? h("div", { class: "tools" }, sheetLink("Edit in sheet ↗")) : null),
      body, warningsBox(), footer()));
  }
  // Order: position of the status in the Statuses list, then date, then sheet order. Feeds: newest first.
  function sorted(c) {
    const pos = (i) => (c.statuses.length && i.status ? c.statuses.indexOf(i.status) : 0);
    const d = (i) => i.date || "9999";
    if (c.layout === "feed") return [...c.items].sort((a, b) => ((b.date || "") < (a.date || "") ? -1 : (b.date || "") > (a.date || "") ? 1 : a.row - b.row));
    return [...c.items].sort((a, b) => pos(a) - pos(b) || (d(a) < d(b) ? -1 : d(a) > d(b) ? 1 : 0) || a.row - b.row);
  }
  function cell(c, i, f) {
    if (f === c.status_field) return statusTag(i.status);
    if (f === c.date_field) {
      if (!i.date) return i.values[f] || "";
      const late = isDeadline(c) && isOpenLike(i) && iso(i.date) < TODAY;
      return h("span", { class: late ? "hot" : "" }, late ? `passed ${fmtItemDate(i)}` : fmtItemDate(i));
    }
    const v = i.values[f] || "";
    if (/^https?:\/\//.test(v)) return ext(v);
    if (f === "fit" || f === "rating") {
      const n = Number(v);
      if (v !== "" && n >= 0 && n <= 5) return h("span", { class: "fit", title: `${n} of 5` }, [0, 1, 2, 3, 4].map((k) => h("i", { class: k < n ? "on" : "" })));
    }
    return v;
  }
  function detailBody(c, i) {
    const rows = Object.entries(i.values).filter(([f, v]) => v && f !== c.title_field && f !== "link");
    const short = rows.filter(([, v]) => v.length <= 60), long = rows.filter(([, v]) => v.length > 60);
    return [
      short.length ? h("div", { class: "kv" }, short.map(([f]) => [h("span", {}, label(c, f)), h("span", {}, cell(c, i, f))])) : null,
      long.map(([f, v]) => h("div", { class: "note" }, h("b", {}, label(c, f)), v))];
  }
  function detailCard(c, i) {
    return h("div", { class: "card" }, h("h3", {}, "Selected", ext(i.values.link)), h("h4", { class: "dt" }, i.title), detailBody(c, i));
  }
  // Table rows expand in place: tap a row to show all its details right below it, tap again to close.
  const openRow = {};
  function tablePage(c, list) {
    const cols = [c.title_field, ...c.fields.filter((f) => f !== c.title_field)];
    if (c.status_field && !cols.includes(c.status_field)) cols.push(c.status_field);
    const open = list.includes(openRow[c.id]) ? openRow[c.id] : null;
    const toggle = (i) => () => { openRow[c.id] = open === i ? null : i; render(); };
    const body = [];
    for (const i of list) {
      const on = i === open;
      body.push(h("tr", { class: on ? "sel" : "", tabindex: "0", "aria-expanded": on ? "true" : "false", onclick: toggle(i),
        onkeydown: (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); toggle(i)(); } } },
        // Title column wraps (pinned on narrow screens); long values show two lines, full text when expanded.
        cols.map((f, j) => {
          if (j === 0) return h("td", { class: "tt" }, h("div", { class: "ttw" }, h("span", { class: "chev", "aria-hidden": "true" }), h("b", { title: i.title }, i.title)));
          const v = i.values[f] || "";
          return v.length > 40 ? h("td", { class: "wrap" }, h("span", { class: "clamp", title: v }, cell(c, i, f))) : h("td", {}, cell(c, i, f));
        })));
      if (on) body.push(h("tr", { class: "xp" }, h("td", { colspan: String(cols.length) },
        h("div", { class: "xp-in" }, h("div", { class: "xp-h" }, h("b", {}, i.title), ext(i.values.link)), detailBody(c, i)))));
    }
    return h("div", { class: "card scroll" }, h("table", { class: "t" },
      h("thead", {}, h("tr", {}, cols.map((f) => h("th", {}, label(c, f))))), h("tbody", {}, body)));
  }
  function cardsPage(c, list) {
    const sel = list[Math.min(pageState[c.id] || 0, list.length - 1)];
    const other = c.fields.filter((f) => f !== c.status_field && f !== c.date_field && f !== c.title_field);
    const isShort = (f) => list.every((i) => (i.values[f] || "").length <= 40);
    const meta = other.filter(isShort).slice(0, 2);
    const body = other.find((f) => !meta.includes(f));
    return h("div", {},
      h("div", { class: "grid3" }, list.map((i, k) => h("button", { type: "button", class: `prop${i === sel ? " sel" : ""}`, onclick: () => { pageState[c.id] = k; render(); } },
        h("span", { class: "meta" }, meta[0] && i.values[meta[0]] ? tag(i.values[meta[0]], "ind") : null, statusTag(i.status)),
        h("h4", {}, i.title), body && i.values[body] ? h("p", {}, i.values[body]) : null,
        h("span", { class: "prow" }, h("span", {}, meta[1] && i.values[meta[1]] ? `${label(c, meta[1])}: ${i.values[meta[1]]}` : fmtItemDate(i)), avatar(i.values.owner || i.values.who))))),
      h("div", { style: "margin-top:16px" }, detailCard(c, sel)));
  }
  function feedPage(c, list) {
    const textF = c.fields.find((f) => !["who", "owner", "timeline", "link", c.date_field, c.title_field].includes(f)) || "text";
    return h("div", { class: "feed" }, list.map((i) => {
      const t = i.timeline && byId.get(i.timeline);
      const who = i.values.who || i.values.owner || "";
      return h("article", { class: "post" },
        h("div", { class: "post-hd" }, avatar(who), who ? h("b", {}, who) : null,
          t ? h("a", withColor(t, { class: "tltag", href: `#t/${encodeURIComponent(t.id)}` }), t.name) : null,
          h("time", {}, fmtItemDate(i) || i.values[c.date_field] || "")),
        h("h4", {}, i.title), i.values[textF] ? h("p", {}, i.values[textF]) : null,
        i.values.link ? h("div", { class: "post-go" }, ext(i.values.link)) : null);
    }));
  }
  function collectionPage(c) {
    const list = sorted(c);
    if (!list.length) return pageShell(c.name, c.description, emptyState(c));
    const counts = c.status_field && c.statuses.length
      ? c.statuses.map((s) => [s, list.filter((i) => i.status === s).length]).filter(([, n]) => n).map(([s, n]) => `${n} ${s}`).join(" · ")
      : `${list.length} item${list.length === 1 ? "" : "s"}`;
    const body = c.layout === "cards" ? cardsPage(c, list) : c.layout === "feed" ? feedPage(c, list) : tablePage(c, list);
    return pageShell(c.name, [c.description, counts].filter(Boolean).join(" · "), body);
  }
  function documentsPage() {
    const docs = DATA.documents;
    const KIND = { folder: ["DIR", "dir"], sheet: ["XLS", "sh"], doc: ["DOC", "doc"], pdf: ["PDF", "pdf"], file: ["FILE", ""] };
    const body = h("div", { class: "card" }, h("h3", {}, "Shared Drive folder", ext(docs.root_url, "Open Drive ↗")),
      docs.items.length ? docs.items.map((f) => h("a", { class: "file", href: f.url, target: "_blank", rel: "noopener" },
        h("i", { class: (KIND[f.kind] || KIND.file)[1] }, (KIND[f.kind] || KIND.file)[0]), h("span", {}, f.name, f.modified ? h("small", {}, `changed ${fmtDate(f.modified)}`) : null), h("span", { class: "w" }, "Open ↗")))
        : h("p", { class: "none" }, "The folder is empty."));
    return pageShell("Documents", "Everything lives in the shared Drive folder; this list refreshes with every update", body, { sheet: false });
  }

  // ---------- sidebar shell ----------
  const initials = (s) => (s || "").split(/\s+/).filter(Boolean).map((w) => w[0]).join("").slice(0, 2).toUpperCase() || "★";
  function sidebar(key) {
    const close = () => shell.classList.remove("open");
    const link = (hash, lbl, ico, extra, on, attrs = {}) => h("a", { ...attrs, class: `sidelink${on ? " on" : ""}${attrs.class ? " " + attrs.class : ""}`, href: hash, onclick: close, "aria-current": on ? "page" : null },
      ico ? icon(ico) : null, lbl, extra || null);
    const count = (n) => (n ? h("span", { class: "n" }, n) : null);
    const groups = [];
    for (const c of COLLECTIONS) {
      let g = groups.find((x) => x.name === c.group);
      if (!g) groups.push((g = { name: c.group, items: [] }));
      g.items.push(link(`#p/${c.id}`, c.name, c.icon || (c.layout === "feed" ? "bell" : "list"),
        count(c.layout === "feed" ? recentCount(c) : c.items.length), key === `p:${c.id}`));
    }
    const tls = timelines.map((t) => {
      const ns = nextStep(t.id);
      const booking = stepsOf(t.id).some((s) => s.status === "to book");
      return link(`#t/${encodeURIComponent(t.id)}`, [dot(), h("span", { class: "nm" }, t.name)],
        null, h("em", {}, ns ? fmtDue(dueDate(ns), ns.approx) : booking ? "to book" : ""), key === `t:${t.id}`, withColor(t));
    });
    return h("aside", { class: "sidebar", "aria-label": "Navigation" },
      h("a", { class: "brand", href: "#", onclick: close }, h("span", { class: "logo" }, initials(DATA.name || DATA.title)), DATA.name ? DATA.name.split(/\s+/)[0] : DATA.title),
      link("#", "Roadmap", "roadmap", null, key === "roadmap"),
      groups.map((g) => [h("h6", {}, g.name), g.items]),
      DATA.documents ? [h("h6", {}, "Files"), link("#p/documents", "Documents", "folder", null, key === "p:documents")] : null,
      timelines.length ? [h("h6", {}, "Timelines"), tls] : null,
      DATA.sheet_url ? sheetLink("＋ New timeline", "sidelink add") : null);
  }
  const shell = h("div", { class: "shell" });
  app.append(shell);
  shell.addEventListener("click", (ev) => { if (ev.target === shell) shell.classList.remove("open"); });

  // ---------- routing ----------
  let current = null, lastRoute = null;
  function render() {
    hideTip();
    const hash = location.hash;
    let key = "roadmap", title = "Roadmap", view;
    const t = hash.match(/^#t\/(.+)$/), p = hash.match(/^#p\/([\w-]+)$/);
    const tid = t && decodeURIComponent(t[1]);
    if (tid && byId.has(tid)) { key = `t:${tid}`; title = byId.get(tid).name; }
    else if (p && colById.has(p[1])) { key = `p:${p[1]}`; title = colById.get(p[1]).name; }
    else if (p && p[1] === "documents" && DATA.documents) { key = "p:documents"; title = "Documents"; }
    else if (hash && hash !== "#") history.replaceState(null, "", location.pathname + location.search);
    if (key !== lastRoute) weekShift = 0;
    if (key.startsWith("t:")) view = focus(tid);
    else if (key === "p:documents") view = { el: documentsPage(), layout: () => {} };
    else if (key.startsWith("p:")) view = { el: collectionPage(colById.get(p[1])), layout: () => {} };
    else view = overview();
    const keepScroll = key === lastRoute ? window.scrollY : 0;
    shell.classList.remove("open");
    shell.replaceChildren(sidebar(key), h("div", { class: "shell-main" },
      h("div", { class: "mbar" }, h("button", { type: "button", "aria-label": "Open menu", onclick: () => shell.classList.add("open") }, "☰ Menu"), h("span", {}, title)),
      view.el));
    current = view;
    view.layout();
    window.scrollTo(0, keepScroll);
    lastRoute = key;
    document.title = key === "roadmap" ? DATA.title : `${title} · ${DATA.title}`;
  }
  window.addEventListener("hashchange", render);
  let lastW = window.innerWidth, rt = 0;
  window.addEventListener("resize", () => {
    if (window.innerWidth === lastW) return;
    lastW = window.innerWidth;
    clearTimeout(rt);
    rt = setTimeout(() => current && current.layout(), 120);
  });
  render();
})();
