// The figures of the documentation: each one shows how a measure comes about on the numbers of
// its example. The data come from the example while the site is built (docs/show.py); the
// figures draw at the width of the page and follow the pointer, a finger or the keyboard.
//
// <figure class="fig" data-kind="errors"><script type="application/json">{...}</script></figure>
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const still = matchMedia("(prefers-reduced-motion: reduce)");
  const C = name => `var(--fig-${name})`;

  function make(doc, name, attrs, parent, text) {
    const e = doc(name);
    for (const k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  const el = (...a) => make(n => document.createElementNS(NS, n), ...a);
  const tag = (...a) => make(n => document.createElement(n), ...a);

  // the marks the figures are made of; colours are names of the --fig- variables
  const label = (p, x, y, text, fill = "hi", cls = null, anchor = null) => el("text", { x, y, fill: C(fill), class: cls, "text-anchor": anchor }, p, text);
  const bold = (p, x, y, text) => el("text", { x, y, fill: C("hi"), "font-weight": 600 }, p, text);
  const line = (p, x1, y1, x2, y2, stroke = "lo", width = 1, more = {}) => el("line", { x1, y1, x2, y2, stroke: C(stroke), "stroke-width": width, ...more }, p);
  const dot = (p, cx, cy, r, fill, stroke = null) => el("circle", { cx, cy, r, fill: C(fill), stroke: stroke && C(stroke), "stroke-width": 1.5 }, p);
  const box = (p, x, y, width, height, fill, more = {}) => el("rect", { x, y, width, height, fill: C(fill), ...more }, p);
  const ticks = (p, X, values, y0, y1, text) => values.forEach(t => {
    line(p, X(t), y0, X(t), y1, "lo", 0.6);
    label(p, X(t), y0 - 8, text(t), "mid", "fig-small", "middle");
  });

  // a number with d decimals, a real minus sign, and NaN for a missing value
  const f = (v, d = 2) => (v == null ? "NaN" : v.toFixed(d).replace("-", "−"));
  const linear = (d0, d1, r0, r1) => v => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  const sum = a => a.reduce((s, v) => s + v, 0);
  const at = (svg, e) => new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse());

  // an svg and a caption: draw(svg, width, hover) returns [height, caption]; pick(point) says
  // what the pointer is on, and a change of it draws again
  function panel(figure, aria, draw, pick = null) {
    const svg = el("svg", { role: "img", "aria-label": aria }, figure);
    const caption = tag("figcaption", { "aria-live": "polite" }, figure);
    let width = 0, hover = null;
    const redraw = () => {
      if (!width) return;
      svg.replaceChildren();
      const [height, text] = draw(svg, width, hover);
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      caption.innerHTML = text;
    };
    // in the next frame, so that a new height does not trigger the observer again
    new ResizeObserver(() => requestAnimationFrame(() => {
      const w = Math.round(figure.getBoundingClientRect().width);
      if (w && w !== width) { width = w; redraw(); }
    })).observe(figure);
    if (pick) {
      const set = h => { if (JSON.stringify(h) !== JSON.stringify(hover)) { hover = h; redraw(); } };
      svg.addEventListener("pointermove", e => set(pick(at(svg, e))));
      svg.addEventListener("pointerleave", () => set(null));
    }
    return { svg, redraw };
  }

  // calls step() every frame while it returns true; with reduced motion, until it is done
  function animation(step) {
    let frame = 0;
    const run = () => {
      let more = step();
      while (more && still.matches) more = step();
      frame = more ? requestAnimationFrame(run) : 0;
    };
    return () => { if (!frame) frame = requestAnimationFrame(run); };
  }

  // a row of buttons, one pressed; onpick(value) when another is pressed
  function buttons(figure, name, options, value, onpick) {
    const row = tag("div", { class: "fig-controls", role: "group", "aria-label": name }, figure);
    tag("span", {}, row, name);
    const all = options.map(([v, text]) => {
      const b = tag("button", { type: "button", class: "fig-button", "aria-pressed": String(v === value) }, row, text);
      b.addEventListener("click", () => { all.forEach(o => o.setAttribute("aria-pressed", String(o === b))); onpick(v); });
      return b;
    });
  }

  // Continuous errors: per question the reference, the answer and the error between them; the
  // band of the tolerance shows which answers are within it.
  function errors(figure, d) {
    const top = 28, rowH = 38, n = d.places.length;
    let x = d.thresholds[Math.min(1, d.thresholds.length - 1)];
    buttons(figure, "tolerance", d.thresholds.map(t => [t, `± ${t} m`]), x, v => { x = v; redraw(); });
    const { redraw } = panel(figure, "Per question the reference depth, the agent's answer and the error between them", (svg, W, hover) => {
      const max = Math.ceil(Math.max(...d.reference, ...d.answer.filter(v => v != null)) + 0.5);
      const X = linear(0, max, Math.min(130, W * 0.3), W - 64), H = top + n * rowH;
      ticks(svg, X, [...Array(max + 1).keys()], top - 4, H, t => `${t} m`);
      label(svg, W, top - 12, "error", "mid", "fig-small", "end");
      const errs = [];
      d.places.forEach((place, i) => {
        const y = top + i * rowH + rowH / 2, ref = d.reference[i], a = d.answer[i], lo = Math.max(0, ref - x);
        const g = el("g", { opacity: hover == null || hover === i ? 1 : 0.3 }, svg);
        label(g, 0, y + 4, place);
        box(g, X(lo), y - 10, X(ref + x) - X(lo), 20, "water", { rx: 2, opacity: 0.4 });
        line(g, X(ref), y - 12, X(ref), y + 12, "hi", 1.6);
        if (a == null) {
          label(g, X(ref + x) + 8, y + 4, "no answer", "mid", "fig-small");
          return label(g, W, y + 4, "left out", "mid", "fig-small", "end");
        }
        const e = Math.abs(a - ref);
        errs.push([i, e]);
        line(g, X(ref), y, X(a), y, "answer", 2);
        dot(g, X(a), y, 5, e <= x + 1e-9 ? "answer" : "plate", "answer");
        label(g, W, y + 4, f(e), "hi", "fig-mono", "end");
      });
      const term = ([i, e], s) => (i === hover ? `<b>${s(e)}</b>` : s(e)), k = errs.length;
      return [H + 4,
        `<b>MAE</b> = (${errs.map(r => term(r, f)).join(" + ")}) / ${k} = <b>${f(d.mae, 3)}</b> m. ` +
        `<b>RMSE</b> = √((${errs.map(r => term(r, e => `${f(e)}²`)).join(" + ")}) / ${k}) = <b>${f(d.rmse, 3)}</b> m. ` +
        `<b>Within ± ${x} m</b>: <b>${f(d.within[d.thresholds.indexOf(x)], 0)}%</b> of the answers. ` +
        `The question without an answer is NaN, left out of every measure and counted in <code>missing</code>.`];
    }, p => (p.y > top && p.y < top + n * rowH ? Math.floor((p.y - top) / rowH) : null));
  }

  // Yes or no: the answers in one table of hits, misses, false alarms and correct "dry"s, and the
  // measures from it; below, the Brier score of the probability in each answer.
  function contingency(figure, d) {
    // [name, answer, observed]: the cells of the table
    const cells = { hit: ["hits", 1, 1], false_alarm: ["false alarms", 1, 0], miss: ["misses", 0, 1], correct: ["correct dry", 0, 0] };
    const keyOf = i => Object.keys(cells).find(k => cells[k][1] === d.answer[i] && cells[k][2] === d.observed[i]);
    const n = k => d.places.filter((_, i) => keyOf(i) === k).length;
    const ratio = (top, bottom) => `${sum(top.map(n))} / ${sum(bottom.map(n))}`;
    // [short, measure, in words, numerator, denominator]
    const formulas = [
      ["POD", "probability_of_detection", "hits / (hits + misses)", ["hit"], ["hit", "miss"]],
      ["FAR", "false_alarm_ratio", "false alarms / (hits + false alarms)", ["false_alarm"], ["hit", "false_alarm"]],
      ["CSI", "critical_success_index", "hits / (hits + misses + false alarms)", ["hit"], ["hit", "miss", "false_alarm"]],
      ["bias", "frequency_bias", "(hits + false alarms) / (hits + misses)", ["hit", "false_alarm"], ["hit", "miss"]],
    ];
    const uses = i => [...formulas[i][3], ...formulas[i][4]];
    let regions = [];
    panel(figure, "The yes or no answers in a contingency table, the measures from it, and the Brier score of each probability", (svg, W, hover) => {
      regions = [];
      const wide = W >= 620, x0 = 96, cw = Math.min(150, ((wide ? W * 0.56 : W) - x0) / 2), ch = 86, y0 = 34;
      const cell = typeof hover === "string" ? hover : null, used = typeof hover === "number" ? uses(hover) : null;
      label(svg, x0 + cw, 12, "observed", "mid", "fig-small", "middle");
      label(svg, 0, y0 + ch - 4, "answer", "mid", "fig-small");
      ["floods", "dry"].forEach((t, j) => {
        label(svg, x0 + cw * j + cw / 2, 28, t, "hi", null, "middle");
        label(svg, 0, y0 + ch * j + ch / 2 + (j ? 12 : -4), t);
      });
      Object.entries(cells).forEach(([k, [name, answer, observed]]) => {
        const x = x0 + (1 - observed) * cw, y = y0 + (1 - answer) * ch, on = cell === k || used?.includes(k);
        box(svg, x + 1, y + 1, cw - 2, ch - 2, on ? "accent" : "plate", { rx: 4, stroke: C(on ? "hi" : "lo"), "stroke-width": 0.9 });
        const g = el("g", { opacity: (cell && cell !== k) || (used && !used.includes(k)) ? 0.35 : 1 }, svg);
        label(g, x + 10, y + 20, name, "mid", "fig-small");
        label(g, x + cw - 10, y + 22, String(n(k)), "hi", "fig-big", "end");
        d.places.filter((_, i) => keyOf(i) === k).forEach((p, j) => label(g, x + 10, y + 42 + j * 16, p));
        regions.push({ id: k, x, y, w: cw, h: ch });
      });
      const fx = wide ? x0 + 2 * cw + 28 : 0, fy = wide ? y0 + 6 : y0 + 2 * ch + 30;
      formulas.forEach(([short, key, words, top, bottom], i) => {
        const y = fy + i * 40, g = el("g", { opacity: (cell && !uses(i).includes(cell)) || (used && hover !== i) ? 0.3 : 1 }, svg);
        el("text", { x: fx, y: y + 12, fill: C("hi") }, g).innerHTML = `<tspan font-weight="600">${short}</tspan> = ${words}`;
        label(g, fx, y + 29, `= ${ratio(top, bottom)} = ${f(d.measures[key])}`, "mid", "fig-mono");
        regions.push({ id: i, x: fx, y, w: W - fx, h: 36 });
      });
      // the Brier score of the probabilities
      const by = (wide ? y0 + 2 * ch : fy + 160) + 46, X = linear(0, 1, Math.min(130, W * 0.3), W - 150), rowH = 30;
      bold(svg, 0, by - 14, "The probability in each answer");
      [0, 0.5, 1].forEach(t => label(svg, X(t), by + 2, String(t), "mid", "fig-small", "middle"));
      const sq = d.places.map((p, i) => {
        const y = by + 22 + i * rowH, o = d.observed[i], v = d.p[i];
        label(svg, 0, y + 4, p);
        line(svg, X(0), y, X(1), y);
        box(svg, X(o) - 4, y - 4, 8, 8, "hi");
        line(svg, X(v), y, X(o), y, "answer", 2);
        dot(svg, X(v), y, 5, "answer");
        label(svg, W, y + 4, `(${f(v)} − ${o})² = ${f((v - o) ** 2)}`, "hi", "fig-mono", "end");
        return (v - o) ** 2;
      });
      return [by + 22 + d.places.length * rowH,
        `Point at a cell to see the measures that use it, or at a measure to see its cells. ` +
        `Every question counts in one table, so the measures are pooled, never averaged per question. ` +
        `The square is what happened (1 floods, 0 dry), the dot the probability in the answer: ` +
        `<b>Brier</b> = (${sq.map(v => f(v)).join(" + ")}) / ${sq.length} = <b>${f(d.brier, 3)}</b>.`];
    }, p => regions.find(r => p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h)?.id ?? null);
  }

  // Maps: a window moves over the reference and the answer, every hour, like a lens; it shows the
  // fractions of wet pixels that the FSS compares, set against its useful level.
  function fss(figure, d) {
    const ny = d.reference[0].length, nx = d.reference[0][0].length;
    let w = d.windows[d.windows.length - 1], geo = null;
    const clamp = ({ c, r }) => {
      const h = (w - 1) / 2;
      return { c: Math.min(nx - 1 - h, Math.max(h, Math.round(c))), r: Math.min(ny - 1 - h, Math.max(h, Math.round(r))) };
    };
    const frac = (grid, { c, r }) => {
      const h = (w - 1) / 2;
      return sum(grid.slice(r - h, r + h + 1).flatMap(row => row.slice(c - h, c + h + 1))) / (w * w);
    };
    let target = clamp({ c: nx / 2 - 1, r: (ny - 1) / 2 }), pos = { ...target };
    buttons(figure, "window", d.windows.map(v => [v, `${v} pixel${v > 1 ? "s" : ""}`]), w, v => { w = v; target = clamp(target); pos = { ...target }; redraw(); });
    const move = animation(() => {
      const k = 0.28;
      pos = { c: pos.c + (target.c - pos.c) * k, r: pos.r + (target.r - pos.r) * k };
      redraw();
      return Math.abs(target.c - pos.c) + Math.abs(target.r - pos.r) > 0.01;
    });
    const { svg, redraw } = panel(figure, "The reference and the answer map every hour, a window over both, and the FSS against its useful level", (svg, W) => {
      const left = 62, gap = 18, c = Math.max(7, Math.min(18, Math.floor((W - left - 2 * gap - Math.max(130, W * 0.24)) / (2 * nx))));
      const gx = [left, left + nx * c + gap], px = gx[1] + nx * c + gap, rowH = ny * c + 34, top = 22;
      const rowsY = d.lead_time.map((_, t) => top + t * rowH), h = (w - 1) / 2, X = linear(0, 1, px, W - 44), k = d.windows.indexOf(w);
      geo = { gx, c, rowsY };
      ["reference", "answer"].forEach((t, j) => label(svg, gx[j], top - 8, t, "mid", "fig-small"));
      label(svg, px, top - 8, "FSS and its useful level", "mid", "fig-small");
      d.lead_time.forEach((lt, t) => {
        const y = rowsY[t], yb = y + (ny * c) / 2, s = d.fss[k][t], useful = d.useful[t];
        label(svg, 0, yb + 4, `${lt} min`);
        [d.reference[t], d.answer[t]].forEach((grid, j) => {
          grid.forEach((row, r) => row.forEach((wet, q) => box(svg, gx[j] + q * c, y + r * c, c, c, wet ? "water" : "plate", { stroke: C("lo"), "stroke-width": 0.5 })));
          box(svg, gx[j] + (pos.c - h) * c, y + (pos.r - h) * c, w * c, w * c, "none", { fill: "none", stroke: C("hi"), "stroke-width": 1.8, rx: 1.5 });
          label(svg, gx[j], y + ny * c + 15, `${j ? "f" : "o"} = ${Math.round(frac(grid, target) * w * w)}/${w * w} wet`, "mid", "fig-small");
        });
        line(svg, X(0), yb, X(1), yb, "lo", 6, { "stroke-linecap": "round" });
        line(svg, X(0), yb, X(s), yb, s >= useful - 1e-9 ? "answer" : "mid", 6, { "stroke-linecap": "round" });
        line(svg, X(useful), yb - 9, X(useful), yb + 9, "hi", 1.6);
        label(svg, W, yb + 4, f(s), "hi", "fig-mono", "end");
        label(svg, X(useful), yb + 22, `useful ${f(useful)}`, "mid", "fig-small", "middle");
      });
      return [top + d.lead_time.length * rowH,
        `Move over a map: the window shows the fraction of wet pixels in the reference (o) and the answer (f). ` +
        `<b>FSS</b> = 1 − Σ(f − o)² / (Σf² + Σo²) over every window that fits in the map. ` +
        `It is useful from 0.5 + f₀/2, with f₀ the wet fraction of the reference that hour. ` +
        `With a window of ${w} pixel${w > 1 ? "s" : ""} (${w * 25} m) the map stays useful up to <b>${d.skillful[k]} min</b>: its skillful lead time.`];
    });
    svg.addEventListener("pointermove", e => {
      if (!geo) return;
      const p = at(svg, e), { gx, c, rowsY } = geo, g = gx.find(x => p.x >= x - c && p.x <= x + nx * c + c);
      const t = rowsY.findIndex(y => p.y >= y - c && p.y <= y + ny * c + c);
      if (g == null) return;
      const next = clamp({ c: (p.x - g) / c - 0.5, r: t < 0 ? target.r : (p.y - rowsY[t]) / c - 0.5 });
      if (next.c !== target.c || next.r !== target.r) { target = next; move(); }
    });
  }

  // Ensembles: the members and the observation every time, their rank, the fraction of members
  // above the alarm level; below, the rank histogram of all observations.
  function ensemble(figure, d) {
    const m = d.members[0].length, n = d.observed.length, top = 30, rowH = 44, hy = top + n * rowH + 44, bh = 70;
    let bw = 0, left = 0;
    panel(figure, "The members and the observation every time, and the rank histogram", (svg, W, hover) => {
      const all = [...d.members.flat(), ...d.observed, d.alarm], L = Math.min(118, W * 0.25), R = W - 196, cols = j => R + 44 + j * 56;
      const lo = Math.floor(Math.min(...all) * 2) / 2 - 0.5, hi = Math.ceil(Math.max(...all) * 2) / 2 + 0.5, X = linear(lo, hi, L, R);
      const row = hover?.row ?? -1, bar = hover?.bar ?? -1;
      bw = Math.min(56, (W - L) / (m + 1));
      left = L;
      ticks(svg, X, Array.from({ length: (hi - lo) * 2 + 1 }, (_, k) => lo + k / 2), top - 4, top + n * rowH, t => `${t} m`);
      line(svg, X(d.alarm), top - 4, X(d.alarm), top + n * rowH, "bad", 1.2, { "stroke-dasharray": "4 3" });
      label(svg, X(d.alarm) + 4, top + n * rowH + 12, `alarm ${d.alarm} m`, "bad", "fig-small");
      ["rank", "P(above)", "CRPS"].forEach((t, j) => label(svg, cols(j), top - 12, t, "mid", "fig-small", "middle"));
      d.observed.forEach((o, i) => {
        const y = top + i * rowH + rowH / 2, members = d.members[i], seen = {};
        const g = el("g", { opacity: (row < 0 && bar < 0) || row === i || d.rank[i] - 1 === bar ? 1 : 0.3 }, svg);
        label(g, 0, y + 4, `6 h after ${d.times[i]}`);
        line(g, X(lo), y, X(hi), y);
        members.forEach(v => {
          const k = (seen[v] = (seen[v] || 0) + 1) - 1, same = members.filter(u => u === v).length;
          dot(g, X(v), y + (k - (same - 1) / 2) * 9, 4, v > d.alarm ? "answer" : "plate", "answer");
        });
        line(g, X(o), y - 16, X(o), y + 16, "hi", 1.8);
        [`${d.rank[i]} of ${m + 1}`, `${members.filter(v => v > d.alarm).length}/${m}`, f(d.crps[i])].forEach((t, j) => label(g, cols(j), y + 4, t, "hi", "fig-mono", "middle"));
      });
      bold(svg, 0, hy + 14, "Rank histogram");
      label(svg, 0, hy + 30, "rank of the observation", "mid", "fig-small");
      d.ranks.forEach((v, j) => {
        const h = Math.max(v * bh * 2, 0.8), on = bar === j || (row >= 0 && d.rank[row] - 1 === j);
        box(svg, L + j * bw + 3, hy + bh - h, bw - 6, h, on ? "answer" : "lo");
        label(svg, L + j * bw + bw / 2, hy + bh + 14, String(j + 1), "mid", "fig-small", "middle");
      });
      line(svg, L, hy + bh - (bh * 2) / (m + 1), L + (m + 1) * bw, hy + bh - (bh * 2) / (m + 1), "mid", 1, { "stroke-dasharray": "2 3" });
      return [hy + bh + 22,
        `The dots are the ${m} members, filled above the alarm level (dashed); the line is the observed level. ` +
        `<b>Fair CRPS</b> = mean of ${d.crps.map(v => f(v)).join(", ")} = <b>${f(d.crps_mean, 3)}</b> m. ` +
        `<b>Brier above ${d.alarm} m</b> (fair, from the fraction of members above it) = <b>${f(d.brier, 3)}</b>. ` +
        `A reliable ensemble has a flat rank histogram, at the dotted line; point at a time or a bar to match them.`];
    }, p => {
      if (p.y > top && p.y < top + n * rowH) return { row: Math.floor((p.y - top) / rowH) };
      return p.y > hy && bw && p.x >= left ? { bar: Math.min(m, Math.floor((p.x - left) / bw)) } : null;
    });
  }

  // Skill and significance: the error of the agent and of the reference per question, the skill
  // score from their means, and a bootstrap of the paired differences that builds the interval.
  function skill(figure, d) {
    const diff = d.agent.map((a, i) => a - d.reference[i]), n = diff.length, DRAWS = 400;
    // a small seeded random number generator (mulberry32), so that every visit looks the same
    let state = 0, seed = 1, draws = [], shown = 0, began = 0;
    const random = () => {
      state = (state + 0x6d2b79f5) | 0;
      let t = Math.imul(state ^ (state >>> 15), 1 | state);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    // the first resamples one by one, slowly, with their questions highlighted; then the rest
    // quickly: HOLD milliseconds each, then REST milliseconds for all the others
    const SLOW = 5, HOLD = 700, REST = 1500, slow = () => shown > 0 && shown <= SLOW && shown < DRAWS;
    const step = animation(() => {
      const t = still.matches ? Infinity : performance.now() - began;
      const next = t <= SLOW * HOLD ? Math.ceil(t / HOLD) : Math.min(DRAWS, Math.round(SLOW + ((t - SLOW * HOLD) / REST) * (DRAWS - SLOW)));
      if (next !== shown) { shown = next; redraw(); }
      return shown < DRAWS;
    });
    // all resamples are drawn at the start, so that the pile knows its height; they show one by one
    const start = () => {
      state = seed++;
      draws = Array.from({ length: DRAWS }, () => {
        const picks = Array.from({ length: n }, () => Math.floor(random() * n));
        return { picks, mean: sum(picks.map(i => diff[i])) / n };
      });
      shown = 0;
      began = performance.now();
      step();
    };
    const { redraw } = panel(figure, "The errors of the agent and the reference per question, the skill score, and the bootstrap of the differences", (svg, W) => {
      const L = Math.min(130, W * 0.3), R = W - 80, Xm = linear(0, Math.max(...d.mae), L, R);
      ["agent", "without tools"].forEach((t, j) => {
        const y = 24 + j * 22;
        label(svg, 0, y + 4, t);
        box(svg, L, y - 6, Xm(d.mae[j]) - L, 12, j ? "lo" : "answer", { rx: 2 });
        label(svg, W, y + 4, `MAE ${f(d.mae[j], 3)}`, "hi", "fig-mono", "end");
      });
      // the errors per question, paired; the questions of the last resample are highlighted
      const y0 = 88, rowH = 28, X = linear(0, Math.max(...d.reference, ...d.agent), L, R);
      const times = (slow() ? draws[shown - 1].picks : []).reduce((c, i) => ((c[i] = (c[i] || 0) + 1), c), {});
      bold(svg, 0, y0 - 10, "Error per question");
      label(svg, W, y0 - 10, "d = agent − without tools", "mid", "fig-small", "end");
      d.places.forEach((p, i) => {
        const y = y0 + 10 + i * rowH;
        if (times[i]) box(svg, 0, y - rowH / 2 + 2, W, rowH - 4, "accent", { rx: 3 });
        label(svg, 0, y + 4, times[i] > 1 ? `${p} ×${times[i]}` : p);
        line(svg, X(d.agent[i]), y, X(d.reference[i]), y, "lo", 2);
        dot(svg, X(d.reference[i]), y, 5, "plate", "mid");
        dot(svg, X(d.agent[i]), y, 5, "answer");
        label(svg, W, y + 4, f(diff[i]), "hi", "fig-mono", "end");
      });
      // the mean d of every resample as a pile of dots, at most as high as the pile of all draws
      const by = y0 + 36 + n * rowH, lo = Math.min(...diff) - 0.2, hi = Math.max(0, ...diff) + 0.2, Xd = linear(lo, hi, L, R);
      const binW = 7, room = 84, base = by + 24 + room, bin = v => Math.round((Xd(v) - L) / binW), count = {}, pile = {};
      draws.forEach(({ mean }) => (count[bin(mean)] = (count[bin(mean)] || 0) + 1));
      const rise = Math.min(5.6, room / Math.max(1, ...Object.values(count))), r = Math.min(2.6, rise / 2);
      bold(svg, 0, by, "Mean d of each resample");
      label(svg, 0, by + 16, `${shown} of ${DRAWS} drawn`, "mid", "fig-small");
      draws.slice(0, shown).forEach(({ mean }) => {
        const b = bin(mean), k = (pile[b] = (pile[b] || 0) + 1) - 1;
        el("circle", { cx: L + b * binW, cy: base - r - k * rise, r, fill: C("answer"), opacity: 0.8 }, svg);
      });
      line(svg, L, base, R, base, "mid");
      line(svg, Xd(0), by - 6, Xd(0), base + 6, "hi", 1, { "stroke-dasharray": "3 3" });
      label(svg, Xd(0) + 4, by + 2, "no difference", "mid", "fig-small");
      for (let t = Math.ceil(lo * 2) / 2; t <= hi; t += 0.5) label(svg, Xd(t), base + 16, f(t, 1), "mid", "fig-small", "middle");
      const ci = d.bootstrap, yc = base + 30;
      if (shown >= DRAWS) {
        el("path", { d: `M${Xd(ci.ci_lower)},${yc - 5} V${yc} H${Xd(ci.ci_upper)} V${yc - 5}`, fill: "none", stroke: C("hi"), "stroke-width": 1.4 }, svg);
        label(svg, (Xd(ci.ci_lower) + Xd(ci.ci_upper)) / 2, yc + 15, `95% interval ${f(ci.ci_lower)} to ${f(ci.ci_upper)}`, "hi", "fig-small", "middle");
      }
      return [yc + 22,
        `<b>Skill</b> = 1 − MAE / MAE without tools = 1 − ${f(d.mae[0], 3)} / ${f(d.mae[1], 3)} = <b>${f(d.skill)}</b>: 1 is perfect, 0 no better. ` +
        `Is that more than luck with ${n} questions? The <b>paired bootstrap</b> draws ${n} questions with replacement (the first ones highlighted), again and again, and takes the mean d of each. ` +
        `In ${f(100 * ci.a_better, 0)}% of ${d.n_boot.toLocaleString("en")} resamples the agent is better (d &lt; 0); here ${DRAWS} of them are drawn.`];
    });
    const again = tag("div", { class: "fig-controls" }, figure);
    tag("button", { type: "button", class: "fig-button" }, again, "resample again").addEventListener("click", start);
    new IntersectionObserver((entries, o) => { if (entries[0].isIntersecting) { o.disconnect(); start(); } }).observe(figure);
  }

  // Probability words: each word as cautious, average and bold readers take it; the reader picks
  // the probability, the Brier score follows.
  function words(figure, d) {
    const readers = ["cautious reader", "average reader", "bold reader"], top = 28, rowH = 36;
    let reader = 1;
    buttons(figure, "read by a", readers.map((r, i) => [i, r]), reader, v => { reader = v; redraw(); });
    const { redraw } = panel(figure, "Each probability word as a range of readings, with the reading of the chosen reader against what happened", (svg, W) => {
      const L = Math.min(210, W * 0.4), X = linear(0, 1, L, W - 60), H = top + d.places.length * rowH;
      ticks(svg, X, [0, 0.25, 0.5, 0.75, 1], top - 4, H, t => `${t * 100}%`);
      const sq = [];
      d.places.forEach((p, i) => {
        const y = top + i * rowH + rowH / 2, r = d.readings[i], o = d.observed[i] ? 1 : 0;
        label(svg, 0, y + 4, p);
        label(svg, L - 12, y + 4, `“${d.words[i]}”`, "mid", null, "end");
        if (!r) return label(svg, X(0) + 4, y + 4, "not one of the 29 words: missing", "mid", "fig-small");
        line(svg, X(r[0]), y, X(r[2]), y, "lo", 8, { "stroke-linecap": "round" });
        line(svg, X(r[1]), y - 6, X(r[1]), y + 6, "mid", 1.2);
        box(svg, X(o) - 4, y - 4, 8, 8, "hi");
        line(svg, X(r[reader]), y, X(o), y, "answer", 1.5, { "stroke-dasharray": "3 2" });
        dot(svg, X(r[reader]), y, 5.5, "answer");
        sq.push((r[reader] - o) ** 2);
        label(svg, W, y + 4, f(sq[sq.length - 1]), "hi", "fig-mono", "end");
      });
      return [H + 4,
        `The bar runs from how cautious to how bold readers take each word (5% to 95%), the tick is the mean; the square is what happened. ` +
        `For a ${readers[reader]}: <b>Brier</b> = (${sq.map(v => f(v)).join(" + ")}) / ${sq.length} = <b>${f(d.brier[reader], 3)}</b>. ` +
        `The same answers are worth ${d.brier.map(v => f(v, 3)).join(", ")} to the three readers.`];
    });
  }

  // Plain language: the answers with their water terms; a term shows how many hydrologists and
  // laypeople take it the same way.
  function jargon(figure, d) {
    const grid = tag("div", { class: "fig-answers" }, figure);
    d.agents.forEach(a => tag("div", { class: "fig-head" }, grid, a));
    let term = Object.keys(d.terms).find(k => d.terms[k].laypeople < d.below);
    const marks = [];
    d.questions.forEach((q, i) => {
      tag("div", { class: "fig-question" }, grid, q);
      d.answers[i].forEach((parts, j) => {
        const answer = tag("div", { class: "fig-answer" }, grid), ok = d.passed[i][j];
        tag("span", { class: "fig-verdict", style: `color: ${C(ok ? "good" : "bad")}` }, answer, ok ? "✓ passes" : "✗ jargon");
        parts.forEach(p => {
          if (typeof p === "string") return answer.append(p);
          const misread = d.terms[p.term].laypeople < d.below;
          const mark = tag("mark", { class: `fig-term ${misread ? "fig-misread" : "fig-read"}`, tabindex: "0", "data-term": p.term }, answer, p.text);
          const pick = () => { term = p.term; show(); };
          mark.addEventListener("pointerenter", pick);
          mark.addEventListener("focus", pick);
          marks.push(mark);
        });
      });
    });
    const { redraw } = panel(figure, "The share of hydrologists and laypeople that take the term as hydrologists do", (svg, W) => {
      const t = d.terms[term], X = linear(0, 100, Math.min(110, W * 0.25), W - 50), y0 = 40;
      el("text", { x: 0, y: 14, fill: C("hi") }, svg).innerHTML = `<tspan font-weight="600">“${term}”</tspan><tspan fill="${C("mid")}"> to a hydrologist: ${t.meaning}</tspan>`;
      [["hydrologists", t.experts], ["laypeople", t.laypeople]].forEach(([who, v], j) => {
        const y = y0 + j * 24;
        label(svg, 0, y + 4, who);
        box(svg, X(0), y - 7, X(100) - X(0), 14, "plate", { rx: 2, stroke: C("lo"), "stroke-width": 0.6 });
        box(svg, X(0), y - 7, X(v) - X(0), 14, j && v < d.below ? "bad" : "water", { rx: 2 });
        label(svg, W, y + 4, `${v}%`, "hi", "fig-mono", "end");
      });
      line(svg, X(d.below), y0 - 14, X(d.below), y0 + 38, "hi", 1, { "stroke-dasharray": "3 3" });
      label(svg, X(d.below), y0 + 52, `below ${d.below}% of laypeople: jargon`, "mid", "fig-small", "middle");
      return [y0 + 58,
        `Point at or tab to an underlined term. <b>Red</b>: fewer than ${d.below}% of laypeople take it as hydrologists do, so <code>Jargon</code> fails the answer; ` +
        `<b>green</b>: a water term most laypeople read the same way. No reference answer is needed, so this check also runs on live answers.`];
    });
    const show = () => { marks.forEach(m => m.classList.toggle("fig-on", m.dataset.term === term)); redraw(); };
    show();
  }

  // The steps of verify as a stack of plates, from the questions at the bottom to one
  // Verification on top. The pointer or the arrow keys pick a plate; the plates above it lift and fade.
  function steps(figure, d) {
    const S = 17, GAP = 34, CX = 150, TOP = 120, W = 600;
    const names = ["questions", "answers", "arrays", "metric", "Verification"], top = names.length - 1;
    const texts = [
      "A pydantic-evals <code>Dataset</code>: each case is a question as text, with its reference answer.",
      "The agent answers every question; pydantic-evals runs it, once or several times (<code>repeat</code>). One answer is missing.",
      "<code>verify</code> takes one field of every answer and reference answer, here the number itself, as two xarray arrays along <code>question</code> (and <code>run</code>). The missing answer is NaN.",
      "Any metric of <code>scores</code> compares the two arrays, here <code>mae</code> and <code>rmse</code>; NaN is left out, and ratios are pooled over all questions.",
      "The measures as an xarray Dataset, with <code>.missing</code>, <code>.to_frame()</code>, <code>.skill()</code> and <code>.plot()</code>.",
    ];
    const P = (u, v, z) => [CX + (u - v) * 0.866 * S, TOP + (u + v) * 0.5 * S - z];
    const pts = (ring, z) => ring.map(([u, v]) => P(u, v, z).map(n => n.toFixed(1)).join(",")).join(" ");
    const plate = [[-1.5, -1.5], [16.5, -1.5], [16.5, 6.5], [-1.5, 6.5]], y0 = P(-1.5, -1.5, top * GAP)[1] - 62;
    let pick = top, ghost = names.map(() => 0);
    const svg = el("svg", { role: "img", tabindex: "0", "aria-label": "verify as a stack of steps: the questions, the answers, the arrays, the metric and one Verification", viewBox: `0 ${y0} ${W} ${P(16.5, 6.5, 0)[1] + 20 - y0}` }, figure);
    svg.style.maxWidth = `${W}px`;
    const caption = tag("figcaption", { "aria-live": "polite" }, figure);

    // what a plate shows, at u along it (0 to 15) and v across it (0 to 5): shapes on the plate
    // in g, and upright text along the plate in layer
    function content(step, g, layer, z) {
      const row = i => 0.55 + i * 1.3;
      const T = (u, v, s, fill = "hi", size = 11, more = {}) => {
        const [x, y] = P(u, v, z);
        el("text", { x, y, "font-size": size, fill: C(fill), transform: `rotate(30 ${x.toFixed(1)} ${y.toFixed(1)})`, ...more }, layer, s);
      };
      const end = { "text-anchor": "end" }, mid = { "text-anchor": "middle" };
      d.places.forEach((p, i) => {
        const a = d.answer[i], e = a == null ? null : Math.abs(a - d.reference[i]);
        if (step === 0) { T(0, row(i), `How deep at the ${p}?`); T(15, row(i), `${f(d.reference[i], 1)} m`, "mid", 11, end); }
        if (step === 1) { T(0, row(i), p, "mid"); T(15, row(i), a == null ? "no answer" : `${f(a)} m`, a == null ? "mid" : "answer", 11, end); }
        if (step === 2 || step === 3) T(0, row(i), p, "mid", 10);
        if (step === 2) [[a, 6, "answer"], [d.reference[i], 10.6, "hi"]].forEach(([v, u, ink]) => {
          el("rect", { x: u, y: row(i) - 0.85, width: 3.2, height: 1.1, rx: 0.15, fill: C("plate"), stroke: C(ink), "stroke-width": 0.06, "stroke-dasharray": v == null ? "0.2 0.15" : null }, g);
          T(u + 1.6, row(i) - 0.05, v == null ? "NaN" : f(v), v == null ? "mid" : ink, 10, mid);
        });
        if (step === 3 && e == null) T(6, row(i), "NaN, left out", "mid", 10);
        if (step === 3 && e != null) {
          el("rect", { x: 6, y: row(i) - 0.6, width: Math.max(0.08, e * 25), height: 0.7, fill: C("answer") }, g);
          T(6.4 + e * 25, row(i), f(e), "hi", 10);
        }
      });
      if (step === 2) { T(7.6, -0.45, "fcst", "mid", 10, mid); T(12.2, -0.45, "obs", "mid", 10, mid); }
      if (step === 3) T(0, -0.45, "|fcst − obs|", "mid", 10);
      if (step === 4) [["mae", f(d.mae, 3)], ["rmse", f(d.rmse, 3)], ["missing", String(d.missing)]].forEach(([k, v], i) => {
        T(2, 1 + i * 1.6, k, "mid", 13);
        T(8, 1 + i * 1.6, v, "hi", 13, { "font-weight": 600 });
      });
    }

    function draw() {
      svg.replaceChildren();
      names.forEach((name, i) => {
        const z = i * GAP + ghost[i] * 20, on = i === pick;
        const g = el("g", { opacity: (1 - 0.8 * ghost[i]).toFixed(2) }, svg);
        const fill = ghost[i] > 0.5 ? "none" : C(i === top ? "accent" : "plate");
        el("polygon", { points: pts(plate, z - 4), fill, stroke: C("lo"), "stroke-width": 0.9 }, g);
        el("polygon", { points: pts(plate, z), fill, stroke: C(on ? "mid" : "lo"), "stroke-width": 0.9 }, g);
        if (on) content(i, el("g", { transform: `matrix(${0.866 * S},${0.5 * S},${-0.866 * S},${0.5 * S},${CX},${TOP - z})` }, g), g, z);
        const [lx, ly] = P(16.5, -1.5, z);
        el("text", { x: lx + 14, y: ly + 4, fill: C(on ? "hi" : "mid"), "font-weight": on ? 600 : null }, g, name);
      });
      // the call: from the questions up to one Verification
      const [x0, yb] = P(-1.5, 6.5, 0), a = x0 - 22, ya = y0 + 40;
      el("path", { d: `M${a},${yb} V${ya} M${a - 3},${ya + 6} L${a},${ya} L${a + 3},${ya + 6}`, fill: "none", stroke: C("mid"), "stroke-width": 0.9 }, svg);
      label(svg, a - 6, ya - 8, "verify(None, mae, rmse).on(report)", "hi", "fig-mono");
      caption.innerHTML = `<b>${names[pick]}</b>: ${texts[pick]}`;
    }
    const lift = animation(() => {
      ghost = ghost.map((g, i) => g + ((i > pick ? 1 : 0) - g) * 0.2);
      draw();
      return ghost.some((g, i) => Math.abs((i > pick ? 1 : 0) - g) > 0.01);
    });
    const choose = next => { next = Math.min(top, Math.max(0, next)); if (next !== pick) { pick = next; lift(); } };
    const corner = P(16.5, -1.5, 0)[1];
    svg.addEventListener("pointermove", e => choose(Math.round((corner - at(svg, e).y) / GAP)));
    svg.addEventListener("pointerleave", () => choose(top));
    svg.addEventListener("keydown", e => {
      const step = { ArrowDown: -1, ArrowUp: 1 }[e.key];
      if (step) { e.preventDefault(); choose(pick + step); }
    });
    draw();
  }

  const KINDS = { errors, contingency, fss, ensemble, skill, words, jargon, steps };

  function mount(figure) {
    if (figure.dataset.mounted) return;
    figure.dataset.mounted = "1";
    KINDS[figure.dataset.kind](figure, JSON.parse(figure.querySelector("script[type='application/json']").textContent));
  }
  const all = () => document.querySelectorAll("figure.fig").forEach(mount);
  // with instant navigation the page changes without a reload
  if (window.document$) window.document$.subscribe(all);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", all);
  else all();
})();
