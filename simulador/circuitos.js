(function (global) {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function txt(parent, x, y, s, cls, anchor) {
    const t = el("text", { x, y, class: cls || "c-lbl", "text-anchor": anchor || "middle" }, parent);
    t.textContent = s;
    return t;
  }

  const LOGICA = {
    original: (a, b, c, d) => (a || (b && c) || d ? 1 : 0),
    pos: (a, b, c, d) => (a | b | c | d) & (a | b | (1 - c) | d) & (a | (1 - b) | c | d),
    simplificada: (a, b, c, d) => a | (b & c) | d,
    nand: (a, b, c, d) => {
      const nand = (...x) => 1 - x.reduce((p, q) => p & q, 1);
      return nand(nand(a, a), nand(b, c), nand(d, d));
    },
  };
  const MINTERMOS = [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];

  const CIRCUITOS = {
    simplificado: {
      titulo: "Circuito simplificado: S = A + B·C + D",
      w: 470, h: 215,
      rails: [
        { name: "A", x: 40, y0: 34, y1: 200 },
        { name: "B", x: 70, y0: 34, y1: 200 },
        { name: "C", x: 100, y0: 34, y1: 200 },
        { name: "D", x: 130, y0: 34, y1: 200 },
      ],
      gates: [
        { id: "g1", type: "AND", x: 180, y: 95, h: 50, inputs: [{ src: "B" }, { src: "C" }], label: "B·C" },
        { id: "g2", type: "OR", x: 320, y: 75, h: 100, inputs: [
          { src: "A", tapY: 55, bendX: 295 }, { src: "g1" }, { src: "D", tapY: 185, bendX: 295 }] },
      ],
      out: { src: "g2" },
    },
    original: {
      titulo: "Circuito original (forma canônica POS): S = (A+B+C+D)·(A+B+C'+D)·(A+B'+C+D)",
      w: 640, h: 500,
      rails: [
        { name: "A", x: 40, y0: 30, y1: 480 },
        { name: "B", x: 75, y0: 30, y1: 480 },
        { name: "C", x: 110, y0: 30, y1: 480 },
        { name: "D", x: 145, y0: 30, y1: 480 },
        { name: "B'", x: 255, y0: 0, y1: 480, from: "nB" },
        { name: "C'", x: 285, y0: 0, y1: 480, from: "nC" },
      ],
      gates: [
        { id: "nB", type: "NOT", x: 180, y: 46, h: 26, inputs: [{ src: "B" }] },
        { id: "nC", type: "NOT", x: 180, y: 86, h: 26, inputs: [{ src: "C" }] },
        { id: "o1", type: "OR", x: 340, y: 125, h: 100, label: "M0",
          inputs: [{ src: "A" }, { src: "B" }, { src: "C" }, { src: "D" }] },
        { id: "o2", type: "OR", x: 340, y: 245, h: 100, label: "M2",
          inputs: [{ src: "A" }, { src: "B" }, { src: "C'" }, { src: "D" }] },
        { id: "o3", type: "OR", x: 340, y: 365, h: 100, label: "M4",
          inputs: [{ src: "A" }, { src: "B'" }, { src: "C" }, { src: "D" }] },
        { id: "a1", type: "AND", x: 490, y: 245, h: 100, inputs: [
          { src: "o1", bendX: 455 }, { src: "o2", bendX: 440 }, { src: "o3", bendX: 455 }] },
      ],
      out: { src: "a1" },
    },
    nand: {
      titulo: "Circuito só com NAND (De Morgan): S = [ A' · (B·C)' · D' ]'",
      w: 480, h: 250,
      rails: [
        { name: "A", x: 40, y0: 30, y1: 235 },
        { name: "B", x: 70, y0: 30, y1: 235 },
        { name: "C", x: 100, y0: 30, y1: 235 },
        { name: "D", x: 130, y0: 30, y1: 235 },
      ],
      gates: [
        { id: "n1", type: "NAND", x: 185, y: 45, h: 44, inputs: [{ src: "A" }, { src: "A" }], label: "A'" },
        { id: "n2", type: "NAND", x: 185, y: 110, h: 44, inputs: [{ src: "B" }, { src: "C" }], label: "(BC)'" },
        { id: "n3", type: "NAND", x: 185, y: 175, h: 44, inputs: [{ src: "D" }, { src: "D" }], label: "D'" },
        { id: "n4", type: "NAND", x: 330, y: 87, h: 90, inputs: [
          { src: "n1", bendX: 300 }, { src: "n2" }, { src: "n3", bendX: 300 }] },
      ],
      out: { src: "n4" },
    },
  };

  const GW = 60;
  const temBolha = (g) => g.type === "NOT" || g.type === "NAND";
  function pinos(g) {
    const n = g.inputs.length;
    if (g.type === "NOT") return [g.y + g.h / 2];
    return g.inputs.map((_, i) => g.y + (g.h * (i + 1)) / (n + 1));
  }
  function pinoX(g, y) {
    if (g.type !== "OR") return g.x;
    const t = (y - g.y) / g.h;
    return g.x + 2 * t * (1 - t) * GW * 0.25;
  }
  const saida = (g) => ({ x: g.x + GW, y: g.y + g.h / 2 });

  function desenharPorta(svg, g, on) {
    const { x, y, h } = g;
    const bw = temBolha(g) ? GW - 8 : GW;
    const cls = "c-gate" + (on ? " on" : "");
    let d;
    if (g.type === "AND" || g.type === "NAND") {
      const r = h / 2;
      d = `M${x},${y} H${x + bw - r} A${r},${r} 0 0 1 ${x + bw - r},${y + h} H${x} Z`;
    } else if (g.type === "OR") {
      d = `M${x},${y} Q${x + bw * 0.25},${y + h / 2} ${x},${y + h} Q${x + bw * 0.65},${y + h} ${x + bw},${y + h / 2} Q${x + bw * 0.65},${y} ${x},${y} Z`;
    } else {
      d = `M${x},${y} L${x},${y + h} L${x + bw},${y + h / 2} Z`;
    }
    el("path", { d, class: cls }, svg);
    if (temBolha(g)) el("circle", { cx: x + bw + 4, cy: y + h / 2, r: 4, class: cls }, svg);
    const nome = g.type === "NOT" ? "NOT" : g.type;
    txt(svg, x + (g.type === "OR" ? bw * 0.45 : bw * 0.4), y + h / 2 + 4, nome, "c-gname");
    if (g.label) txt(svg, x + bw / 2, y - 5, g.label, "c-small");
  }

  function linha(svg, pts, on) {
    el("polyline", { points: pts.map((p) => p.join(",")).join(" "), class: "c-wire" + (on ? " on" : "") }, svg);
  }

  function renderCircuito(container, nome, ent) {
    const def = CIRCUITOS[nome];
    const val = { A: ent[0], B: ent[1], C: ent[2], D: ent[3] };
    const gate = {};
    for (const g of def.gates) {
      gate[g.id] = g;
      const v = g.inputs.map((i) => val[i.src]);
      const and = v.reduce((p, q) => p & q, 1);
      const or = v.reduce((p, q) => p | q, 0);
      val[g.id] = { AND: and, NAND: 1 - and, OR: or, NOT: 1 - v[0] }[g.type];
      for (const r of def.rails) if (r.from === g.id) val[r.name] = val[g.id];
    }

    container.innerHTML = "";
    const svg = el("svg", { viewBox: `0 0 ${def.w} ${def.h}`, class: "c-svg", role: "img",
      "aria-label": def.titulo }, container);
    const rail = Object.fromEntries(def.rails.map((r) => [r.name, r]));

    for (const r of def.rails) {
      let y0 = r.y0;
      if (r.from) {
        const o = saida(gate[r.from]);
        y0 = o.y;
        linha(svg, [[o.x, o.y], [r.x, o.y]], val[r.name]);
        el("circle", { cx: r.x, cy: y0, r: 2.5, class: "c-dot" + (val[r.name] ? " on" : "") }, svg);
        txt(svg, r.x + 2, y0 - 7, r.name, "c-in", "start");
      } else {
        txt(svg, r.x, 16, `${r.name}=${val[r.name]}`, "c-in");
      }
      linha(svg, [[r.x, y0 + (r.from ? 0 : 6)], [r.x, r.y1]], val[r.name]);
    }

    for (const g of def.gates) {
      const ys = pinos(g);
      g.inputs.forEach((inp, i) => {
        const py = ys[i], px = pinoX(g, py), on = val[inp.src];
        if (rail[inp.src]) {
          const r = rail[inp.src], ty = inp.tapY != null ? inp.tapY : py;
          const pts = [[r.x, ty]];
          if (ty !== py) { const bx = inp.bendX != null ? inp.bendX : px - 20; pts.push([bx, ty], [bx, py]); }
          pts.push([px, py]);
          linha(svg, pts, on);
          el("circle", { cx: r.x, cy: ty, r: 3, class: "c-dot" + (on ? " on" : "") }, svg);
        } else {
          const o = saida(gate[inp.src]);
          const pts = [[o.x, o.y]];
          if (o.y !== py) { const bx = inp.bendX != null ? inp.bendX : px - 20; pts.push([bx, o.y], [bx, py]); }
          pts.push([px, py]);
          linha(svg, pts, on);
        }
      });
    }

    for (const g of def.gates) {
      desenharPorta(svg, g, val[g.id]);
      const o = saida(g);
      if (g.type !== "NOT") txt(svg, o.x + 4, o.y - 6, String(val[g.id]), "c-val", "start");
    }

    const o = saida(gate[def.out.src]);
    const s = val[def.out.src];
    linha(svg, [[o.x, o.y], [o.x + 34, o.y]], s);
    el("circle", { cx: o.x + 46, cy: o.y, r: 12, class: "c-led" + (s ? " on" : "") }, svg);
    txt(svg, o.x + 46, o.y + 30, `S=${s}`, "c-out");
    return s;
  }

  const GRAY = ["00", "01", "11", "10"];
  function renderKmap(container, destaque) {
    const cs = 56, x0 = 92, y0 = 64;
    container.innerHTML = "";
    const svg = el("svg", { viewBox: "0 0 330 300", class: "c-svg k-svg", role: "img",
      "aria-label": "Mapa de Karnaugh de S com os agrupamentos A, D e BC" }, container);
    txt(svg, x0 - 22, y0 - 26, "AB \\ CD", "c-small");
    GRAY.forEach((g, j) => txt(svg, x0 + j * cs + cs / 2, y0 - 10, g, "c-lbl"));
    GRAY.forEach((g, i) => txt(svg, x0 - 20, y0 + i * cs + cs / 2 + 5, g, "c-lbl"));
    const celulas = [];
    GRAY.forEach((ab, i) => GRAY.forEach((cd, j) => {
      const m = parseInt(ab + cd, 2);
      const x = x0 + j * cs, y = y0 + i * cs;
      el("rect", { x, y, width: cs, height: cs, class: "k-cell" + (m === destaque ? " hl" : "") }, svg);
      celulas.push([m, x, y]);
    }));
    const grupos = [
      { r: 2, c: 0, h: 2, w: 4, ins: 4, cls: "k-g1" },
      { r: 0, c: 1, h: 4, w: 2, ins: 8, cls: "k-g2" },
      { r: 1, c: 2, h: 2, w: 2, ins: 13, cls: "k-g3" },
    ];
    for (const g of grupos) {
      el("rect", { x: x0 + g.c * cs + g.ins, y: y0 + g.r * cs + g.ins, width: g.w * cs - 2 * g.ins,
        height: g.h * cs - 2 * g.ins, rx: 12, class: "k-grp " + g.cls }, svg);
    }
    for (const [m, x, y] of celulas) {
      txt(svg, x + cs / 2, y + cs / 2 + 7, MINTERMOS.includes(m) ? "1" : "0", "k-val");
      txt(svg, x + cs / 2, y + cs - 6, "m" + m, "k-m");
    }
    return svg;
  }

  global.CircuitosCA = { LOGICA, MINTERMOS, CIRCUITOS, renderCircuito, renderKmap };
})(window);
