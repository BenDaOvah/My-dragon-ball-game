"use client";

import { useEffect, useRef, useState, useCallback } from "react";

/* ===========================================================================
 * DRAGON ARENA — a Sparking! ZERO-style 2.5D arena fighter demo
 *
 * Implements the design blueprint in /Dragon_Ball_Game_Design_Blueprint.pdf:
 *   • Canon power levels (Goku 416 base / Vegeta 18,000 base) with the
 *     log-scaled combat-ratio damage formula from Chapter 5.
 *   • Ki as the universal economy (Chapter 3.2): blast, dash, transform, all
 *     spend Ki; K holds to charge.
 *   • Movement as backbone (Chapter 3.1): walk / fly / Dragon Dash (Ki-cost).
 *   • Layered counters (Chapter 3.3): Guard (free), Super Perception (timed,
 *     free, triggers Sonic Sway), counter-blast (2 Skill Count).
 *   • Sparking! Mode climax (Chapter 3.4): gauge + Skill Count → free Ki +
 *     Ultimate Blast.
 *   • Mid-battle transformation (Chapter 7): Skill Count cost + Ki-upkeep.
 *
 * Architecture: all game logic is in module-level pure functions that take the
 * mutable game-state object `S`. The React component only owns the canvas ref,
 * the input listeners, the rAF loop, and the JSX. This keeps the hot path
 * allocation-free and avoids React re-render churn during the 60fps loop.
 * =========================================================================== */

type KeySet = { [k: string]: boolean };

type FormDef = {
  name: string;
  plMul: number;
  aura: string | null;
  hairColor: string;
  upkeepPerSec: number;
  spark?: boolean;
};

type Fighter = {
  name: string;
  color: string;
  skin: string;
  hairBase: string;
  isPlayer: boolean;
  x: number; y: number; vx: number; vy: number;
  facing: 1 | -1;
  onGround: boolean;
  hp: number; maxHp: number;
  ki: number; maxKi: number;
  kiChargeHold: boolean;
  skillCount: number; maxSkill: number; skillProgress: number;
  sparkingGauge: number; maxSparking: number;
  sparkingActive: boolean; sparkingTimer: number;
  basePL: number;
  formIdx: number;
  forms: FormDef[];
  state: string;
  stateTimer: number;
  attackPhase: string | null;
  attackPhaseTimer: number;
  currentMove: MoveDef | null;
  rushChain: number;
  rushChainTimer: number;
  hitstun: number;
  invuln: number;
  guardHold: boolean;
  guardStamina: number;
  counterWindow: number;
  counterType: "perception" | null;
  transformFlash: number;
  flashHit: number;
  aiThink: number;
  aiAction: string;
  _hitThisMove?: boolean;
};

type MoveDef = {
  name: string;
  type: "rush" | "smash" | "ki" | "ultimate" | "vanishing";
  baseDamage: number;
  kiCost: number;
  startup: number; active: number; recovery: number;
  reach: number;
  knockback: number;
  hitstun: number;
};

type Projectile = {
  x: number; y: number; vx: number; vy: number;
  owner: "player" | "enemy";
  damage: number;
  life: number;
  color: string;
  size: number;
  chargeLevel: number;
};

type Particle = {
  x: number; y: number; vx: number; vy: number;
  life: number; maxLife: number;
  color: string; size: number;
  gravity: number;
};

type Effect = {
  type: "hit" | "smash" | "transform" | "block" | "counter" | "ultimate";
  x: number; y: number;
  life: number; maxLife: number;
  color: string; size: number;
};

type GameState = {
  player: Fighter; enemy: Fighter;
  projectiles: Projectile[]; particles: Particle[]; effects: Effect[];
  keys: KeySet; justPressed: Set<string>;
  timer: number; combo: number; comboTimer: number;
  shake: number; cameraX: number;
  roundOver: boolean; roundResult: string;
  paused: boolean;
  frame: number;
};

/* ----------------------------- constants ----------------------------- */
const W = 960, H = 540;
const GROUND_Y = 440;
const GRAVITY = 0.55;
const ARENA_LEFT = 40, ARENA_RIGHT = 920;
const FIGHTER_W = 36, FIGHTER_H = 70;

export const PALETTE = {
  bg0: "#05060f",
  bg1: "#0a0e1a",
  bg2: "#131826",
  ground: "#1a2030",
  groundLine: "#3a5a8a",
  text: "#e6eaf2",
  muted: "#8a94a8",
  accent: "#00e5ff",
  orange: "#ff8c2a",
  yellow: "#f9f871",
  green: "#39ff14",
  pink: "#ff2d95",
  red: "#ff3b3b",
  purple: "#b14dff",
};

const GOKU_FORMS: FormDef[] = [
  { name: "Base",          plMul: 1,  aura: null,     hairColor: "#111111", upkeepPerSec: 0 },
  { name: "Kaio-ken",      plMul: 4,  aura: "#ff3b3b", hairColor: "#111111", upkeepPerSec: 4 },
  { name: "Super Saiyan",  plMul: 50, aura: "#f9f871", hairColor: "#f9f871", upkeepPerSec: 7, spark: true },
];
const VEGETA_FORMS: FormDef[] = [
  { name: "Base",          plMul: 1,  aura: null,     hairColor: "#111111", upkeepPerSec: 0 },
  { name: "Super Saiyan",  plMul: 50, aura: "#f9f871", hairColor: "#f9f871", upkeepPerSec: 7, spark: true },
];

const MOVES: { [k: string]: MoveDef } = {
  rush1:   { name: "Rush 1",         type: "rush",     baseDamage: 32,  kiCost: 0,  startup: 7,  active: 4, recovery: 12, reach: 70, knockback: 4,  hitstun: 14 },
  rush2:   { name: "Rush 2",         type: "rush",     baseDamage: 30,  kiCost: 0,  startup: 8,  active: 4, recovery: 12, reach: 70, knockback: 4,  hitstun: 14 },
  rush3:   { name: "Rush 3",         type: "rush",     baseDamage: 34,  kiCost: 0,  startup: 9,  active: 4, recovery: 14, reach: 72, knockback: 6,  hitstun: 16 },
  rush4:   { name: "Rush Finisher",  type: "rush",     baseDamage: 48,  kiCost: 0,  startup: 11, active: 5, recovery: 18, reach: 74, knockback: 14, hitstun: 22 },
  smash:   { name: "Smash",          type: "smash",    baseDamage: 58,  kiCost: 0,  startup: 16, active: 6, recovery: 22, reach: 78, knockback: 22, hitstun: 28 },
  kiblast: { name: "Ki Blast",       type: "ki",       baseDamage: 40,  kiCost: 14, startup: 8,  active: 3, recovery: 14, reach: 0,  knockback: 3,  hitstun: 8 },
  ultimate:{ name: "Kamehameha",     type: "ultimate", baseDamage: 320, kiCost: 0,  startup: 24, active: 10, recovery: 30, reach: 0,  knockback: 30, hitstun: 40 },
};

/* ===========================================================================
 * PURE GAME LOGIC (module-level)
 * =========================================================================== */

function effectivePL(f: Fighter): number {
  return f.basePL * f.forms[f.formIdx].plMul;
}

function combatRatioDamage(attacker: Fighter, defender: Fighter, base: number): number {
  const ratio = effectivePL(attacker) / Math.max(effectivePL(defender), 1);
  const ratioScale = Math.log10(ratio + 9);
  return Math.round(base * ratioScale);
}

function makeGoku(isPlayer: boolean): Fighter {
  return {
    name: "GOKU", color: "#ff8c2a", skin: "#f0c8a0", hairBase: "#111111",
    isPlayer,
    x: 280, y: GROUND_Y, vx: 0, vy: 0, facing: 1, onGround: true,
    hp: 1000, maxHp: 1000, ki: 60, maxKi: 100, kiChargeHold: false,
    skillCount: 1, maxSkill: 4, skillProgress: 0,
    sparkingGauge: 0, maxSparking: 100, sparkingActive: false, sparkingTimer: 0,
    basePL: 416, formIdx: 0, forms: GOKU_FORMS,
    state: "idle", stateTimer: 0, attackPhase: null, attackPhaseTimer: 0, currentMove: null,
    rushChain: 0, rushChainTimer: 0, hitstun: 0, invuln: 0,
    guardHold: false, guardStamina: 100, counterWindow: 0, counterType: null,
    transformFlash: 0, flashHit: 0,
    aiThink: 0, aiAction: "approach",
  };
}

function makeVegeta(isPlayer: boolean): Fighter {
  return {
    name: "VEGETA", color: "#4dd0e1", skin: "#f0c8a0", hairBase: "#111111",
    isPlayer,
    x: 680, y: GROUND_Y, vx: 0, vy: 0, facing: -1, onGround: true,
    hp: 1000, maxHp: 1000, ki: 60, maxKi: 100, kiChargeHold: false,
    skillCount: 1, maxSkill: 4, skillProgress: 0,
    sparkingGauge: 0, maxSparking: 100, sparkingActive: false, sparkingTimer: 0,
    basePL: 18000, formIdx: 0, forms: VEGETA_FORMS,
    state: "idle", stateTimer: 0, attackPhase: null, attackPhaseTimer: 0, currentMove: null,
    rushChain: 0, rushChainTimer: 0, hitstun: 0, invuln: 0,
    guardHold: false, guardStamina: 100, counterWindow: 0, counterType: null,
    transformFlash: 0, flashHit: 0,
    aiThink: 0, aiAction: "approach",
  };
}

function makeInitialState(): GameState {
  return {
    player: makeGoku(true),
    enemy: makeVegeta(false),
    projectiles: [], particles: [], effects: [],
    keys: {}, justPressed: new Set(),
    timer: 90 * 60, combo: 0, comboTimer: 0,
    shake: 0, cameraX: 0,
    roundOver: false, roundResult: "",
    paused: false, frame: 0,
  };
}

function pushParticle(S: GameState, x:number,y:number,vx:number,vy:number,life:number,maxLife:number,color:string,size:number,g:number) {
  S.particles.push({ x,y,vx,vy,life,maxLife,color,size,gravity:g });
  if (S.particles.length > 200) S.particles.shift();
}
function pushEffect(S: GameState, e: Effect) { S.effects.push(e); if (S.effects.length > 30) S.effects.shift(); }

function endRound(S: GameState, res: string, onEnd?: (r:string)=>void) {
  if (S.roundOver) return;
  S.roundOver = true; S.roundResult = res;
  if (onEnd) onEnd(res);
}

function startMove(S: GameState, f: Fighter, m: MoveDef) {
  f.state = "attack"; f.currentMove = m; f.attackPhase = "startup"; f.attackPhaseTimer = m.startup;
  f._hitThisMove = false;
}

function fireKiBlast(S: GameState, f: Fighter, opp: Fighter) {
  const chargeLevel = f.sparkingActive ? 2 : 1;
  const dmg = combatRatioDamage(f, opp, MOVES.kiblast.baseDamage) * (chargeLevel === 2 ? 1.6 : 1);
  S.projectiles.push({
    x: f.x + f.facing * 20, y: f.y - 35, vx: f.facing * 9, vy: 0,
    owner: f.isPlayer ? "player" : "enemy",
    damage: Math.round(dmg), life: 90, color: f.forms[f.formIdx].aura || PALETTE.accent,
    size: 6 + chargeLevel * 2, chargeLevel,
  });
}

function fireUltimate(S: GameState, f: Fighter, opp: Fighter) {
  const dmg = combatRatioDamage(f, opp, MOVES.ultimate.baseDamage);
  S.projectiles.push({
    x: f.x + f.facing * 20, y: f.y - 35, vx: f.facing * 14, vy: 0,
    owner: f.isPlayer ? "player" : "enemy",
    damage: Math.round(dmg), life: 50, color: f.forms[f.formIdx].aura || PALETTE.yellow,
    size: 22, chargeLevel: 3,
  });
  f.sparkingActive = false;
  S.shake = 18;
}

function resolveMeleeHit(S: GameState, atk: Fighter, def: Fighter, m: MoveDef) {
  atk._hitThisMove = true;
  // Super Perception counter
  if (def.counterWindow > 0 && def.counterType === "perception") {
    atk.ki = Math.max(0, atk.ki - 25);
    def.counterWindow = 0;
    pushEffect(S, { type: "counter", x: def.x, y: def.y - 40, life: 24, maxLife: 24, color: PALETTE.accent, size: 40 });
    atk.vx = -atk.facing * 6; atk.state = "hitstun"; atk.hitstun = 18;
    S.shake = 6;
    if (def.sparkingGauge < def.maxSparking) def.sparkingGauge += 12;
    return;
  }
  // Guard
  if (def.guardHold && def.guardStamina > 0) {
    def.guardStamina = Math.max(0, def.guardStamina - 12);
    pushEffect(S, { type: "block", x: (atk.x+def.x)/2, y: def.y - 35, life: 12, maxLife: 12, color: PALETTE.accent, size: 30 });
    atk.vx = -atk.facing * 2;
    if (atk.sparkingGauge < atk.maxSparking) atk.sparkingGauge += 4;
    return;
  }
  // Damage
  const dmg = combatRatioDamage(atk, def, m.baseDamage);
  def.hp = Math.max(0, def.hp - dmg);
  def.state = "hitstun"; def.hitstun = m.hitstun;
  def.vx = atk.facing * m.knockback * 0.6; def.vy = -2.5; def.onGround = false;
  def.flashHit = 8; def.invuln = 6;
  pushEffect(S, { type: m.type === "smash" ? "smash" : "hit", x: (atk.x+def.x)/2, y: def.y - 35, life: 16, maxLife: 16, color: PALETTE.yellow, size: m.type === "smash" ? 50 : 30 });
  if (atk.sparkingGauge < atk.maxSparking) atk.sparkingGauge += m.type === "smash" ? 14 : 8;
  if (def.sparkingGauge < def.maxSparking) def.sparkingGauge += 5;
  if (atk.isPlayer) { S.combo++; S.comboTimer = 90; }
  S.shake = m.type === "smash" ? 10 : 4;
  for (let i=0;i<8;i++) pushParticle(S, (atk.x+def.x)/2, def.y - 35 + (Math.random()-0.5)*20,
    (Math.random()-0.5)*6, -Math.random()*4 - 1, 22, 22, Math.random()>0.5?PALETTE.yellow:PALETTE.orange, 3, 0.2);
}

function handleActionInput(S: GameState, f: Fighter, opp: Fighter, jp: Set<string>) {
  // REVENGE COUNTER (burst): while being combo'd (in hitstun), pressing E
  // spends 1 Skill Count to instantly break out — the blueprint Ch.3.3
  // "panic button once you're actually being combo'd." Without this, getting
  // caught in a combo was inescapable (combined with the state-exit bug, a
  // single hit could softlock the fighter).
  if (f.state === "hitstun") {
    if (jp.has("e") && f.skillCount >= 1) {
      f.skillCount -= 1;
      f.hitstun = 0; f.state = "idle";
      f.invuln = 30;           // brief i-frames to escape the combo
      f.vx = -f.facing * 6;    // back off from the attacker
      f.vy = -6; f.onGround = false;
      pushEffect(S, { type: "counter", x: f.x, y: f.y - 35, life: 26, maxLife: 26, color: PALETTE.purple, size: 44 });
      S.shake = 8;
    }
    return; // no other actions while in hitstun
  }
  if (f.state === "attack" || f.state === "transform") return;
  if (jp.has("p")) {
    const chainIdx = Math.min(f.rushChain, 3);
    const moveKey = ["rush1","rush2","rush3","rush4"][chainIdx];
    startMove(S, f, MOVES[moveKey]);
    f.rushChain = chainIdx + 1; f.rushChainTimer = 40;
    return;
  }
  if (jp.has("i")) { startMove(S, f, MOVES.smash); return; }
  if (jp.has("j") && f.ki >= MOVES.kiblast.kiCost) {
    f.ki -= MOVES.kiblast.kiCost; startMove(S, f, MOVES.kiblast); return;
  }
  if (jp.has("l") && f.skillCount >= 1 && f.formIdx < f.forms.length - 1) {
    f.skillCount -= 1; f.formIdx++;
    f.state = "transform"; f.stateTimer = 28; f.transformFlash = 28;
    f.ki = Math.min(f.maxKi, f.ki + 30);
    pushEffect(S, { type: "transform", x: f.x, y: f.y - 30, life: 40, maxLife: 40, color: f.forms[f.formIdx].aura || PALETTE.yellow, size: 70 });
    S.shake = 8; return;
  }
  if ((jp.has("enter") || jp.has("=")) && !f.sparkingActive && f.sparkingGauge >= f.maxSparking && f.skillCount >= 1) {
    f.sparkingActive = true; f.sparkingTimer = 600; f.skillCount -= 1; f.sparkingGauge = 0; f.ki = f.maxKi;
    f.state = "sparking"; f.stateTimer = 20; f.transformFlash = 20;
    pushEffect(S, { type: "transform", x: f.x, y: f.y - 30, life: 50, maxLife: 50, color: PALETTE.yellow, size: 100 });
    S.shake = 14; return;
  }
  if (jp.has("u") && f.sparkingActive) { startMove(S, f, MOVES.ultimate); return; }
  if (jp.has("e") && f.counterWindow <= 0) {
    f.counterWindow = 14; f.counterType = "perception";
    pushEffect(S, { type: "block", x: f.x, y: f.y - 40, life: 14, maxLife: 14, color: PALETTE.accent, size: 28 });
  }
}

function aiThink(S: GameState, f: Fighter, opp: Fighter) {
  f.aiThink--;
  const dist = Math.abs(opp.x - f.x);
  const dirToOpp = (opp.x < f.x ? -1 : 1) as 1 | -1;
  f.facing = dirToOpp;

  // Phase 2: transform at half HP
  if (f.name === "VEGETA" && f.hp < f.maxHp * 0.5 && f.formIdx === 0 && f.skillCount >= 1) {
    f.skillCount -= 1; f.formIdx = 1; f.state = "transform"; f.stateTimer = 28; f.transformFlash = 28;
    f.ki = Math.min(f.maxKi, f.ki + 30);
    pushEffect(S, { type: "transform", x: f.x, y: f.y - 30, life: 40, maxLife: 40, color: PALETTE.yellow, size: 70 });
    S.shake = 8; return;
  }
  if (!f.sparkingActive && f.sparkingGauge >= f.maxSparking && f.skillCount >= 1 && f.hp < f.maxHp * 0.4) {
    f.sparkingActive = true; f.sparkingTimer = 480; f.skillCount -= 1; f.sparkingGauge = 0; f.ki = f.maxKi;
    f.state = "sparking"; f.stateTimer = 20; f.transformFlash = 20;
    pushEffect(S, { type: "transform", x: f.x, y: f.y - 30, life: 50, maxLife: 50, color: PALETTE.yellow, size: 100 });
    S.shake = 14; return;
  }
  if (f.state === "attack" || f.state === "hitstun" || f.state === "transform") {
    f.guardHold = false; f.kiChargeHold = false; return;
  }
  if (f.aiThink > 0) {
    if (f.aiAction === "approach") { f.vx = dirToOpp * 2.6; f.state = "walk"; }
    else if (f.aiAction === "retreat") { f.vx = -dirToOpp * 2.6; f.state = "walk"; }
    else if (f.aiAction === "guard") { f.guardHold = true; f.state = "idle"; }
    else if (f.aiAction === "charge") { f.kiChargeHold = true; f.state = "idle"; }
    return;
  }
  f.aiThink = 40 + Math.floor(Math.random() * 50);
  if (f.ki < 30 && Math.random() < 0.5) { f.aiAction = "charge"; return; }
  if (dist < 90) {
    const r = Math.random();
    if (r < 0.55) {
      if (f.ki >= MOVES.kiblast.kiCost && Math.random() < 0.3) {
        f.ki -= MOVES.kiblast.kiCost; startMove(S, f, MOVES.kiblast);
      } else if (f.sparkingActive && Math.random() < 0.12) {
        startMove(S, f, MOVES.ultimate);
      } else {
        const chainIdx = Math.min(f.rushChain, 3);
        startMove(S, f, MOVES[["rush1","rush2","rush3","rush4"][chainIdx]]);
        f.rushChain = chainIdx + 1; f.rushChainTimer = 40;
      }
      f.aiThink = 30;
    } else if (r < 0.7) { f.aiAction = "guard"; f.aiThink = 25; }
    else if (r < 0.85) { f.aiAction = "retreat"; f.aiThink = 20; }
    else { f.aiAction = "approach"; f.aiThink = 15; }
  } else {
    if (f.ki >= MOVES.kiblast.kiCost && Math.random() < 0.35) {
      f.ki -= MOVES.kiblast.kiCost; startMove(S, f, MOVES.kiblast); f.aiThink = 35;
    } else if (f.ki >= 8 && Math.random() < 0.25) {
      f.vx = dirToOpp * 7; f.ki -= 5; f.state = "dash"; f.aiThink = 18;
    } else { f.aiAction = "approach"; }
  }
}

function updateFighter(S: GameState, f: Fighter, opp: Fighter, isPlayer: boolean) {
  const keys = S.keys;
  const jp = S.justPressed;

  if (f.stateTimer > 0) f.stateTimer--;
  if (f.hitstun > 0) f.hitstun--;
  if (f.invuln > 0) f.invuln--;
  if (f.flashHit > 0) f.flashHit--;
  if (f.transformFlash > 0) f.transformFlash--;
  if (f.counterWindow > 0) f.counterWindow--;
  if (f.rushChainTimer > 0) { f.rushChainTimer--; if (f.rushChainTimer === 0) f.rushChain = 0; }
  if (f.guardStamina < 100 && !f.guardHold) f.guardStamina = Math.min(100, f.guardStamina + 0.4);

  // STATE-EXIT (bug fix): when a locked-state timer expires, return the
  // fighter to a controllable state. Previously the state never reset, so a
  // single hit (or one transform/sparking activation) permanently locked the
  // fighter in "hitstun"/"transform"/"sparking" — the "can't move after one
  // hit" bug. The form/sparking bonus persists; only the locked animation ends.
  if (f.hitstun === 0 && f.state === "hitstun") f.state = f.onGround ? "idle" : "jump";
  if (f.stateTimer === 0 && (f.state === "transform" || f.state === "sparking")) {
    f.state = f.onGround ? "idle" : "jump";
  }

  if (f.sparkingActive) {
    f.sparkingTimer--;
    if (f.sparkingTimer <= 0) {
      f.sparkingActive = false;
      pushEffect(S, { type: "transform", x: f.x, y: f.y - 30, life: 30, maxLife: 30, color: PALETTE.yellow, size: 60 });
    }
  } else {
    f.skillProgress += 0.18;
    if (f.skillProgress >= 100) { f.skillProgress = 0; if (f.skillCount < f.maxSkill) f.skillCount++; }
    if (f.sparkingGauge < f.maxSparking && f.ki >= f.maxKi) f.sparkingGauge += 0.3;
  }

  const form = f.forms[f.formIdx];
  if (f.formIdx > 0 && !f.sparkingActive) {
    f.ki = Math.max(0, f.ki - (form.upkeepPerSec / 60));
    if (f.ki <= 0) {
      f.formIdx = 0; f.transformFlash = 20;
      pushEffect(S, { type: "transform", x: f.x, y: f.y - 30, life: 25, maxLife: 25, color: PALETTE.muted, size: 50 });
    }
  }

  if (f.kiChargeHold && f.state !== "hitstun" && f.state !== "attack" && !f.guardHold) {
    const rate = f.sparkingActive ? 0 : 1.6;
    f.ki = Math.min(f.maxKi, f.ki + rate);
    if (S.frame % 3 === 0) {
      pushParticle(S, f.x + (Math.random()-0.5)*30, f.y - 30 - Math.random()*40,
        (Math.random()-0.5)*0.5, -1.5 - Math.random(), 20, 20, f.forms[f.formIdx].aura || PALETTE.accent, 2.5, 0);
    }
  }

  let moveX = 0, moveY = 0;
  let wantDash = false;
  if (isPlayer) {
    if (f.state !== "attack" && f.state !== "hitstun" && f.state !== "transform") {
      if (keys["a"] || keys["arrowleft"]) moveX = -1;
      if (keys["d"] || keys["arrowright"]) moveX = 1;
      if (keys["w"] || keys["arrowup"]) moveY = -1;
      if (keys["s"] || keys["arrowdown"]) moveY = 1;
      if ((keys["shift"] || keys["shiftleft"]) && (moveX !== 0 || moveY !== 0)) wantDash = true;
      f.guardHold = !!keys["o"];
      f.kiChargeHold = !!keys["k"] && !f.guardHold;
    } else { f.guardHold = false; f.kiChargeHold = false; }
    if (f.state === "idle" || f.state === "walk") {
      f.facing = (opp.x < f.x ? -1 : 1);
    }
    handleActionInput(S, f, opp, jp);
  } else {
    aiThink(S, f, opp);
  }

  if (f.guardHold) { f.guardStamina = Math.max(0, f.guardStamina - 0.5); if (f.guardStamina <= 0) f.guardHold = false; }

  const isLocked = f.state === "attack" || f.state === "hitstun" || f.state === "transform";
  if (!isLocked) {
    const speed = wantDash && f.ki >= 8 ? 7.5 : 3.2;
    if (wantDash && f.ki >= 8) f.ki -= 0.25;
    f.vx = moveX * speed;
    if (moveY < 0 && (f.sparkingActive || f.ki >= 0.3)) {
      f.vy = -4.5; if (!f.sparkingActive) f.ki = Math.max(0, f.ki - 0.15); f.onGround = false;
    } else if (moveY > 0 && !f.onGround) {
      f.vy = 4.5; f.onGround = false;
    } else if (f.onGround && moveY < 0) {
      f.vy = -10; f.onGround = false;
    }
    if (wantDash && moveX === 0 && moveY === 0) f.vx = f.facing * 7.5;
    if (f.state === "hitstun") f.vx *= 0.9;
    f.state = (moveX !== 0 || moveY !== 0 || wantDash) ? (wantDash ? "dash" : "walk") : "idle";
    if (!f.onGround) f.state = "jump";
  } else {
    f.vx *= 0.85;
    if (f.state === "hitstun") f.vx *= 0.92;
  }

  f.x += f.vx; f.y += f.vy;
  if (!f.onGround) f.vy += GRAVITY;
  if (f.y >= GROUND_Y) { f.y = GROUND_Y; f.vy = 0; f.onGround = true; }
  f.x = Math.max(ARENA_LEFT, Math.min(ARENA_RIGHT, f.x));

  if (f.currentMove && f.state === "attack") {
    f.attackPhaseTimer--;
    if (f.attackPhase === "startup" && f.attackPhaseTimer <= 0) {
      f.attackPhase = "active"; f.attackPhaseTimer = f.currentMove.active;
      if (f.currentMove.type === "ki") fireKiBlast(S, f, opp);
      if (f.currentMove.type === "ultimate") fireUltimate(S, f, opp);
    } else if (f.attackPhase === "active" && f.attackPhaseTimer <= 0) {
      f.attackPhase = "recovery"; f.attackPhaseTimer = f.currentMove.recovery;
    } else if (f.attackPhase === "recovery" && f.attackPhaseTimer <= 0) {
      f.attackPhase = null; f.currentMove = null; f.state = "idle";
    }
    if (f.attackPhase === "active" && f.currentMove && (f.currentMove.type === "rush" || f.currentMove.type === "smash")) {
      const reach = f.currentMove.reach;
      const dx = opp.x - f.x;
      const dy = (opp.y - 30) - (f.y - 30);
      const inReach = Math.abs(dx) < reach && f.facing === Math.sign(dx || 1) && Math.abs(dy) < 60;
      if (inReach && opp.invuln <= 0 && !f._hitThisMove) {
        resolveMeleeHit(S, f, opp, f.currentMove);
      }
    }
  }
}

function updateProjectiles(S: GameState) {
  const arr = S.projectiles;
  for (let i = arr.length - 1; i >= 0; i--) {
    const pr = arr[i];
    pr.x += pr.vx; pr.y += pr.vy; pr.life--;
    if (S.frame % 2 === 0) pushParticle(S, pr.x, pr.y, -pr.vx*0.2, 0, 14, 14, pr.color, pr.size*0.6, 0);
    if (pr.life <= 0 || pr.x < ARENA_LEFT-20 || pr.x > ARENA_RIGHT+20) { arr.splice(i,1); continue; }
    const target = pr.owner === "player" ? S.enemy : S.player;
    const dx = target.x - pr.x; const dy = (target.y - 35) - pr.y;
    if (Math.abs(dx) < FIGHTER_W/2 + pr.size && Math.abs(dy) < 45 && target.invuln <= 0) {
      if (target.counterWindow > 0 && target.counterType === "perception" && target.skillCount >= 2) {
        target.skillCount -= 2; target.counterWindow = 0;
        pushEffect(S, { type: "counter", x: target.x, y: target.y - 40, life: 28, maxLife: 28, color: PALETTE.accent, size: 50 });
        arr.splice(i,1); S.shake = 6; continue;
      }
      if (target.guardHold && target.guardStamina > 0) {
        target.guardStamina = Math.max(0, target.guardStamina - 10);
        pushEffect(S, { type: "block", x: pr.x, y: pr.y, life: 12, maxLife: 12, color: PALETTE.accent, size: 30 });
        arr.splice(i,1); continue;
      }
      target.hp = Math.max(0, target.hp - pr.damage);
      target.state = "hitstun"; target.hitstun = 18;
      target.vx = Math.sign(pr.vx) * 5; target.vy = -2; target.onGround = false;
      target.flashHit = 8; target.invuln = 8;
      const effType = pr.chargeLevel >= 3 ? "ultimate" : "hit";
      pushEffect(S, { type: effType, x: pr.x, y: pr.y, life: 24, maxLife: 24, color: pr.color, size: pr.size * 3 });
      S.shake = pr.chargeLevel >= 3 ? 22 : 6;
      if (target.sparkingGauge < target.maxSparking) target.sparkingGauge += 6;
      for (let j=0;j<10;j++) pushParticle(S, pr.x, pr.y, (Math.random()-0.5)*8, (Math.random()-0.5)*8 - 1, 24, 24, pr.color, 3, 0.15);
      arr.splice(i,1);
    }
  }
}

function updateParticles(S: GameState) {
  for (let i = S.particles.length - 1; i >= 0; i--) {
    const p = S.particles[i];
    p.x += p.vx; p.y += p.vy; p.vy += p.gravity; p.life--;
    if (p.life <= 0) S.particles.splice(i,1);
  }
}
function updateEffects(S: GameState) {
  for (let i = S.effects.length - 1; i >= 0; i--) {
    S.effects[i].life--; if (S.effects[i].life <= 0) S.effects.splice(i,1);
  }
}

function update(S: GameState, onEnd: (r:string)=>void) {
  if (S.frame % 60 === 0) S.timer = Math.max(0, S.timer - 1);
  if (S.timer === 0) endRound(S, "TIME UP", onEnd);
  if (S.shake > 0) S.shake *= 0.85;
  if (S.comboTimer > 0) { S.comboTimer--; if (S.comboTimer === 0) S.combo = 0; }

  updateFighter(S, S.player, S.enemy, true);
  updateFighter(S, S.enemy, S.player, false);
  updateProjectiles(S);
  updateParticles(S);
  updateEffects(S);

  if (S.player.hp <= 0) endRound(S, "DEFEAT", onEnd);
  else if (S.enemy.hp <= 0) endRound(S, "VICTORY", onEnd);

  S.justPressed.clear();
}

/* ===========================================================================
 * RENDER
 * =========================================================================== */
function fmtPL(n: number): string {
  if (n >= 1e9) return (n/1e9).toFixed(2) + "B";
  if (n >= 1e6) return (n/1e6).toFixed(2) + "M";
  if (n >= 1e3) return (n/1e3).toFixed(1) + "K";
  return String(Math.round(n));
}

function drawBars(ctx: CanvasRenderingContext2D, f: Fighter, x: number, y: number, left: boolean) {
  const W_BAR = 360;
  ctx.textAlign = left ? "left" : "right";
  ctx.font = "bold 12px 'Courier New', monospace";
  ctx.fillStyle = f.isPlayer ? PALETTE.orange : PALETTE.accent;
  ctx.fillText(f.name, x, y);
  ctx.font = "9px 'Courier New', monospace"; ctx.fillStyle = PALETTE.muted;
  ctx.fillText(" · " + f.forms[f.formIdx].name + " · " + fmtPL(effectivePL(f)) + " PL", left ? x + 60 : x - 60, y);

  const hpW = (f.hp / f.maxHp) * W_BAR;
  const hpX = left ? x : x - W_BAR;
  ctx.fillStyle = "rgba(20,20,30,0.9)"; ctx.fillRect(hpX, y+8, W_BAR, 14);
  ctx.strokeStyle = PALETTE.groundLine; ctx.lineWidth = 1; ctx.strokeRect(hpX, y+8, W_BAR, 14);
  const hpCol = f.hp > f.maxHp*0.3 ? PALETTE.green : PALETTE.red;
  const hpG = ctx.createLinearGradient(0,0,W_BAR,0);
  hpG.addColorStop(0, hpCol); hpG.addColorStop(1, "#ffffff44");
  ctx.fillStyle = hpG;
  if (left) ctx.fillRect(x, y+8, hpW, 14); else ctx.fillRect(x - hpW, y+8, hpW, 14);
  ctx.font = "8px 'Courier New', monospace"; ctx.fillStyle = PALETTE.text; ctx.textAlign = left?"left":"right";
  ctx.fillText(Math.ceil(f.hp) + " / " + f.maxHp, left? x + W_BAR - 50 : x - W_BAR + 50, y + 19);

  const kiW = (f.ki / f.maxKi) * W_BAR;
  ctx.fillStyle = "rgba(20,20,30,0.9)"; ctx.fillRect(hpX, y+26, W_BAR, 6);
  ctx.fillStyle = f.ki >= f.maxKi ? PALETTE.yellow : PALETTE.accent;
  if (left) ctx.fillRect(x, y+26, kiW, 6); else ctx.fillRect(x - kiW, y+26, kiW, 6);

  const spW = (f.sparkingGauge / f.maxSparking) * W_BAR;
  ctx.fillStyle = "rgba(20,20,30,0.9)"; ctx.fillRect(hpX, y+36, W_BAR, 5);
  ctx.fillStyle = f.sparkingGauge >= f.maxSparking ? PALETTE.yellow : PALETTE.orange;
  if (left) ctx.fillRect(x, y+36, spW, 5); else ctx.fillRect(x - spW, y+36, spW, 5);
  if (f.sparkingActive) {
    ctx.fillStyle = PALETTE.yellow; ctx.font = "bold 9px 'Courier New', monospace";
    ctx.textAlign = left ? "left" : "right";
    ctx.fillText("✦ SPARKING! ✦", x, y + 50);
  }

  ctx.textAlign = left ? "left" : "right";
  for (let i = 0; i < f.maxSkill; i++) {
    const px = left ? x + i * 12 : x - i * 12;
    ctx.fillStyle = i < f.skillCount ? PALETTE.purple : "rgba(60,60,80,0.6)";
    ctx.beginPath(); ctx.arc(px, y + 56, 4, 0, Math.PI*2); ctx.fill();
  }
  ctx.font = "7px 'Courier New', monospace"; ctx.fillStyle = PALETTE.muted;
  ctx.fillText("SKILL", x, y + 68);
}

function drawFighter(ctx: CanvasRenderingContext2D, f: Fighter, S: GameState) {
  const form = f.forms[f.formIdx];
  ctx.save();
  ctx.translate(f.x, f.y);
  ctx.scale(f.facing, 1);

  if (form.aura || f.kiChargeHold || f.sparkingActive || f.transformFlash > 0) {
    const auraColor = f.sparkingActive ? PALETTE.yellow : (form.aura || (f.kiChargeHold ? PALETTE.accent : null));
    if (auraColor) {
      const auraR = 40 + (f.kiChargeHold?8:0) + (f.sparkingActive?14:0) + (f.transformFlash>0?20:0) + Math.sin(S.frame*0.3)*4;
      const ag = ctx.createRadialGradient(0, -35, 5, 0, -35, auraR);
      ag.addColorStop(0, auraColor + "cc"); ag.addColorStop(0.5, auraColor + "55"); ag.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = ag; ctx.globalAlpha = 0.85;
      ctx.beginPath(); ctx.arc(0, -35, auraR, 0, Math.PI*2); ctx.fill();
      ctx.globalAlpha = 1;
      if (f.kiChargeHold || f.sparkingActive) {
        ctx.fillStyle = auraColor;
        for (let i=0;i<5;i++) {
          const fx = (i-2)*10; const fh = 14 + Math.sin(S.frame*0.4 + i)*6 + (f.sparkingActive?10:0);
          ctx.globalAlpha = 0.5;
          ctx.beginPath();
          ctx.moveTo(fx, -50); ctx.lineTo(fx-4, -50-fh); ctx.lineTo(fx+4, -50-fh); ctx.closePath(); ctx.fill();
        }
        ctx.globalAlpha = 1;
      }
    }
  }

  ctx.translate(0, -FIGHTER_H);
  const flash = f.flashHit > 0 && (S.frame % 2 === 0);

  ctx.fillStyle = flash ? "#ffffff" : f.color;
  ctx.fillRect(-12, 48, 10, 22); ctx.fillRect(2, 48, 10, 22);
  ctx.fillStyle = flash ? "#ffffff" : (f.name === "VEGETA" ? "#ffffff" : "#3a2a1a");
  ctx.fillRect(-14, 66, 14, 6); ctx.fillRect(0, 66, 14, 6);
  ctx.fillStyle = flash ? "#ffffff" : f.color;
  ctx.fillRect(-16, 20, 32, 32);
  ctx.fillStyle = flash ? "#ffffff" : (f.name === "GOKU" ? "#3a2a1a" : "#1a3a5a");
  ctx.fillRect(-6, 20, 12, 32);
  ctx.fillStyle = flash ? "#ffffff" : (f.name === "GOKU" ? "#3a8aff" : "#ffaa3a");
  ctx.fillRect(-16, 48, 32, 4);
  ctx.fillStyle = flash ? "#ffffff" : f.color;
  ctx.fillRect(-22, 22, 8, 24); ctx.fillRect(14, 22, 8, 24);
  ctx.fillStyle = flash ? "#ffffff" : "#ff3b3b";
  ctx.fillRect(-23, 44, 10, 6); ctx.fillRect(13, 44, 10, 6);
  ctx.fillStyle = flash ? "#ffffff" : f.skin;
  ctx.beginPath(); ctx.arc(0, 12, 12, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = "#111";
  ctx.fillRect(3, 9, 3, 4); ctx.fillRect(-2, 9, 2, 4);
  ctx.fillStyle = flash ? "#ffffff" : form.hairColor;
  if (f.formIdx === 0) {
    ctx.beginPath();
    ctx.moveTo(-12, 8); ctx.lineTo(-14, -2); ctx.lineTo(-8, 4); ctx.lineTo(-6, -6);
    ctx.lineTo(-2, 2); ctx.lineTo(2, -6); ctx.lineTo(6, 2); ctx.lineTo(8, -2);
    ctx.lineTo(12, 4); ctx.lineTo(14, -4); ctx.lineTo(10, 10);
    ctx.closePath(); ctx.fill();
  } else {
    ctx.beginPath();
    ctx.moveTo(-14, 10); ctx.lineTo(-16, -16); ctx.lineTo(-10, -4); ctx.lineTo(-6, -22);
    ctx.lineTo(-1, -8); ctx.lineTo(3, -24); ctx.lineTo(7, -10); ctx.lineTo(11, -18);
    ctx.lineTo(15, -2); ctx.lineTo(13, 10);
    ctx.closePath(); ctx.fill();
  }

  if (f.guardHold) {
    ctx.strokeStyle = PALETTE.accent; ctx.lineWidth = 2; ctx.globalAlpha = 0.7;
    ctx.beginPath(); ctx.arc(8, 30, 28, -Math.PI/2, Math.PI/2); ctx.stroke();
    ctx.globalAlpha = 1;
  }
  if (f.counterWindow > 0) {
    ctx.strokeStyle = PALETTE.purple; ctx.lineWidth = 2;
    ctx.globalAlpha = f.counterWindow / 14;
    ctx.beginPath(); ctx.arc(0, 30, 30, 0, Math.PI*2); ctx.stroke();
    ctx.globalAlpha = 1;
  }
  ctx.restore();

  ctx.font = "8px 'Courier New', monospace"; ctx.textAlign = "center";
  ctx.fillStyle = PALETTE.muted;
  ctx.fillText(`${f.name} · ${form.name}`, f.x, f.y - FIGHTER_H - 22);
  ctx.fillStyle = PALETTE.yellow; ctx.font = "bold 9px 'Courier New', monospace";
  ctx.fillText(fmtPL(effectivePL(f)) + " PL", f.x, f.y - FIGHTER_H - 10);
}

function render(ctx: CanvasRenderingContext2D, S: GameState) {
  const shakeX = (Math.random()-0.5) * S.shake;
  const shakeY = (Math.random()-0.5) * S.shake;
  ctx.save();
  ctx.translate(shakeX, shakeY);

  const grad = ctx.createLinearGradient(0,0,0,H);
  grad.addColorStop(0, PALETTE.bg0);
  grad.addColorStop(0.6, PALETTE.bg1);
  grad.addColorStop(1, "#0f1320");
  ctx.fillStyle = grad; ctx.fillRect(0,0,W,H);

  ctx.fillStyle = "rgba(255,255,255,0.5)";
  for (let i=0;i<40;i++) {
    const sx = (i*73) % W; const sy = (i*47) % 280;
    ctx.fillRect(sx, sy, 1, 1);
  }

  ctx.fillStyle = "#0d1018";
  ctx.beginPath(); ctx.moveTo(0, 320);
  for (let x=0; x<=W; x+=40) ctx.lineTo(x, 320 - Math.sin(x*0.02)*30 - (x%160===0?40:0));
  ctx.lineTo(W, GROUND_Y); ctx.lineTo(0, GROUND_Y); ctx.closePath(); ctx.fill();

  ctx.fillStyle = "#11151f";
  ctx.beginPath(); ctx.moveTo(0, 380);
  for (let x=0; x<=W; x+=30) ctx.lineTo(x, 380 - Math.sin(x*0.03+1)*20);
  ctx.lineTo(W, GROUND_Y); ctx.lineTo(0, GROUND_Y); ctx.closePath(); ctx.fill();

  const ggrad = ctx.createLinearGradient(0, GROUND_Y, 0, H);
  ggrad.addColorStop(0, PALETTE.ground); ggrad.addColorStop(1, PALETTE.bg1);
  ctx.fillStyle = ggrad; ctx.fillRect(0, GROUND_Y, W, H - GROUND_Y);
  ctx.strokeStyle = PALETTE.groundLine; ctx.lineWidth = 0.5; ctx.globalAlpha = 0.4;
  for (let x=0; x<=W; x+=40) { ctx.beginPath(); ctx.moveTo(x, GROUND_Y); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y=GROUND_Y; y<=H; y+=20) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
  ctx.globalAlpha = 1;
  ctx.strokeStyle = PALETTE.accent; ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(0, GROUND_Y); ctx.lineTo(W, GROUND_Y); ctx.stroke();

  for (const p of S.particles) {
    const a = p.life / p.maxLife;
    ctx.globalAlpha = a; ctx.fillStyle = p.color;
    ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha = 1;

  drawFighter(ctx, S.player, S);
  drawFighter(ctx, S.enemy, S);

  for (const pr of S.projectiles) {
    const r = pr.size * 2.5;
    const pg = ctx.createRadialGradient(pr.x, pr.y, 0, pr.x, pr.y, r);
    pg.addColorStop(0, pr.color); pg.addColorStop(0.4, pr.color); pg.addColorStop(1, "rgba(0,0,0,0)");
    ctx.globalAlpha = 0.7; ctx.fillStyle = pg;
    ctx.beginPath(); ctx.arc(pr.x, pr.y, r, 0, Math.PI*2); ctx.fill();
    ctx.globalAlpha = 1; ctx.fillStyle = "#ffffff";
    ctx.beginPath(); ctx.arc(pr.x, pr.y, pr.size*0.6, 0, Math.PI*2); ctx.fill();
  }

  for (const e of S.effects) {
    const a = e.life / e.maxLife;
    ctx.globalAlpha = a;
    if (e.type === "hit" || e.type === "smash" || e.type === "ultimate") {
      const r = e.size * (1 + (1-a));
      const eg = ctx.createRadialGradient(e.x, e.y, 0, e.x, e.y, r);
      eg.addColorStop(0, "#ffffff"); eg.addColorStop(0.3, e.color); eg.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = eg; ctx.beginPath(); ctx.arc(e.x, e.y, r, 0, Math.PI*2); ctx.fill();
      ctx.strokeStyle = e.color; ctx.lineWidth = 2;
      for (let i=0;i<6;i++) {
        const ang = i * Math.PI/3 + (1-a)*2;
        ctx.beginPath(); ctx.moveTo(e.x, e.y);
        ctx.lineTo(e.x + Math.cos(ang)*r*0.8, e.y + Math.sin(ang)*r*0.8); ctx.stroke();
      }
    } else if (e.type === "transform" || e.type === "counter") {
      const r = e.size * (1 + (1-a)*1.5);
      ctx.strokeStyle = e.color; ctx.lineWidth = 3 * a + 1;
      ctx.beginPath(); ctx.arc(e.x, e.y, r, 0, Math.PI*2); ctx.stroke();
    } else if (e.type === "block") {
      ctx.strokeStyle = e.color; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(e.x, e.y, e.size, 0, Math.PI*2); ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;

  drawBars(ctx, S.player, 20, 20, true);
  drawBars(ctx, S.enemy, W - 20, 20, false);

  if (S.combo > 1) {
    ctx.font = "bold 22px 'Courier New', monospace"; ctx.textAlign = "center";
    ctx.fillStyle = PALETTE.yellow;
    ctx.fillText(`${S.combo} HIT`, W/2, 120);
    ctx.font = "10px 'Courier New', monospace"; ctx.fillStyle = PALETTE.muted;
    ctx.fillText("COMBO", W/2, 134);
  }

  const secs = Math.ceil(S.timer / 60);
  ctx.font = "bold 28px 'Courier New', monospace"; ctx.textAlign = "center";
  ctx.fillStyle = PALETTE.text;
  ctx.fillText(String(secs).padStart(2,"0"), W/2, 40);

  ctx.restore();

  if (S.roundOver) {
    ctx.fillStyle = "rgba(5,6,15,0.78)"; ctx.fillRect(0,0,W,H);
    ctx.textAlign = "center";
    ctx.font = "bold 56px 'Courier New', monospace";
    ctx.fillStyle = S.roundResult === "VICTORY" ? PALETTE.green : S.roundResult === "DEFEAT" ? PALETTE.red : PALETTE.yellow;
    ctx.fillText(S.roundResult, W/2, H/2 - 20);
    ctx.font = "12px 'Courier New', monospace"; ctx.fillStyle = PALETTE.muted;
    ctx.fillText("Press FIGHT AGAIN to rematch", W/2, H/2 + 20);
  } else if (S.paused) {
    ctx.fillStyle = "rgba(5,6,15,0.6)"; ctx.fillRect(0,0,W,H);
    ctx.font = "bold 40px 'Courier New', monospace"; ctx.textAlign = "center";
    ctx.fillStyle = PALETTE.accent; ctx.fillText("PAUSED", W/2, H/2);
  }
}

/* ===========================================================================
 * COMPONENT
 * =========================================================================== */
export default function DragonArena() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  // Lazy ref init during first render — avoids setState-in-effect.
  // Re-assignment for a rematch happens in the click handler.
  const stateRef = useRef<GameState | null>(null);
  if (stateRef.current === null) stateRef.current = makeInitialState();
  const [result, setResult] = useState<string | null>(null);

  const rematch = useCallback(() => {
    stateRef.current = makeInitialState();
    setResult(null);
  }, []);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (!stateRef.current) return;
      const k = e.key.toLowerCase();
      if (["arrowup","arrowdown","arrowleft","arrowright"," "].includes(k)) e.preventDefault();
      if (!stateRef.current.keys[k]) stateRef.current.justPressed.add(k);
      stateRef.current.keys[k] = true;
    };
    const up = (e: KeyboardEvent) => {
      if (!stateRef.current) return;
      stateRef.current.keys[e.key.toLowerCase()] = false;
    };
    const blur = () => { if (stateRef.current) stateRef.current.keys = {}; };
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    window.addEventListener("blur", blur);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
      window.removeEventListener("blur", blur);
    };
  }, []);

  useEffect(() => {
    let raf = 0;
    const loop = () => {
      raf = requestAnimationFrame(loop);
      const S = stateRef.current;
      const canvas = canvasRef.current;
      if (!S || !canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      if (!S.paused && !S.roundOver) update(S, setResult);
      else if (S.roundOver) updateParticles(S);
      render(ctx, S);
      S.frame++;
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, []);

  const setKey = (k: string, v: boolean) => {
    if (!stateRef.current) return;
    if (v && !stateRef.current.keys[k]) stateRef.current.justPressed.add(k);
    stateRef.current.keys[k] = v;
  };

  return (
    <div className="w-full flex flex-col items-center gap-3">
      <div className="relative w-full max-w-[960px]">
        <canvas
          ref={canvasRef}
          width={W}
          height={H}
          className="w-full h-auto rounded-lg border-2"
          style={{
            borderColor: PALETTE.orange + "66",
            boxShadow: `0 0 24px ${PALETTE.orange}33, inset 0 0 40px rgba(0,0,0,0.6)`,
            imageRendering: "pixelated",
            touchAction: "none",
            background: PALETTE.bg0,
          }}
          tabIndex={0}
        />
        <div
          className="pointer-events-none absolute inset-0 rounded-lg opacity-30"
          style={{
            backgroundImage:
              "repeating-linear-gradient(to bottom, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px, transparent 1px, transparent 3px)",
            mixBlendMode: "overlay",
          }}
        />
      </div>

      {result && (
        <div className="flex items-center gap-3">
          <button
            onClick={rematch}
            className="px-5 py-2 rounded-md font-bold text-sm tracking-wider transition-all hover:scale-105"
            style={{
              border: `2px solid ${PALETTE.orange}`,
              color: PALETTE.orange,
              boxShadow: `0 0 16px ${PALETTE.orange}44`,
              background: "rgba(20,20,30,0.6)",
            }}
          >
            ▶ FIGHT AGAIN
          </button>
          <button
            onClick={rematch}
            className="px-4 py-2 rounded-md text-xs tracking-wider transition-all hover:scale-105"
            style={{
              border: `1px solid ${PALETTE.muted}`,
              color: PALETTE.muted,
              background: "rgba(20,20,30,0.4)",
            }}
          >
            RESET
          </button>
        </div>
      )}

      <div className="w-full max-w-[960px] lg:hidden grid grid-cols-2 gap-2 mt-2">
        <div className="flex gap-1">
          {[
            {l:"◀",k:"a"},{l:"▶",k:"d"},{l:"▲",k:"w"},{l:"▼",k:"s"},
          ].map(b => (
            <button key={b.k}
              onPointerDown={e => { e.preventDefault(); setKey(b.k, true); }}
              onPointerUp={e => { e.preventDefault(); setKey(b.k, false); }}
              onPointerLeave={() => setKey(b.k, false)}
              className="flex-1 py-3 text-xs rounded font-mono"
              style={{ background:"rgba(20,20,30,0.7)", border:`1px solid ${PALETTE.accent}55`, color:PALETTE.accent }}
            >{b.l}</button>
          ))}
        </div>
        <div className="grid grid-cols-4 gap-1">
          {[
            {l:"P",k:"p",c:PALETTE.pink},{l:"J",k:"j",c:PALETTE.yellow},
            {l:"K",k:"k",c:PALETTE.accent},{l:"O",k:"o",c:PALETTE.green},
            {l:"I",k:"i",c:PALETTE.orange},{l:"L",k:"l",c:PALETTE.purple},
            {l:"E",k:"e",c:PALETTE.purple},{l:"U",k:"u",c:PALETTE.yellow},
          ].map(b => (
            <button key={b.k}
              onPointerDown={e => { e.preventDefault(); setKey(b.k, true); }}
              onPointerUp={e => { e.preventDefault(); setKey(b.k, false); }}
              onPointerLeave={() => setKey(b.k, false)}
              className="py-3 text-xs rounded font-mono font-bold"
              style={{ background:"rgba(20,20,30,0.7)", border:`1px solid ${b.c}66`, color:b.c }}
            >{b.l}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
