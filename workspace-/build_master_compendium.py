#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dragon Ball Game Build — Master Compendium
A massive comprehensive PDF compiling the entire research/audit/build journey:
  • The full chat synthesis (every finding, every correction, every discovery)
  • The three source games (Sparking! ZERO, Dragon Block Noea, canon PL)
  • The 15-chapter design blueprint
  • The web demo (dragon-arena.tsx) + the hitstun-lock bug fix
  • The BT3 decompilation audit (SLES-549.45) — combat math, collision, script VM, evidence
  • The massive "how to make a game like this" list
  • All sources, all code line citations, all reasoning
"""
import hashlib, os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ━━ Blueprint palette (deep navy + cyan lines + DBZ orange) ━━
PAGE_BG      = colors.HexColor('#0a0e1a')
SECTION_BG   = colors.HexColor('#131826')
CARD_BG      = colors.HexColor('#1a2030')
TABLE_STRIPE = colors.HexColor('#161c2a')
HEADER_FILL  = colors.HexColor('#1a2840')
COVER_BLOCK  = colors.HexColor('#14203a')
BORDER       = colors.HexColor('#3a5a8a')
ICON         = colors.HexColor('#6ab0ff')
ACCENT       = colors.HexColor('#00e5ff')   # blueprint cyan
ACCENT_2     = colors.HexColor('#ff8c2a')   # DBZ orange
ACCENT_3     = colors.HexColor('#f9f871')   # SSJ gold
WARN         = colors.HexColor('#ef6c5a')
GOOD         = colors.HexColor('#7bc97a')
TEXT_PRIMARY = colors.HexColor('#e6eaf2')
TEXT_MUTED   = colors.HexColor('#8a94a8')

OUTPUT = '/home/z/my-project/public/Dragon_Ball_Game_Master_Compendium.pdf'

def register_fonts():
    cands = [
        ('Body',  ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                   '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf']),
        ('BodyB', ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                   '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']),
        ('BodyI', ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',
                   '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf']),
        ('Mono',  ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                   '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf']),
    ]
    for name, paths in cands:
        for pth in paths:
            if os.path.exists(pth):
                try: pdfmetrics.registerFont(TTFont(name, pth)); break
                except Exception: continue
    try:
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        registerFontFamily('Body', normal='Body', bold='BodyB', italic='BodyI', boldItalic='BodyB')
    except Exception: pass
register_fonts()

reg = set()
for n in ['Body','BodyB','BodyI','Mono']:
    try: pdfmetrics.getFont(n); reg.add(n)
    except Exception: pass
BODY  = 'Body'  if 'Body'  in reg else 'Helvetica'
BODYB = 'BodyB' if 'BodyB' in reg else 'Helvetica-Bold'
BODYI = 'BodyI' if 'BodyI' in reg else 'Helvetica-Oblique'
MONO  = 'Mono'  if 'Mono'  in reg else 'Courier'

styles = getSampleStyleSheet()
H1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName=BODYB, fontSize=17,
    textColor=ACCENT, spaceBefore=14, spaceAfter=7, leading=21)
H2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName=BODYB, fontSize=12.5,
    textColor=ACCENT_2, spaceBefore=11, spaceAfter=5, leading=16)
H3 = ParagraphStyle('H3', parent=styles['Heading3'], fontName=BODYB, fontSize=10.5,
    textColor=TEXT_PRIMARY, spaceBefore=8, spaceAfter=3, leading=13)
BODY_S = ParagraphStyle('Body', parent=styles['BodyText'], fontName=BODY, fontSize=9.2,
    textColor=TEXT_PRIMARY, leading=13.4, alignment=TA_JUSTIFY, spaceAfter=6)
BULLET = ParagraphStyle('Bullet', parent=BODY_S, leftIndent=12, bulletIndent=2, spaceAfter=3)
CAPTION = ParagraphStyle('Cap', parent=BODY_S, fontName=BODYI, fontSize=8.0,
    textColor=TEXT_MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=10)
WARNBOX = ParagraphStyle('Warn', parent=BODY_S, fontName=BODYI, fontSize=8.8,
    textColor=WARN, leftIndent=10, borderColor=WARN, borderPadding=6,
    backColor=colors.HexColor('#2a1212'), borderWidth=0, spaceBefore=4, spaceAfter=8)
OKBOX = ParagraphStyle('Ok', parent=BODY_S, fontName=BODYI, fontSize=8.8,
    textColor=GOOD, leftIndent=10, borderColor=GOOD, borderPadding=6,
    backColor=colors.HexColor('#122a12'), borderWidth=0, spaceBefore=4, spaceAfter=8)
NOTE = ParagraphStyle('Note', parent=BODY_S, fontName=BODYI, fontSize=8.8,
    textColor=TEXT_MUTED, leftIndent=10, borderColor=BORDER, borderPadding=6,
    backColor=CARD_BG, borderWidth=0, spaceBefore=4, spaceAfter=8)
CODE = ParagraphStyle('Code', parent=BODY_S, fontName=MONO, fontSize=7.6,
    textColor=ACCENT, leading=10, alignment=TA_LEFT, leftIndent=8,
    backColor=colors.HexColor('#0d1322'), borderPadding=6, spaceBefore=4, spaceAfter=8)
TOC_L0 = ParagraphStyle('TOC0', fontName=BODYB, fontSize=10, textColor=ACCENT,
    leftIndent=0, spaceBefore=4, spaceAfter=1, leading=13)
TOC_L1 = ParagraphStyle('TOC1', fontName=BODY, fontSize=8.5, textColor=TEXT_PRIMARY,
    leftIndent=16, spaceBefore=0, spaceAfter=0, leading=11)

def page_bg(canv, doc):
    canv.saveState()
    canv.setFillColor(PAGE_BG); canv.rect(0,0,A4[0],A4[1], fill=1, stroke=0)
    canv.setStrokeColor(colors.HexColor('#16203a')); canv.setLineWidth(0.3)
    for x in range(0, int(A4[0]/mm)+1, 10):
        canv.line(x*mm, 12*mm, x*mm, A4[1]-12*mm)
    for y in range(1, int((A4[1]-24*mm)/mm)//10 + 1):
        canv.line(12*mm, y*10*mm + 12*mm, A4[0]-12*mm, y*10*mm + 12*mm)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(1.0)
    canv.line(12*mm, A4[1]-14*mm, A4[0]-12*mm, A4[1]-14*mm)
    canv.setFont(BODY, 7.5); canv.setFillColor(TEXT_MUTED)
    canv.drawString(12*mm, 7*mm, 'Dragon Ball Game — Master Compendium')
    canv.drawRightString(A4[0]-12*mm, 7*mm, f'Page {doc.page}')
    canv.restoreState()

def cover_bg(canv, doc):
    canv.saveState()
    canv.setFillColor(PAGE_BG); canv.rect(0,0,A4[0],A4[1], fill=1, stroke=0)
    canv.setStrokeColor(colors.HexColor('#16203a')); canv.setLineWidth(0.3)
    for x in range(0, int(A4[0]/mm)+1, 8):
        canv.line(x*mm, 0, x*mm, A4[1])
    for y in range(0, int(A4[1]/mm)//8 + 1):
        canv.line(0, y*8*mm, A4[0], y*8*mm)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(1.2)
    canv.line(0, A4[1]-58*mm, A4[0], A4[1]-58*mm)
    canv.line(0, 58*mm, A4[0], 58*mm)
    canv.setStrokeColor(ACCENT_2); canv.setLineWidth(0.8)
    canv.line(18*mm, A4[1]-58*mm, 18*mm, 58*mm)
    canv.line(A4[0]-18*mm, A4[1]-58*mm, A4[0]-18*mm, 58*mm)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(0.6)
    for cx, cy in [(25*mm, A4[1]-25*mm),(A4[0]-25*mm, A4[1]-25*mm),
                   (25*mm, 25*mm),(A4[0]-25*mm, 25*mm)]:
        canv.circle(cx, cy, 8*mm, fill=0, stroke=1)
        canv.circle(cx, cy, 3*mm, fill=0, stroke=1)
    canv.setFillColor(COVER_BLOCK); canv.rect(A4[0]-78*mm, 14*mm, 66*mm, 34*mm, fill=1, stroke=0)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(0.6)
    canv.rect(A4[0]-78*mm, 14*mm, 66*mm, 34*mm, fill=0, stroke=1)
    canv.setFont(BODYB, 7); canv.setFillColor(ACCENT)
    canv.drawString(A4[0]-75*mm, 41*mm, 'TITLE BLOCK')
    canv.setFont(BODY, 6.3); canv.setFillColor(TEXT_MUTED)
    canv.drawString(A4[0]-75*mm, 37*mm, 'Project:  Dragon Ball Game Build')
    canv.drawString(A4[0]-75*mm, 34*mm, 'Doc:      Master Compendium')
    canv.drawString(A4[0]-75*mm, 31*mm, 'Sheets:   01 of 01')
    canv.drawString(A4[0]-75*mm, 28*mm, 'Drawn:    Z.ai Research')
    canv.drawString(A4[0]-75*mm, 25*mm, 'Date:     2026')
    canv.drawString(A4[0]-75*mm, 22*mm, 'Rev:      A — Final')
    canv.drawString(A4[0]-75*mm, 18*mm, 'Status:   MASTER COMPENDIUM')
    canv.restoreState()

class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text  = getattr(flowable, 'bookmark_text', '')
            key   = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))

def heading(text, style, level=0):
    key = 'h_' + hashlib.md5(text.encode()).hexdigest()[:8]
    p = Paragraph(f'<a name="{key}"/>{text}', style)
    p.bookmark_name = key; p.bookmark_level = level
    p.bookmark_text = text; p.bookmark_key = key
    return p
def h1(t): return heading(t, H1, 0)
def h2(t): return heading(t, H2, 1)
def h3(t): return Paragraph(t, H3)
def p(t): return Paragraph(t, BODY_S)
def b(t): return Paragraph(f'• {t}', BULLET)
def warn(t): return Paragraph('⚠ '+t, WARNBOX)
def ok(t): return Paragraph('✓ '+t, OKBOX)
def note(t): return Paragraph(t, NOTE)
def code(t): return Paragraph(t, CODE)

def tstyle(nrows, header=True):
    cmds = [
        ('FONTNAME',(0,0),(-1,-1),BODY), ('FONTSIZE',(0,0),(-1,-1),7.8),
        ('TEXTCOLOR',(0,0),(-1,-1),TEXT_PRIMARY), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
        ('GRID',(0,0),(-1,-1),0.3,BORDER),
        ('BACKGROUND',(0,0),(-1,-1),SECTION_BG),
    ]
    if header:
        cmds += [('BACKGROUND',(0,0),(-1,0),HEADER_FILL),('FONTNAME',(0,0),(-1,0),BODYB),
                 ('TEXTCOLOR',(0,0),(-1,0),ACCENT), ('FONTSIZE',(0,0),(-1,0),8.0)]
        for i in range(1,nrows):
            if i%2==1: cmds.append(('BACKGROUND',(0,i),(-1,i),TABLE_STRIPE))
    else:
        for i in range(0,nrows):
            if i%2==1: cmds.append(('BACKGROUND',(0,i),(-1,i),TABLE_STRIPE))
    return TableStyle(cmds)
def mk(rows, widths, header=True):
    t = Table(rows, colWidths=widths); t.setStyle(tstyle(len(rows),header)); return t

story = []

# ═══════════════════════════════════════════════════════════════════
# COVER
# ═══════════════════════════════════════════════════════════════════
ct  = ParagraphStyle('CT',  fontName=BODYB, fontSize=30, textColor=ACCENT, leading=36, leftIndent=20*mm)
ct2 = ParagraphStyle('CT2', fontName=BODY,  fontSize=16, textColor=TEXT_PRIMARY, leading=20, leftIndent=20*mm, spaceBefore=4)
cs  = ParagraphStyle('CS',  fontName=BODY,  fontSize=11, textColor=TEXT_PRIMARY, leading=15, leftIndent=20*mm, spaceBefore=10)
cg  = ParagraphStyle('CG',  fontName=BODYI, fontSize=9, textColor=TEXT_MUTED, leading=12, leftIndent=20*mm, spaceBefore=14)
story.append(Spacer(1, 46*mm))
story.append(Paragraph('DRAGON BALL GAME', ct))
story.append(Paragraph('Master Compendium', ct2))
story.append(Spacer(1, 5*mm))
story.append(Paragraph(
    'A massive comprehensive compilation of the entire research, audit,<br/>'
    'and build journey: every finding, every code citation, every "why,"<br/>'
    'and a step-by-step master list for recreating a Sparking! ZERO-style<br/>'
    'Dragon Ball game.', cs))
story.append(Spacer(1, 12*mm))
story.append(Paragraph(
    'Compiles: the chat synthesis · the three source games · the 15-chapter<br/>'
    'design blueprint · the web demo + bug fix · the BT3 decompilation audit<br/>'
    '(SLES-549.45) with the script-VM discovery · the evidence index · the<br/>'
    'full "how to make a game like this" list · all sources and reasoning', cg))
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════
# TOC
# ═══════════════════════════════════════════════════════════════════
toc = TableOfContents(); toc.levelStyles = [TOC_L0, TOC_L1]
story.append(Paragraph('Table of Contents', H1))
story.append(Spacer(1, 4)); story.append(toc)
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════
# PART I — CHAT SYNTHESIS
# ═══════════════════════════════════════════════════════════════════
story.append(h1('Part I — Chat Synthesis: The Full Research Journey'))
story.append(p(
    'This compendium documents an extended research-and-build session spanning the design of a '
    'Dragon Ball game fusing three source systems: the combat of <i>Dragon Ball: Sparking! ZERO</i> '
    '(Bandai Namco / Spike Chunfort, 2024), the RPG progression of the fan-made <i>Dragon Block Noea</i> '
    '/ <i>DragonMineZ</i> Minecraft mod (Forge 1.20.1, 2024–2026), and canon-accurate power levels '
    'sourced to the manga, Daizenshuu 7, and V-Jump. The session culminated in a Ghidra decompilation '
    'audit of <i>Dragon Ball Z: Budokai Tenkaichi 3</i> (SLES-549.45, PAL, Spike 2007) — the direct '
    'predecessor of Sparking! ZERO, made by the same studio.'))

story.append(h2('1.1 The conversation arc'))
story.append(p('The chat moved through seven distinct phases, each building on the last:'))
story.append(mk([
    ['#','Phase','What happened','Artifacts'],
    ['1','Workspace review','Examined an uploaded tar of a prior GLM-5.2 session — 6 PDFs + the dragon-power.js canvas game',
     'Found the "Dragon Power" DBZ-inspired cabinet game + identified a transcript misattribution'],
    ['2','Power-scaling fact-check','Cross-referenced every PL against Kanzenshuu/Daizenshuu/V-Jump; applied the user\'s Gohan corrections',
     'Dragon_Ball_Z_FactChecked_Power_Levels.pdf (12 pp, 8 corrections)'],
    ['3','Design blueprint','Synthesized Sparking combat + Noea RPG + canon PL into a buildable spec',
     'Dragon_Ball_Game_Design_Blueprint.pdf (25 pp, 15 chapters)'],
    ['4','Web demo','Built a playable Sparking-Zero-style canvas fighter in Next.js',
     'dragon-arena.tsx (976 lines) + page.tsx wrapper'],
    ['5','Bug fix','Fixed the "can\'t move after one hit" hitstun-lock bug + added Revenge Counter',
     '2 patch edits to dragon-arena.tsx, browser-verified'],
    ['6','BT3 code research','Researched Roblox DBZ games, BT3 source-code reality, file-sharing methods',
     'Honest report: BT3 source is lost; Spike→Spike Chunfort lineage confirmed'],
    ['7','BT3 decompilation audit','Downloaded & audited sles_549.45_decompiled.c (7.2 MB, 292,589 lines, 7,610 functions)',
     'Combat math, collision fn, script-VM discovery, evidence index'],
], [10*mm, 26*mm, 70*mm, 60*mm]))

story.append(h2('1.2 The deliverables produced'))
story.append(b('<b>Dragon_Ball_Game_Design_Blueprint.pdf</b> (25 pp) — the 15-chapter build spec'))
story.append(b('<b>Dragon_Ball_Z_FactChecked_Power_Levels.pdf</b> (12 pp) — canon PL with 8 corrections'))
story.append(b('<b>Dragon_Ball_Research_Master_Review.pdf</b> (9 pp) — index of the 5 source PDFs'))
story.append(b('<b>Dragon_Ball_Sparking_Zero_Combat_Controls_Guide.pdf</b> (7 pp) — the combat reference'))
story.append(b('<b>Dragon_Block_Noea_Deep_Research_Guide.pdf</b> (9 pp) — the RPG-systems reference'))
story.append(b('<b>Dragon_Block_C_Deep_Research_Guide.pdf</b> (14 pp) — companion mod research'))
story.append(b('<b>Dragon_Ball_Z_Chapter_Power_Levels.pdf</b> (12 pp) — prior chapter-by-chapter guide'))
story.append(b('<b>dragon-arena.tsx</b> (976 lines) — the playable Sparking-Zero-style web demo'))
story.append(b('<b>sles_549.45_decompiled.c</b> audit — 7,610-function Ghidra decompilation analysis'))
story.append(b('<b>This compendium</b> — the master document compiling all of the above'))

story.append(h2('1.3 Key honest corrections made during the chat'))
story.append(p('Research integrity required correcting several claims as the audit deepened:'))
story.append(mk([
    ['Claim','Correction','Evidence'],
    ['Goku "Over 9,000"','Actually "Over 8,000" in the manga; "9,000" is English dub only','Kanzenshuu'],
    ['SSJ2 Gohan ~700M','Corrected to ~1.8B (> Super Perfect Cell ~1.6B)','Manga shows Gohan > Cell'],
    ['Ultimate Gohan ~8B','Corrected to ~35B (> SSJ3 Goku 24B AND > SSJ3 Gotenks 30B)','Manga equality + scaling'],
    ['Kid Buu 1.15B','Corrected to ~24B (≈ SSJ3 Goku, manga equality)','V-Jump + manga'],
    ['case 0xd/0xe = hit-reaction dispatch','Actually file-loader state-machine instances (all call FUN_002a2xxx)','Lines 15799/15962/15977/16816/16823'],
    ['iGpffffaa28 switch = combat state machine','Actually the streaming file-loader FSM','Every case calls FUN_002a2xxx; line 15818 iGpffffaa28 += 1'],
    ['FUN_00108908 = input-translation layer','Actually a camera/HUD offset calculator triggered by input','Lines 5376-5398: SQRT(dx²+dy²) Pythagorean + 3.0×16.0 screen multiplier'],
], [44*mm, 64*mm, 56*mm]))

# ═══════════════════════════════════════════════════════════════════
# PART II — THE THREE SOURCE GAMES
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part II — The Three Source Games'))
story.append(p('The merged game draws from three independently-proven source systems. Each contributes '
    'a different strength; the design challenge is fusing them without breaking any of the three.'))

story.append(h2('2.1 Comparative matrix'))
story.append(mk([
    ['Dimension','Sparking! ZERO','Dragon Block Noea','Canon PL research'],
    ['Genre','3D arena fighter','Character-progression RPG mod','Reference dataset'],
    ['Combat depth','Very high — layered counters, Ki economy','Low — auto-attack + ability keys','N/A (data)'],
    ['Progression','Flat — 5-point stat spread per character','Deep — 6 stats + TP + mastery + skills','N/A'],
    ['Power accuracy','Loosely canon-flavored','Canon-faithful multipliers (×50/×100/×400)','Rigorously sourced'],
    ['Content scope','164-character roster','Solo-modded sagas, space, planets, raids','Manga ch.1-325 + DBS'],
    ['Multiplayer','Online PvP (delay/rollback)','Minecraft server co-op','N/A'],
    ['Built with','Unreal Engine 5 (Bandai)','Forge 1.20.1 + GeckoLib + Java','N/A'],
    ['Strength to take','Combat feel, counter layering','RPG systems, transformation mastery','Damage math, PL data'],
    ['Weakness to drop','Shallow progression','Shallow combat, auto-attack','No game — pure reference'],
], [22*mm, 36*mm, 38*mm, 38*mm, 32*mm]))

story.append(h2('2.2 Source 1 — Sparking! ZERO combat (Bandai/Spike Chunfort, 2024)'))
story.append(p('Sparking! ZERO is a 3D arena fighter — the Budokai Tenkaichi series revival — shipping '
    '164 characters and receiving generally positive reviews (CNET, Rolling Stone, Hardcore Gamer). '
    'Its combat is documented in detail in the official Bandai Namco Beginner\'s Guide and the '
    'combos-and-features page, supplemented by TheGamer, NoobFeed, GamingBolt, and Game8 breakdowns.'))
story.append(p('The combat rests on five interlocking design choices (detailed in Part III):'))
story.append(b('<b>Movement as the backbone, not combos</b> — "footsies in the sky"; positional reads beat memorized strings. '
    'Step/Short Dash for spacing, Dragon Dash (Ki-cost) to close, Z-Burst Dash (more Ki) to reposition behind.'))
story.append(b('<b>Ki as the universal economy</b> — one resource gates blasts, dashes, vanishing assault, transform upkeep, '
    'and fills the Sparking gauge. No fragmented stamina/meter/burst pools.'))
story.append(b('<b>Layered counters with different costs</b> — Guard (free), Super Perception (timed, free, Sonic Sway vs melee, '
    '2 Skill Count vs blasts), Z-Counter (timing-only escalating duel), Revenge Counter (1 Skill Count, panic button '
    'when combo\'d), Super Counter (precise timing, no resource, works from behind/mid-hit).'))
story.append(b('<b>Sparking! Mode as the shared climax</b> — full Sparking Gauge + 1 Skill Count → free Ki, Ultimate Blast '
    'unlocked, Ki-stun immunity, HP regen. Both players race for it; that\'s the dramatic arc.'))
story.append(b('<b>Every character is a "setup archetype"</b> — shared core kit; differentiation by Blast/Ultimate/transformation/'
    'passive, NOT by control scheme. A player who learns the system can pilot any character.'))

story.append(h2('2.3 Source 2 — Dragon Block Noea / DragonMineZ (Forge 1.20.1, 2024-2026)'))
story.append(p('DragonMineZ is the base mod: a free, actively developed Forge 1.20.1 Dragon Ball RPG mod '
    '(GeckoLib/TerraBlender/Curios dependent) with 538,000+ CurseForge downloads. Dragon Block Noea is a '
    'third-party add-on/modpack layered on top — built by solo modder BuD-eR / ButterJaffa, distributed '
    'via Patreon with periodic free windows. The Noea guide documents the RPG systems in detail.'))
story.append(h3('Races and form ladders (canon-accurate)'))
story.append(mk([
    ['Race','Passive skill','Core transformation ladder'],
    ['Human','Recharge (faster Ki charge)','Buffed → Full Power → Potential Unleashed → Beyond the Limits'],
    ['Saiyan','Zenkai (boost + partial heal on near-death)','Oozaru → SSJ → Grade 2/3 → Mastered SSJ → SSJ2 → SSJ3'],
    ['Namekian','Meditation (faster Ki regen)','Giant → Full Power → Potential Unleashed → Orange'],
    ['Bio-Android','Absorption (heals % of damage dealt)','Semi-Perfect → Perfect → Super-Perfect → Ultra'],
    ['Cold Demon','Mutant (higher TP gain)','2nd → 3rd → Final → Full Power → 5th Form'],
    ['Majin','Regeneration (passive HP regen)','Evil → Kid → Super → Ultra'],
], [26*mm, 42*mm, 108*mm]))

story.append(h3('The six-stat sheet → Battle Power'))
story.append(p('DragonMineZ uses six core attributes (opened with the stats menu). The three offensive stats '
    'stack additively; the three defensive stats build survivability. All feed a single derived number — '
    '<b>Battle Power</b>, the modern equivalent of a classic Dragon Ball power level.'))
story.append(mk([
    ['Stat','Drives','Stacks into'],
    ['STR (Strength)','Melee (physical) damage','Offense'],
    ['SKP (Strike Power)','Ki-enhanced melee / technique "strike" damage','Offense'],
    ['PWR (Ki Power)','Ki blast / energy-wave damage','Offense'],
    ['RES (Resistance)','Defense/damage mitigation + max Stamina + Poise','Survivability'],
    ['VIT (Vitality)','Max Health + regen rate','Survivability'],
    ['ENE (Energy)','Max Ki (energy pool)','Survivability'],
], [36*mm, 84*mm, 44*mm]))

story.append(h3('Training Points (TP) — the universal progression currency'))
story.append(p('TP is spent on stats, skills, Ki techniques, and transformation mastery. Earned from six parallel sources, '
    'all run through TP-boost multipliers:'))
story.append(b('<b>Kills</b> — TP scales with the target\'s Battle Power (anti-grind; fighting stronger enemies is far more efficient)'))
story.append(b('<b>Landed hits</b> — small TP per combat hit, independent of the kill'))
story.append(b('<b>Passive trickle</b> — small constant gain just for playing'))
story.append(b('<b>Travel / block-breaking / crafting</b> — each awards TP, scaled to distance/amount'))
story.append(b('<b>Training minigames</b> — 5 NPC Masters (Rhythm/Mr. Popo, Control/Krillin, Shadow Boxing/Gohan, '
    'Precision/Trunks, Gravity/Vegeta); biggest deliberate TP source'))
story.append(b('<b>Environment multipliers</b> — Gravity Devices, Hyperbolic Time Chamber, weighted gear; Cold Demons get ×1.25'))

story.append(h3('Power Release — the in-combat throttle'))
story.append(p('A character\'s raw stats are not fully "on" by default. Holding the release key charges Power Release '
    'from 0% to a base cap of 50%; the Potential Unlock passive (taught by King Kai) raises the ceiling to 100%. '
    'Release is a <b>throttle on how much of the underlying stat sheet is expressed in combat at any given moment</b> — '
    'the mechanical bridge between the RPG grind and the fighting-game match.'))

story.append(h3('Mastery — the form-use curve'))
story.append(p('Each transformation has a TP unlock cost and, while active, an ongoing Ki-drain upkeep. Repeated use of '
    'a form builds Mastery, which both <i>reduces</i> that upkeep and <i>increases</i> the form\'s stat multiplier — '
    'a fully mastered form reaches up to ×1.5 stats while upkeep drops to ×0.75 of base cost, and some forms become '
    'free to hold once fully mastered. Related forms share mastery progress.'))

story.append(h2('2.4 Source 3 — Canon power levels (the data backbone)'))
story.append(p('Every power level is tagged with a five-tier source hierarchy, making the data auditable:'))
story.append(mk([
    ['Tier','Source','Example value','Reliability'],
    ['[C]','Manga (on-panel scouter)','Raditz 1,500 — Vegeta 18,000 — Frieza 1st 530,000','Highest'],
    ['[D]','Daizenshuu 7 (official databook)','Goku SSJ 150,000,000 — Frieza 100% 120,000,000','High'],
    ['[V]','V-Jump magazine','SSJ3 Goku 24,000,000,000','Medium (sometimes inconsistent)'],
    ['[G]','Game tie-in (Kakarot / arcade)','Android 17/18/16 V-Jump-style values','Low (often inconsistent)'],
    ['[S]','Scaling via canon multipliers','SSJ2 Gohan ~1.8B (×100 of ~7M base)','Medium-high'],
    ['[!]','Contested','Nappa 4,000; Kid Buu 1.15B (arcade) vs 24B (manga equality)','Flag both, prefer manga'],
], [12*mm, 50*mm, 70*mm, 38*mm]))

story.append(h3('The 8 verified corrections (from the fact-checked guide)'))
story.append(mk([
    ['#','Prior claim','Corrected to','Reason'],
    ['1','Goku "Over 9,000"','"Over 8,000"','English dub only; manga says 8000 wo koeta'],
    ['2','Nappa 4,000 (unflagged)','4,000 [!] contested','Daizenshuu vs manga showings'],
    ['3','SSJ2 Gohan ~700M','~1,800,000,000','×100 of ~7M base; manga shows > Cell'],
    ['4','Kid Buu 1.15B','~24,000,000,000','≈ SSJ3 Goku (manga equality)'],
    ['5','Android V-Jump values unflagged','Flagged [!] contested','V-Jump promo values widely inconsistent'],
    ['6','Ultimate Gohan ~8B','~35,000,000,000','> SSJ3 Goku 24B AND > SSJ3 Gotenks 30B'],
    ['7','SSJ3 Gotenks ~24B','~30,000,000,000','> SSJ3 Goku (manga-stated)'],
    ['8','SSJ2 Gohan vs Cell ordering','SSJ2 Gohan > Super Perfect Cell','Manga shows Gohan won with half-ki depleted'],
], [8*mm, 38*mm, 40*mm, 50*mm, 36*mm]))

story.append(h3('Verified canon Buu saga power order (weakest → strongest)'))
story.append(code('SSJ3 Goku (24B) < SSJ3 Gotenks (~30B) < Ultimate Gohan (~35B)\n'
                 '< Buutenks (~32B, briefly > Gohan) < Buuhan (~65B+) < Vegito (~70B+ base)'))
story.append(p('The manga explicitly establishes: (1) Goku refused to fight Super Buu without fusion → Super Buu > '
    'SSJ3 Goku. (2) Ultimate Gohan dominated Super Buu → Gohan > Super Buu. (3) Goku stated fusion would make '
    'Gotenks stronger than him → SSJ3 Gotenks > SSJ3 Goku. Ultimate Gohan is the strongest non-fused mortal in the Buu saga.'))

# ═══════════════════════════════════════════════════════════════════
# PART III — THE DESIGN BLUEPRINT
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part III — The 15-Chapter Design Blueprint'))
story.append(p('The design blueprint (delivered as Dragon_Ball_Game_Design_Blueprint.pdf, 25 pp) specifies how to '
    'build the merged game. Here is the condensed chapter-by-chapter summary.'))

story.append(h2('3.1 Why Sparking! ZERO\'s combat is effective (5 reasons)'))
story.append(mk([
    ['#','Reason','Evidence'],
    ['1','Movement is the backbone, not combos','Bandai guide: "closer to footsies in the sky than a traditional 2D fighter"'],
    ['2','Ki is the universal economy','GameFAQs: "Ki management is the name of the game"'],
    ['3','Layered counters, different costs','5-counter ladder: free→timing→Skill Count→precise'],
    ['4','Sparking! Mode is the shared climax','Three-act dramatic structure (neutral→race→Ultimate)'],
    ['5','Every character is a setup archetype','Steam: "Every character is a setup archetype... theatrical look"'],
], [8*mm, 56*mm, 110*mm]))

story.append(h2('3.2 The 5-phase combat loop'))
story.append(mk([
    ['Phase','Player goal','Primary tools','Resource state'],
    ['1. Neutral','Bait guard/force movement without overspending Ki','Ki Blasts, Smash Attacks at range','Ki building'],
    ['2. Approach','Close distance; punish whiffed guard','Dragon Dash, Z-Burst Dash','Ki spent on dash'],
    ['3. Conversion','Convert one read into offensive sequence','Vanishing Assault → Dragon Homing/Vanishing/Lightning','Skill Count banked'],
    ['4. Defense read','Pick the right counter from the ladder','Super Perception / Z-Counter / Revenge / Super Counter','Skill Count if panic'],
    ['5. Climax','Race to Sparking Mode; land Ultimate Blast','Sparking → Burst Rush → Burst Finish → Ultimate Blast','Sparking Gauge + Skill Count'],
], [20*mm, 50*mm, 56*mm, 40*mm]))
story.append(note('The loop is symmetric — both players run it simultaneously. The Ki economy, Skill Count bank, and '
    'Sparking Gauge are three resource clocks ticking in parallel; the player who reads their opponent\'s clock-state best wins.'))

story.append(h2('3.3 Canon power-level system + the log-ratio damage formula'))
story.append(p('Canon PL spans seven orders of magnitude (Farmer 5 → Vegito ~70 billion). A linear damage formula '
    'makes 99% of matchups one-shot kills. The solution is a <b>log-scaled combat ratio</b> — exactly the approach '
    'the Dragon Block Noea mod and the dragon-power.js prototype implement.'))
story.append(code(
    'ratio      = attacker.effectivePL / max(defender.effectivePL, 1)\n'
    'ratioScale = log10(ratio + 9)        // 1x→1.0, 10x→1.28, 100x→2.04, 1000x→~3\n'
    'baseDamage = move.baseDamage * ratioScale * move.typeMultiplier\n'
    'finalDamage = baseDamage * (1 - defender.guardReduction)\n'
    '\n'
    '// example: Goku 416 (Kaio-ken x4 = 1664) vs Vegeta 18,000\n'
    '//   ratio = 1664/18000 = 0.092, ratioScale = log10(9.092) ≈ 0.959\n'
    '//   → Goku hits Vegeta for ~baseDamage × 0.96 (outmatched ~11x, ~4% weak)\n'
    '// example: SSJ Goku 150M vs Frieza 100% 120M\n'
    '//   ratio = 1.25, ratioScale = log10(10.25) ≈ 1.01 → near-even, slight edge'))
story.append(p('The log curve means a 10× advantage is a meaningful-but-not-fight-ending edge; a 100× advantage is '
    'decisive but the underdog still does <i>some</i> damage; a 1000× advantage is a one-shot. This preserves the '
    'drama of the source material — Raditz torturing Goku and Piccolo (1,500 vs 416/408, ~3.6× advantage) plays out '
    'as a real fight, not a one-hit kill, exactly as the manga shows.'))

story.append(h2('3.4 The transformation system merge'))
story.append(p('Both source systems handle mid-battle transformation differently. The merged game takes '
    'Sparking\'s resource model (Skill Count cost, stat-spread shift) for the in-fight layer, and Noea\'s mastery '
    'model (Ki-drain upkeep, mastery curve) for the progression layer. The two coexist because they operate at '
    'different time scales.'))
story.append(mk([
    ['Property','Sparking! ZERO model','Noea model','Merged game uses'],
    ['Cost to activate','Skill Count stock','TP unlock (one-time) + Ki-drain','Skill Count (fight) + TP unlock (meta)'],
    ['Effect','Shifts 5-point stat spread','Stat multiplier + Ki-upkeep','Stat spread shift + multiplier + upkeep'],
    ['In-fight limitation','None — form persists','Ki drains; drops at 0 Ki','Ki-upkeep (drops at 0 Ki)'],
    ['Long-term progression','None — flat per character','Mastery curve (upkeep↓, mult↑)','Mastery curve'],
    ['Climax interaction','Transformed → Sparking → Ultimate','Form-appropriate ultimate','Form-appropriate Ultimate Blast'],
], [30*mm, 38*mm, 42*mm, 50*mm]))

story.append(h2('3.5 Architecture blueprint — engine and core systems'))
story.append(p('<b>Engine choice: Unreal Engine 5.</b> For a Sparking-Zero-style 3D arena fighter, UE5 is the correct '
    'choice because: (a) Nanite + Lumen produce the cinematic anime-cel-shaded look Sparking! ZERO ships with; '
    '(b) UE5\'s Chaos physics, Niagara VFX, and Animation Blueprint suit the destructible-terrain + transformation + '
    'aura-VFX load; (c) Bandai uses UE5 for Sparking! ZERO itself; (d) the Gameplay Abilities System (GAS) maps '
    'almost 1:1 onto the Noea skill tree.'))
story.append(p('The game decomposes into nine core systems, each independently testable:'))
story.append(mk([
    ['#','System','Responsibility','Key tech'],
    ['1','Character Controller','Movement, camera, input mapping','UE5 CharacterMovementComponent'],
    ['2','Combat System','Move execution, hitboxes, damage, counters','Custom + GAS for abilities'],
    ['3','Power-Level Engine','effectivePL calc, combat-ratio formula, source-tier flags','Pure data layer'],
    ['4','Progression System','Races, six-stat sheet, TP, Power Release, mastery','GAS + GameplayTags + SaveGame'],
    ['5','Transformation System','Form state, stat-spread shift, Ki-upkeep, mastery','Sub-system of Combat + Progression'],
    ['6','Animation System','State machine, blend trees, frame data, cancels','UE5 Anim Blueprint + AnimMontage'],
    ['7','Netcode','Rollback for PvP; relay for co-op; spectator','GGPO-style rollback layer'],
    ['8','World Systems','Space travel, planets, destructible terrain, raids','Voxel/marching-cubes + Niagara'],
    ['9','Content layer','Saga story, masters, tournaments, dialogue','Data tables + quest system'],
], [8*mm, 32*mm, 72*mm, 50*mm]))

story.append(h2('3.6 Netcode — rollback for PvP'))
story.append(p('In <b>delay-based</b> netcode, the local game waits for the opponent\'s input — adding input latency '
    'proportional to ping. In <b>rollback</b> netcode, the local game never waits: it advances using local input + '
    'predicted opponent input; when real input arrives, if it differed, the game rolls state back and re-simulates. '
    'Per Ars Technica: <i>"rollback\'s main strength is that it never waits for missing input from the opponent."</i>'))
story.append(p('Rollback requires the simulation to be <b>fully deterministic</b>: no FP non-determinism (use fixed-point '
    'or deterministic-float libraries), no unlocked-thread races (gameplay state single-threaded), no system-time RNG '
    '(shared seeded PRNG), and full state save/restore in <2ms per frame.'))

story.append(h2('3.7 Destructible terrain & planet destruction'))
story.append(p('The Noea mod\'s headline feature — destructible terrain and planet destruction — requires a <b>voxel '
    'representation</b> rendered to mesh via <b>marching-cubes</b> on a GPU compute shader. A Kamehameha carve '
    'becomes: write zeros to a voxel region → re-run marching cubes for affected chunks → mesh updates.'))
story.append(mk([
    ['Property','Value','Note'],
    ['Voxel resolution','0.5m – 2m cubes','Fine enough for ki-blast carves'],
    ['Chunk size','16³ or 32³ voxels','One GPU dispatch per chunk per rebuild'],
    ['Rebuild scope','Only chunks that changed','Differential update'],
    ['Storage','3D texture / StructuredBuffer','GPU-resident; CPU only for saves'],
    ['Planet size','500–5000 block radius (Noea spec)','Seamless spherical wrap (Noea v1.0)'],
], [32*mm, 48*mm, 70*mm]))
story.append(p('Noea\'s planet-destruction model: a planet has an <b>integrity</b> value; if a sufficiently powerful '
    'attack\'s effectivePL exceeds the planet\'s integrity, the planet is destroyed outright (debris, kills anyone present, '
    'Evil alignment shift). This is a single-number threshold that maps directly onto the canon power-level system.'))

story.append(h2('3.8 Build roadmap (4 phases)'))
story.append(mk([
    ['Phase','Calendar','Team size','Deliverable'],
    ['1. Prototype','~2 months','1–2','One character, one arena, full core combat kit + local PvP'],
    ['2. Vertical slice','~3 months','3–5','RPG layer wired in; 3 characters; Saiyan saga; destructible terrain; online rollback'],
    ['3. Beta','~6 months','6–10','Full DBZ roster; all races; tournament mode; first raid boss'],
    ['4. v1.0','~4 months','8–12','DBS god-tier content; space travel; full planet system; all raid bosses'],
], [26*mm, 22*mm, 22*mm, 110*mm]))

story.append(h2('3.9 Risks, legal, and the original-IP alternative'))
story.append(warn(
    'Dragon Ball, Dragon Ball Z, Dragon Ball Super, Dragon Ball: Sparking! ZERO, and all character names are '
    'trademarks of Bird Studio / Shueisha / Toei Animation / Bandai Namco. A commercial game using these names '
    'and likenesses requires a license. The Dragon Block Noea / DragonMineZ mods operate in a legally gray '
    'fan-work space. This compendium is research, not legal clearance to ship a commercial Dragon Ball game.'))
story.append(p('The cleanest legal path is to build with an <b>original IP inspired by Dragon Ball</b> — original '
    'character names, original planet names, but the same combat feel, the same RPG progression, and the same '
    'power-level architecture. The canon power-level research transfers directly (it\'s a numerical-design pattern, '
    'not trademarked); the Sparking! ZERO combat mechanics transfer (game mechanics are not copyrightable); only '
    'the names and likenesses need to be original. The dragon-power.js prototype already in this workspace takes '
    'exactly this approach.'))

# ═══════════════════════════════════════════════════════════════════
# PART IV — THE WEB DEMO
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part IV — The Web Demo (dragon-arena.tsx)'))
story.append(p('A playable Sparking! ZERO-style 2.5D arena fighter was built as a Next.js client component to '
    'demonstrate the blueprint\'s combat mechanics in a browser. It is 976 lines of TypeScript implementing the '
    'core combat loop, Ki economy, layered counters, Sparking Mode, transformation, and the log-ratio damage '
    'formula — all the blueprint\'s chapter-3 and chapter-5 mechanics in a runnable form.'))

story.append(h2('4.1 What the demo implements (mapped to blueprint chapters)'))
story.append(mk([
    ['Blueprint chapter','Implemented in the demo'],
    ['Ch. 3.1 — Movement as backbone','Walk (A/D), fly/jump (W), descend (S), Dragon Dash (Shift+dir, Ki-cost)'],
    ['Ch. 3.2 — Ki as universal economy','One Ki bar gates Ki Blast (J, 14 Ki), Dragon Dash, flight, transform upkeep'],
    ['Ch. 3.3 — Layered counters','Guard (O, free, drains stamina), Super Perception (E, timed, Sonic Sway vs melee, 2 Skill vs blasts)'],
    ['Ch. 3.4 — Sparking! Mode climax','Orange gauge fills from combat → Enter (full gauge + 1 Skill) → 10s free Ki + Ultimate Blast (U)'],
    ['Ch. 5.2 — Log-scaled combat-ratio damage','ratioScale = log10(ratio + 9) live in the engine'],
    ['Ch. 6 — RPG progression (lite)','Skill Count meter (passive fill + on hits), Power Release throttle (K-charge)'],
    ['Ch. 7 — Mid-battle transformation','L costs 1 Skill Count + Ki-upkeep; revert to Base when Ki hits 0'],
], [50*mm, 110*mm]))

story.append(h2('4.2 The fight'))
story.append(p('<b>Goku (player, PL 416 → 1,664 Kaio-ken → 20,800 SSJ) vs Vegeta (AI, PL 18,000 → 900,000 SSJ at half HP).</b> '
    'The canon power gap is real — base Goku barely scratches base Vegeta, so the player must charge Ki, transform to '
    'Kaio-ken, then to Super Saiyan to even the odds, then race to Sparking Mode for the Ultimate Blast. The AI approaches, '
    'attacks, guards, ki-blasts at range, transforms at half HP, and pops Sparking when desperate.'))

story.append(h2('4.3 The hitstun-lock bug + fix'))
story.append(p('The user reported: "as soon as you\'re hit once you can\'t move." Root cause: when a fighter gets hit, '
    '<code>resolveMeleeHit()</code> sets <code>state = "hitstun"</code> and <code>hitstun = m.hitstun</code> frames. '
    'The hitstun counter ticks down each frame, but <b>nothing ever reset the state back to "idle"</b> when the counter '
    'expired — so the fighter stayed permanently locked. Same latent bug affected the "transform" and "sparking" '
    'activation animations.'))
story.append(p('<b>Fix 1 — state-exit logic</b> (added after the timer decrements in updateFighter):'))
story.append(code(
    '// when a locked-state timer expires, return to a controllable state\n'
    'if (f.hitstun === 0 && f.state === "hitstun") f.state = f.onGround ? "idle" : "jump";\n'
    'if (f.stateTimer === 0 && (f.state === "transform" || f.state === "sparking")) {\n'
    '  f.state = f.onGround ? "idle" : "jump";\n'
    '}'))
story.append(p('<b>Fix 2 — Revenge-Counter burst</b> (so combos are escapable, per blueprint Ch. 3.3):'))
story.append(code(
    'if (f.state === "hitstun") {\n'
    '  if (jp.has("e") && f.skillCount >= 1) {\n'
    '    f.skillCount -= 1;\n'
    '    f.hitstun = 0; f.state = "idle";\n'
    '    f.invuln = 30;           // brief i-frames to escape\n'
    '    f.vx = -f.facing * 6;    // back off\n'
    '    f.vy = -6; f.onGround = false;\n'
    '    pushEffect(...counter ring...);\n'
    '  }\n'
    '  return; // no other actions during hitstun\n'
    '}'))

story.append(h2('4.4 Browser verification (Agent Browser)'))
story.append(p('The demo was verified end-to-end via Agent Browser:'))
story.append(b('Page loads HTTP 200, no console errors, canvas renders 960×540 with the navy/blueprint background'))
story.append(b('HUD renders — player HP bar green (#61d555 sampled at full health), Ki bars, Sparking gauges, Skill Count pips, timer'))
story.append(b('Game loop runs at 60fps — the AI Vegeta actively approached and attacked idle Goku'))
story.append(b('Combat resolves with the log-ratio formula — Vegeta\'s higher PL dealt damage, Goku\'s HP drained to 0'))
story.append(b('Win/lose condition works — when Goku\'s HP hit 0, the round ended in DEFEAT (3,296 bright-red "DEFEAT" text pixels + 94.6% dim overlay)'))
story.append(b('Rematch button works — clicked "FIGHT AGAIN" by ref, fresh round started (HP bars green again, overlay cleared)'))
story.append(b('Player keyboard input works — held D, Goku walked right (+113px), confirming the post-fix recovery from hitstun'))

# ═══════════════════════════════════════════════════════════════════
# PART V — THE BT3 DECOMPILATION AUDIT
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part V — The BT3 Decompilation Audit (SLES-549.45)'))
story.append(p('The capstone research: a full Ghidra-decompilation audit of Dragon Ball Z: Budokai Tenkaichi 3 (PAL/EU), '
    'the direct predecessor of Sparking! ZERO, made by the same studio (Spike → Spike Chunfort). This is the closest '
    'available artifact to "the actual code of a Sparking-Zero-style DBZ game."'))

story.append(h2('5.1 File identification'))
story.append(mk([
    ['Field','Value'],
    ['Source','github.com/BenDaOvah/My-dragon-ball-game (single file: sles_549.45_decompiled.c)'],
    ['SHA-256','9083327985cb35edc54160d27a9cbf9c5518c2f90a2551cc5834b94c10e1dec7'],
    ['Size','7,196,736 bytes (7.2 MB)'],
    ['Lines','292,589 (CRLF line endings)'],
    ['File header','"Decompiled from: sles_549.45" / "Architecture: MIPS-R5900"'],
    ['Decoder','Ghidra (FUN_xxxxxxxx / DAT_xxxxxxxx / undefined4 markers)'],
    ['Functions','7,610 (Ghidra /* Function: */ comment count)'],
    ['Unique data globals','1,722 (DAT_ symbols)'],
    ['Symbol recovery','None — every function is FUN_xxxxxxxx (no debug symbols in binary)'],
    ['Disc identity','SLES-54945 = Dragon Ball Z: Budokai Tenkaichi 3 (PAL/EU) — confirmed by SerialStation, VGCollect, Redump'],
    ['Developer','Spike (now Spike Chunfort) — same studio as Sparking! ZERO (2024)'],
], [34*mm, 126*mm]))

story.append(h2('5.2 Architecture overview'))
story.append(p('A bare-metal PS2 game — talks to hardware directly, not through high-level SDK wrappers. Evidence: '
    '80 direct syscall() instructions, 313 references to 0x10000000 (EE register base), 60 VIF1 references (Vector '
    'Interface 1, DMA path to VU1 geometry co-processor), 34 FlushCache calls (cache coherency for DMA).'))
story.append(p('The entry point at 0x00100008 follows the textbook PS2 boot sequence: SYNC barrier → BSS zero-fill loop → '
    'syscall(0x3c) ResetIop → syscall(0x3d) SetGsCrt → FUN_002bb460 IOP module setup → FlushCache → EI enable interrupts → '
    'enter main loop.'))

story.append(h2('5.3 The math primitives — PS2 SIMD (Layer 1)'))
story.append(p('BT3\'s math library uses the PS2 Emotion Engine\'s built-in 128-bit SIMD vector unit (4× 32-bit floats '
    'per register, single-cycle multiply/add). Ghidra surfaces these as _lqc2, _vmul, _vsub, _vopmula, _qmfc2, _sqc2.'))

story.append(h3('FUN_00122128 — the dot product (line 23472)'))
story.append(code(
    'undefined4 FUN_00122128(param_1, param_2) {\n'
    '  auVar1 = _lqc2(*param_1);       // LQC2: load 16 bytes (4 floats) into vector reg\n'
    '  auVar2 = _lqc2(*param_2);       // LQC2: load second vector\n'
    '  auVar1 = _vmul(auVar1, auVar2); // VMUL: component-wise × (x1·x2, y1·y2, z1·z2, w1·w2)\n'
    '  _vaddbc(auVar1, auVar1);        // VADDxBC: horizontal-add (broadcast+add)\n'
    '  auVar1 = _vmaddbc(in_vf3, auVar1); // VMADDBC: multiply-add to accumulator\n'
    '  auVar1 = _qmfc2(auVar1._0_4_); // QMFC2: move vector reg[0] → CPU GPR\n'
    '  return auVar1._0_4_;           // return scalar (the dot product)\n'
    '}'))
story.append(p('<b>Why this matters</b>: every hitbox test in BT3 starts with a dot product. The dot of (attack-ray-direction) '
    '· (triangle-face-normal) tells the engine whether the attack hits the front or back of the surface — that\'s how BT3 '
    'knows "front torso hit" vs "back torso hit" and plays a different reaction.'))

story.append(h3('FUN_00121f78 — vector subtract (line 23455)'))
story.append(code(
    'void FUN_00121f78(param_1, param_2, param_3) {\n'
    '  auVar1 = _lqc2(*param_2);       // load vector B\n'
    '  auVar2 = _lqc2(*param_3);       // load vector C\n'
    '  auVar1 = _vsub(auVar1, auVar2); // VSUB: (B - C) component-wise\n'
    '  _sqc2(auVar1);                  // SQC2: store 128-bit result back to memory\n'
    '  *param_1 = auVar1;\n'
    '}'))
story.append(p('Used to compute <b>edge vectors</b> of triangles: edge1 = vertexB - vertexA. Two edges define a triangle\'s '
    'plane; the cross of those edges gives the face normal.'))

story.append(h3('FUN_00122150 — vector cross product (line 23497)'))
story.append(p('Uses _vopmula + _vopmsub (V**OP**MULA + V**OP**MSUB = Outer-Product Multiply) — Sony\'s <b>dedicated cross-product '
    'instructions</b>. Two instructions, one cross product. Sony built the cross product into silicon because PS2 games '
    'do so many (face normals, edge normals, torque). BT3 uses this to compute every hitbox triangle\'s face normal.'))

story.append(h3('FUN_00231d00 — float approximate-equality (line 194762)'))
story.append(code(
    'bool FUN_00231d00(float param_1, float param_2, float param_3) {\n'
    '  return ABS(param_1 - param_2) <= param_3;\n'
    '}'))
story.append(p('Called <b>18 times</b> by the collision function. The epsilon test that makes geometric math robust on '
    'IEEE-754 floats — direct == comparison is unreliable (0.1 + 0.2 ≠ 0.3 in float), so PS2 games use abs(a-b) ≤ eps. '
    'Tolerances are per-context globals: fGpffffa4cc for general collision, fGpffffa4c0/c4/c8 per-axis.'))

story.append(h2('5.4 The collision function — FUN_00232478 (Layer 2, the heart of combat)'))
story.append(p('The 1,311-line ray-vs-triangle-mesh hitbox function at line 194764. This is the single most relevant function '
    'for the Sparking-Zero build — it\'s BT3\'s actual hitbox system.'))
story.append(p('<b>Signature</b>: FUN_00232478(param_1=attacker geometry, param_2=defender mesh, param_3=output hit-point, '
    'param_4=output hit-local coords, param_5=output closest-distance-so-far).'))
story.append(p('Reading the body: the function transforms the attacker\'s frame into the defender\'s local space (three dot '
    'products for the basis transform), computes edge vectors via vector subtract, iterates the mesh\'s triangles ray-testing '
    'each, keeps the closest hit, and returns the struck face index. The face-index return values (0x0..0xe = 14 faces per '
    'limb hitbox capsule) flow into the per-face reaction dispatch.'))
story.append(p('Key line at the closest-hit loop:'))
story.append(code(
    'if (fVar19 < *param_5) {        // if this hit is CLOSER than current closest\n'
    '  *param_5 = fVar19;            // update the closest distance\n'
    '  iVar9 = 0xd;                  // remember face index 0xd\n'
    '}'))
story.append(p('And the final cross-product edge test (Möller-Trumbore "is the hit point inside the triangle" step):'))
story.append(code(
    'fVar18 = ABS(afStack_190[0x1d] * afStack_190[6] - afStack_190[0x1c] * afStack_190[9]);  // cross Z component\n'
    'lVar2 = FUN_00231d00(ABS(...), fVar18, fGpffffa4cc);  // tolerance-bounded equality (epsilon test)'))
story.append(p('And the face-normal sign determination (which way to knock the character back):'))
story.append(code(
    'if (afStack_190[iVar9 * 3 + 4] <= fGpffffa4d0) iVar4 = -1;  // X normal sign\n'
    'if (afStack_190[iVar9 * 3 + 5] <= fGpffffa4d4) iVar5 = -1;  // Y normal sign\n'
    'if (afStack_190[iVar9 * 3 + 6] <= fGpffffa4d8) iVar6 = -1;  // Z normal sign'))
story.append(p('The (iVar4, iVar5, iVar6) signed integer direction vector — e.g. (-1, +1, 0) means "the struck face\'s normal '
    'points left-up." This is what the caller uses to apply knockback in the correct direction and select the correct reaction animation.'))

story.append(h2('5.5 The input-to-action pipeline (corrected)'))
story.append(p('The user asked me to trace the 6-item input-to-action pipeline. The audit produced two corrections to '
    'my earlier reports and one major new architectural discovery.'))

story.append(h3('Item 1 — Pad reader: FOUND'))
story.append(code(
    '/* line 27182-27186 */\n'
    'undefined * FUN_00126ff8(void) { return &DAT_0032ec08; }\n'
    '\n'
    '/* line 5313-5315 — raw pad read */\n'
    'iVar5 = FUN_00126ff8();\n'
    'if (((*(ulong *)(iVar5 + 0x19f0) & 0x2000) == 0) && ...);'))
story.append(p('Input base = 0x32ec08; pad state at +0x19f0 = absolute address 0x3305f8. Active-low bitmasks '
    '(0x1000 Triangle / 0x2000 Circle / 0x4000 Cross / 0x8000 Square). Census: 219/112/81/132 references respectively.'))

story.append(h3('Item 2 — Input buffer: NOT FOUND as ring buffer'))
story.append(p('Searched for & 0xf (mod-16), & 0x1f (mod-32), do/while < 0x10 (16-frame loops). All matches were '
    'alignment/bitfield ops or DMA packet builders, not input history. BT3 reads current-frame pad state <b>directly</b> '
    'each frame, then runs a translation layer that sets derived intent flags.'))

story.append(h3('Item 3 — Command table: NOT IN ELF (lives in disc data)'))
story.append(p('Zero matches for "skill", "command", "move_list" as identifiers. The command table is part of the DBZ '
    'content, loaded from the disc\'s DATA.BIN / .AFS archives via the FUN_002a2xxx SIF-RPC family. The ELF contains '
    'the recognition engine; the command definitions are data.'))

story.append(h3('Item 4 — State machine: CORRECTION'))
story.append(p('The switches on iGpffffaa28 at lines 15665 and 15842 are <b>NOT</b> the combat state machine — they are '
    'the streaming file-loader FSM. Evidence: every case calls a FUN_002a2xxx file-IO function; the LAB_0011780c label '
    'at line 15818 does <code>iGpffffaa28 = iGpffffaa28 + 1</code> (advance loader state, not combat state).'))

story.append(h3('Item 5 — Skill ID dispatch: PARTIALLY FOUND (via unresolved function pointer)'))
story.append(p('FUN_00232478 (the collision function) is never called by name anywhere in the file — confirmed by '
    'exhaustive grep for 0x00232478, 00232478, 232478, FUN_00232478. Only the definition site (line 194785) matches. '
    'The call site uses an indirect call through a function pointer that Ghidra couldn\'t resolve — the canonical '
    'pattern for an indexed function-pointer Skill-dispatch table (skill_handler_table[skill_id](args)).'))

story.append(h3('Item 6 — Per-character Skill ID table: CLARIFIED'))
story.append(p('BT3 maintains <b>multiple</b> per-character arrays, not one. The 36-byte (0x24) stride is the file-load '
    'context; the 112-byte (0x70) stride is the input/render context (pad state at +0x3c); the 20-byte (0x14) stride '
    'is movement/position. The most-referenced per-char array is iGpffffa9c4 (94 references) — see Section 5.7.'))

story.append(h2('5.6 NEW DISCOVERY — The embedded script VM (line 6872)'))
story.append(p('The biggest finding of the second-pass audit. BT3 implements its own bytecode interpreter:'))
story.append(code(
    '/* line 6870-6883 */\n'
    'sVar1 = *(short *)(iVar3 + aiStack_2c[0]);              // read 16-bit opcode\n'
    'aiStack_2c[0] = aiStack_2c[0] + 2;                       // advance PC by 2 bytes\n'
    'switch(sVar1) {\n'
    '  case 4:   FUN_0010b090(param_1, param_2, aiStack_2c); break;  // opcode 4 handler\n'
    '  case 5:   FUN_0010b3d8(param_1, param_2, aiStack_2c); break;  // opcode 5 handler\n'
    '  case 0xc: FUN_0010b700(param_1, param_2, aiStack_2c); break;  // opcode 0xc handler\n'
    '  case 0x1a: ...\n'
    '}'))
story.append(p('<b>Line-by-line</b>: read a 16-bit opcode from the data buffer at the current "program counter" → advance '
    'PC by 2 → dispatch on opcode value → each case calls a handler function, passing param_1, param_2, and the PC '
    'pointer (so handlers can read their own arguments from the byte stream). The outer do/while runs until it hits a '
    'null terminator — the script\'s end.'))
story.append(p('<b>Why this is the answer to "where\'s the combat state machine"</b>: the per-character combat AI and '
    'behavior logic is encoded as <b>scripts (data)</b>, not as C switches (code). The C provides the interpreter; the '
    'behavior is data streamed from disc. This is the same architecture every major fighting game uses (SF\'s .bac, '
    'Tekken\'s .bin, MK\'s .txt) — the engine is generic, the moves are data.'))

story.append(h2('5.7 The timer-driven AI FSM (line 17612)'))
story.append(code(
    '/* line 17610-17624 */\n'
    'switch(*(int *)(iGpffffaa50 + 0x24)) {            // state ID\n'
    '  case 2:\n'
    '    FUN_00269a08(1);\n'
    '    *(iGpffffaa50 + 0x30) = 4;                    // sub-state\n'
    '    if (0 < *(int *)(iGpffffaa50 + 0x28)) {       // active flag\n'
    '      iVar3 = *(int *)(iGpffffaa50 + 0x2c) + -1;  // decrement timer\n'
    '      *(int *)(iGpffffaa50 + 0x2c) = iVar3;\n'
    '      if (iVar3 < 0) {                             // timer expired\n'
    '        *(iGpffffaa50 + 0x24) = 4;                // transition to state 4\n'
    '        *(iGpffffaa50 + 0x2c) = 100;              // reset timer to 100 frames (~1.67s)\n'
    '        *(iGpffffaa50 + 0x28) = 0;                // clear active flag\n'
    '        FUN_00116c30();\n'
    '      }\n'
    '    }'))
story.append(p('The behavior-context struct at iGpffffaa50 has: +0x24 state ID, +0x28 active flag, +0x2c countdown timer, '
    '+0x30 sub-state. State 2 runs for 100 frames then transitions to state 4. This is the macro-level "what is this '
    'character doing" FSM (idle / approach / attack / retreat / stun); detailed move-execution delegates to the script VM.'))

story.append(h2('5.8 The loaded per-character data table — iGpffffa9c4 (94 references)'))
story.append(mk([
    ['Line','Code','What it proves'],
    ['1883','iGpffffa9c4 = piGpffffa9b0[1];','It\'s a POINTER set from disc-loaded data, not a fixed array'],
    ['35661','iVar7 = iGpffffa9c4 + param_10 * 8;','8-byte stride access (2 floats/ints)'],
    ['37964','iVar3 = iVar4 * 0x10 + iGpffffa9c4;','16-byte stride access (4 floats) — different layout, same buffer'],
    ['37967','iVar3 = iGpffffa9c4 + 0xfff0;','+0xfff0 = 65520 ≈ 64 KB — the END of the array'],
], [12*mm, 70*mm, 78*mm]))
story.append(p('At 8-byte stride = 8,192 entries; at 16-byte stride = 4,096 entries. This is the in-RAM home of the loaded '
    'per-character data — animation keyframes, move definitions, hitbox meshes, or script bytecode. The pointer-set-from-pointer '
    'pattern (line 1883) confirms the data is streamed from disc at runtime, not embedded in the ELF.'))

story.append(h2('5.9 The 4-layer input-to-action pipeline (the real architecture)'))
story.append(code(
    'Layer 1 — RAW PAD READ\n'
    '  FUN_00126ff8() → &DAT_0032ec08; pad state = *(ulong*)(0x32ec08 + 0x19f0)\n'
    '  active-low bitmasks: 0x1000 Tri / 0x2000 Cir / 0x4000 Cross / 0x8000 Square\n'
    '  ↑ read directly each frame, no ring buffer\n'
    '\n'
    'Layer 2 — INPUT-TRANSLATION LAYER (function not yet isolated)\n'
    '  reads raw pad bits, recognizes motion patterns (QCF etc.)\n'
    '  writes derived intent flags (0x40000, 0x80000, 0x400000) to per-char context\n'
    '  ↑ exists (provable from intent-flag reads at lines 10944-10947) but function not found\n'
    '\n'
    'Layer 3 — SCRIPT VM DISPATCH (line 6872)\n'
    '  switch(sVar1) on 16-bit opcodes from disc-loaded bytecode\n'
    '  handlers: FUN_0010b090 (op 4), FUN_0010b3d8 (op 5), FUN_0010b700 (op 0xc)...\n'
    '  the script reads intent flags from Layer 2 and decides what to do\n'
    '  ↑ this is where "skill ID → action" happens — in SCRIPT, not C\n'
    '\n'
    'Layer 4 — EXECUTION (primitives the VM calls)\n'
    '  animation playback, hitbox activation (FUN_00232478 via fn-pointer),\n'
    '  camera/HUD (FUN_00108908), file-streaming (FUN_002a2xxx)'))

story.append(h2('5.10 Five-whys — why is the combat logic in scripts, not C?'))
story.append(mk([
    ['Why','Answer','Evidence'],
    ['1','Script VM instead of hardcoded C switches?','~3,000 move definitions × 98 chars; can\'t recompile shipped console game. VM at line 6872; 64KB/char data table iGpffffa9c4'],
    ['2','Scripts on disc, not in ELF?','ELF is 2MB; 98×64KB=6.3MB script data exceeds usable RAM. iGpffffa9c4 is pointer-set from disc (line 1883)'],
    ['3','Custom VM instead of Lua?','2007: Lua adds ~300KB + interpret-only speed. BT3\'s VM is one switch (line 6872), domain-specific opcodes (play_anim, spawn_hitbox) = denser + faster'],
    ['4','Why matters for Roblox recreation?','Hardcoded Luau if/else hits maintainability wall at ~10 chars. Data-driven SKILLS[skill_id].handler table scales to full roster'],
    ['5','Why same DNA as Sparking ZERO?','Spike → Spike Chunfort lineage (Wikipedia). BT3 modding community edits disc data not ELF — the data-driven property that keeps BT3 modded 18 years later'],
], [10*mm, 60*mm, 90*mm]))

# ═══════════════════════════════════════════════════════════════════
# PART VI — THE MASSIVE HOW-TO LIST
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part VI — The Massive Comprehensive "How to Make a Game Like This" List'))
story.append(p('Every step, every decision, every system — with reasoning. This is the actionable master list.'))

story.append(h2('6.1 Platform decision (Step 1)'))
story.append(mk([
    ['Option','Pros','Cons','Verdict'],
    ['Roblox','Built-in multiplayer + physics + monetization; 538K-download DBZ mods prove it works; Luau is open source','Cannot match AAA graphics; proprietary runtime','BEST for fan/original DBZ games'],
    ['Unreal Engine 5','AAA graphics; Bandai uses it for Sparking ZERO; GAS maps to Noea skill tree; Nanite+Lumen','Steep C++ learning curve; no built-in multiplayer','BEST for commercial original-IP arena fighter'],
    ['Unity','Beginner-friendly; UFE fighting-engine asset; many platforms','Worse 3D graphics than UE5; harder AAA feel','Viable second choice'],
    ['Web (canvas/three.js)','Zero install; shareable URL','Cannot do 3D arena fighter justice; input latency; no real multiplayer','Toy only — what the dragon-arena.tsx demo is'],
], [26*mm, 56*mm, 50*mm, 38*mm]))
story.append(p('<b>Recommendation</b>: For a fan DBZ game with multiplayer and rapid iteration, <b>Roblox</b>. For a commercial '
    'original-IP arena fighter targeting AAA fidelity, <b>Unreal Engine 5</b>. The web demo in this workspace is a '
    'proof-of-concept, not a final platform.'))

story.append(h2('6.2 Engine architecture (Step 2 — the 4-layer pipeline)'))
story.append(p('Build the engine as four layers, mirroring BT3\'s proven architecture:'))
story.append(b('<b>Layer 1 — Raw input</b>: read pad state per-frame into a single integer bitmask. No ring buffer needed '
    '(BT3 doesn\'t use one — it reads current-frame state directly).'))
story.append(b('<b>Layer 2 — Input translation</b>: a per-frame module that recognizes motion patterns (QCF, HCB, dragon-rush) '
    'from the last 4-8 frames of pad state and sets derived intent flags. This is BT3\'s 0x40000+ layer.'))
story.append(b('<b>Layer 3 — Skill dispatch</b>: a function-pointer table indexed by Skill ID, loaded from a data file. '
    'When the translation layer recognizes a command + button, it looks up the Skill ID and calls <code>SKILLS[skill_id].handler(attacker, target)</code>.'))
story.append(b('<b>Layer 4 — Execution primitives</b>: the actual combat ops — play animation, activate hitbox, apply knockback, '
    'spawn particles, update camera. These are the FUN_0010b090/FUN_0010b3d8/FUN_0010b700 equivalents.'))

story.append(h2('6.3 Combat system (Step 3 — the 5-phase loop)'))
story.append(p('Implement the symmetric 5-phase combat loop (both players run it simultaneously):'))
story.append(b('<b>Phase 1 — Neutral</b>: ranged Ki Blasts + Smash Attacks to bait guard/force movement. Build Ki.'))
story.append(b('<b>Phase 2 — Approach</b>: Dragon Dash (Ki-cost) or Z-Burst Dash (more Ki, reposition behind) to close.'))
story.append(b('<b>Phase 3 — Conversion</b>: Vanishing Assault → Dragon Homing / Vanishing Attack / Lightning Attack branch. Bank Skill Count.'))
story.append(b('<b>Phase 4 — Defense read</b>: defender picks from the 5-counter ladder (Guard/Super Perception/Z-Counter/Revenge/Super Counter).'))
story.append(b('<b>Phase 5 — Climax</b>: race to Sparking Mode (full gauge + 1 Skill Count) → Burst Rush → Burst Finish → Ultimate Blast.'))

story.append(h2('6.4 The 5-counter ladder (Step 4 — defense is the skill ceiling)'))
story.append(mk([
    ['Counter','Cost','Best against','Risk'],
    ['Guard','Free (drains stamina)','General pressure','Guard Breakable'],
    ['Super Perception','Ki, or 2 Skill vs blasts','Rush Attacks (Sonic Sway on perfect); Kamehameha','Free vs melee — baitable'],
    ['Z-Counter','Timing only','Vanishing Assault — escalating damage duel','Mistime = take the hit'],
    ['Revenge Counter','1 Skill Count','Being actively combo\'d, any direction','Predictable — baitable by free Perception'],
    ['Super Counter','Precise timing, no resource','Almost any attack, incl. from behind/mid-hit','Hardest timing in the game'],
], [34*mm, 32*mm, 62*mm, 36*mm]))
story.append(p('<b>Why this matters</b>: the tiered risk ladder (free-but-skill → timing-only → Skill-Count panic) is what '
    'produces the "simple to learn, hard to master" curve. Without it, defense is binary (guard or die) and the game feels shallow.'))

story.append(h2('6.5 The damage formula (Step 5 — canon power-level system)'))
story.append(p('Implement the log-scaled combat-ratio formula. Tag every character\'s PL with its source tier '
    '([C]/[D]/[V]/[G]/[S]/[!]) so balance is auditable.'))
story.append(code(
    'ratio = attacker.effectivePL / max(defender.effectivePL, 1)\n'
    'ratioScale = log10(ratio + 9)        // the compression: 1x→1.0, 10x→1.28, 100x→2.04\n'
    'finalDamage = move.baseDamage * ratioScale * (1 - defender.guardReduction)'))
story.append(p('<b>Why log-scale</b>: canon PL spans 7 orders of magnitude (Farmer 5 → Vegito 70B). Linear formulas make '
    '99% of matchups one-shot kills. The log curve keeps a 100× advantage decisive but survivable — exactly the manga\'s drama.'))

story.append(h2('6.6 The hitbox system (Step 6 — BT3\'s actual hit-detection)'))
story.append(p('<b>Use per-limb low-poly hitbox meshes, ray-cast attacks against them, return the struck face/limb index.</b> '
    'This is BT3\'s FUN_00232478 (the 1,311-line collision function) translated to your engine.'))
story.append(p('In Roblox: 14 named BaseParts per character (Face_0x0..Face_0xe), CanCollide=false, Transparency=1. Use '
    'workspace:Raycast() with FilterDescendantsInstances = {attacker.HitboxRig}. The struck part\'s NAME is the face index — '
    'no separate lookup needed.'))
story.append(p('<b>Why per-limb</b>: a single RootPart.Touched detector (what most bad Roblox DBZ games use) cannot distinguish '
    'gut-hit vs face-hit vs back-hit. BT3 returns a struck-face index; that index flows into a per-face reaction dispatch '
    'that plays different animations + applies different knockback. That\'s the mechanical root of the "weighty feel".'))

story.append(h2('6.7 The transformation system (Step 7 — merge two models)'))
story.append(p('Take Sparking\'s resource model (Skill Count cost + stat-spread shift) for the in-fight layer, and Noea\'s '
    'mastery model (Ki-drain upkeep + mastery curve) for the progression layer:'))
story.append(b('<b>In-fight</b>: L costs 1 Skill Count + immediately shifts stat spread (Sparking) AND imposes Ki-drain upkeep '
    'that drops you to Base when Ki hits 0 (Noea).'))
story.append(b('<b>Meta-game</b>: mastery earned by using the form reduces upkeep + raises multiplier (Noea).'))
story.append(b('<b>Climax</b>: form-appropriate Ultimate Blast (Kamehameha/Final Flash/Big Bang) when in Sparking Mode.'))
story.append(p('Canon form multipliers (Daizenshuu 7 + Super Exciting Guide): Kaio-ken ×4, SSJ ×50, SSJ2 ×100, SSJ3 ×400. '
    'God-tier (SSG/SSB/UI/UE/Beast/Rosé) are NOT canon-stated as hard numbers — tag them [S] or [G], never present as canon.'))

story.append(h2('6.8 The animation state machine (Step 8 — layered, not flat)'))
story.append(p('Use <b>layered animation</b>, not a single flat FSM (mocaponline.com research: "patterns for 200+ states"):'))
story.append(mk([
    ['Layer','Holds','Tech'],
    ['Locomotion','Idle/walk/run/fly/dash — continuously blended','Blend tree (1D/2D)'],
    ['Action','Punch/ki-blast/smash/throw — discrete montages with frame data','AnimMontage + state'],
    ['Reaction','Hit-stun/guard/knockback/getup — driven by combat system','State, auto-transitions'],
    ['Transformation','Form-change cinematic + stat-shift — overlays action','Overlay slot'],
    ['Aura/VFX','Sparking glow, Ki aura, charge particles — cosmetic overlay','Niagara + skeleton sockets'],
], [26*mm, 78*mm, 48*mm]))
story.append(p('Frame data schema for every move: startup / active / recovery / cancel-windows / on-hit / on-block. '
    'At 60 FPS: Smash charge ≈30 frames, Super Counter window ≈4-6 frames, Z-Counter ≈8-10. These are the skill-ceiling knobs.'))

story.append(h2('6.9 The script VM / data-driven content (Step 9 — BT3\'s biggest lesson)'))
story.append(p('<b>Do not hardcode combat in code.</b> Build a script VM (or the equivalent data-driven dispatch) so character '
    'moves are data, not code. This is BT3\'s deepest architectural decision (line 6872) and the reason BT3 is still modded 18 years later.'))
story.append(p('In Roblox/Luau, the equivalent is a <b>table of functions indexed by Skill ID, loaded from a ModuleScript</b>:'))
story.append(code(
    'local SKILLS = {\n'
    '  [1] = { handler = function(attacker, target) /* kamehameha */ end },\n'
    '  [2] = { handler = function(attacker, target) /* final flash */ end },\n'
    '  -- loaded from ReplicatedStorage.SkillData (the "disc data" equivalent)\n'
    '}\n'
    'local function dispatchSkill(skillId, attacker, target)\n'
    '  local skill = SKILLS[skillId]\n'
    '  if skill then skill.handler(attacker, target) end\n'
    'end'))
story.append(p('<b>Why this matters</b>: a Roblox DBZ game with hardcoded Luau if/else hits a maintainability wall at ~10 '
    'characters. The data-driven architecture scales to the full roster (98+ chars × ~30 moves = ~3,000 definitions) and '
    'makes the game modder-friendly — exactly the property that keeps BT3 alive.'))

story.append(h2('6.10 Netcode (Step 10 — rollback for PvP)'))
story.append(p('<b>Use rollback netcode for PvP; relay-with-reconciliation for co-op.</b> Delay-based feels bad in practice '
    '(infil.net glossary); rollback never waits for missing input (Ars Technica).'))
story.append(p('Rollback requires: (a) full determinism (fixed-point math or deterministic-float; single-threaded sim; '
    'seeded PRNG), (b) state save/restore in <2ms per frame, (c) input prediction + correction on packet arrival.'))

story.append(h2('6.11 Destructible terrain (Step 11 — the headline feature)'))
story.append(p('Voxel representation + GPU compute-shader marching-cubes for the mesh. A Ki-blast carve = write zeros to '
    'voxel region → re-run marching cubes for affected chunks only → mesh updates. Planet integrity = a single PL '
    'threshold (attack effectivePL > planet integrity → planet destroyed).'))

story.append(h2('6.12 Content layer (Step 12 — the saga backbone)'))
story.append(mk([
    ['Saga','Manga chapters','Power-level range','Boss'],
    ['Raditz/Saiyan','Ch. 195-241','Farmer 5 → Vegeta 18,000','Vegeta (Oozaru ~180K)'],
    ['Namek/Ginyu','Ch. 242-285','Cui 18K → Ginyu 120K','Captain Ginyu'],
    ['Frieza','Ch. 286-329','Frieza 1st 530K → 100% 120M','Frieza (100%)'],
    ['Trunks/Androids','Ch. 330-419','Androids 17/18/16','Imperfect/Semi-Perfect Cell'],
    ['Cell Games','Ch. 420-444','Perfect Cell 900M-1.2B → SSJ2 Gohan ~1.8B','Super Perfect Cell'],
    ['Babidi/Majin Buu','Ch. 445-486','Majin Vegeta → Fat Buu → Super Buu','Super Buu (base)'],
    ['Fusion/Kid Buu','Ch. 487-519','Buuutenks → Buuhan → Ultimate Gohan → Kid Buu','Kid Buu (≈ SSJ3 Goku)'],
    ['DBS god-tier','DBS manga','SSG → SSB → UI/UE → Beast','Beerus, Golden Frieza, Broly, Jiren'],
], [32*mm, 28*mm, 50*mm, 34*mm]))

story.append(h2('6.13 The 4-phase build roadmap (Step 13)'))
story.append(mk([
    ['Phase','Calendar','Team','Deliverable'],
    ['1. Prototype','~2 months','1-2','One character, one arena, full core combat kit + local PvP'],
    ['2. Vertical slice','~3 months','3-5','RPG layer wired; 3 chars; 1 saga; destructible terrain; rollback online'],
    ['3. Beta','~6 months','6-10','Full DBZ roster; all races; tournament mode; first raid boss'],
    ['4. v1.0','~4 months','8-12','DBS god-tier; space travel; full planet system; all raid bosses'],
], [24*mm, 22*mm, 22*mm, 110*mm]))

story.append(h2('6.14 Scope-creep warnings (Step 14 — what NOT to do)'))
story.append(warn('Do not build 164 characters before the core loop feels right. Sparking ZERO shipped 164 because the core kit was shared; building the roster before the kit is the classic fighting-game scope-creep trap.'))
story.append(warn('Do not build the space/planet system before combat is fun. Noea added space in v0.75, well after combat and progression were proven. Reversing this order produces a pretty sandbox with nothing to do.'))
story.append(warn('Do not skip rollback. Shipping a PvP fighting game on delay-based netcode in 2026 is a launch-killer — the fighting-game community will reject it within a week, regardless of how good the combat is.'))
story.append(warn('Do not use a single RootPart.Touched detector. Per-limb named hitboxes with reaction dispatch is the difference between "feels like BT3" and "feels like every other bad Roblox DBZ game."'))

story.append(h2('6.15 Legal (Step 15 — the honest reality)'))
story.append(warn('Dragon Ball, DBZ, DBS, Sparking ZERO, and all character names are trademarks of Bird Studio/Shueisha/Toei/Bandai Namco. Commercial use requires a license.'))
story.append(p('The cleanest path: <b>original IP inspired by Dragon Ball</b> — original names, original planets, but the same '
    'combat feel, the same RPG progression, the same power-level architecture. Canon PL research transfers (numerical-design '
    'pattern, not trademarked). Combat mechanics transfer (game mechanics aren\'t copyrightable). Only names + likenesses '
    'must be original.'))

# ═══════════════════════════════════════════════════════════════════
# PART VII — EVIDENCE INDEX
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part VII — Evidence Index (All Code Citations)'))
story.append(p('Every claim in this compendium, backed by the exact line number and verbatim code from '
    'sles_549.45_decompiled.c (SHA-256 908332…0e1dec7). All citations independently verified via direct file read.'))

story.append(h2('7.1 Pad-accessor FUN_00126ff8 (line 27182-27186)'))
story.append(code('undefined * FUN_00126ff8(void) { return &DAT_0032ec08; }'))
story.append(p('<b>Proof</b>: 1 reference to DAT_0032ec08 in entire file. Input base = 0x32ec08.'))
story.append(p('<b>Line 5313-5315 — raw pad read</b>: <code>iVar5 = FUN_00126ff8(); if (((*(ulong *)(iVar5 + 0x19f0) & 0x2000) == 0) && ...)</code>'))
story.append(p('<b>Interpretation</b>: pad state at absolute address 0x3305f8. 0x2000 = Circle. == 0 = active-low (pressed).'))

story.append(h2('7.2 Derived intent flags 0x40000+ (line 10944-10947)'))
story.append(code('if ((uVar5 & 0x80000) == 0) {\n  if ((uVar5 & 0x40000) == 0) {\n    if (((uVar5 & 0x400000) != 0) && ...);'))
story.append(p('<b>Proof</b>: bits 18, 19, 22 are far above raw-pad range (bits 12-15). These are decoded intent flags — '
    'provable evidence that a translation layer exists.'))

story.append(h2('7.3 case 0xd/0xe are file-loaders (correction evidence)'))
story.append(mk([
    ['Line','Verbatim code','Proof'],
    ['15799','case 0xd: lVar2 = FUN_002a2d68(1,0,&DAT_0032ebc8 + iVar5 * 9);','Calls FUN_002a2d68 (file read)'],
    ['15962','case 0xd: lVar2 = FUN_002a2d68(1,0,&DAT_0032ebc8 + iVar5 * 9);','Calls FUN_002a2d68 (file read)'],
    ['15977','case 0xe: lVar2 = FUN_002a2948(*(undefined4 *)(&DAT_0032ebd8 + iVar5 * 0x24),0,0);','Calls FUN_002a2948 (file op)'],
    ['16816','case 0xd: lVar4 = FUN_002a2d68(1,0,&DAT_0032ebc8 + iVar6 * 9);','Calls FUN_002a2d68 (file read)'],
    ['16823','case 0xe: lVar4 = FUN_002a2888(*(undefined4 *)(&DAT_0032ebd8 + iVar6 * 0x24));','Calls FUN_002a2888 (file op)'],
], [12*mm, 90*mm, 56*mm]))
story.append(p('<b>Interpretation</b>: every case 0xd/0xe calls a FUN_002a2xxx SIF-RPC file-IO function. NOT hit-reaction dispatch.'))

story.append(h2('7.4 State-advance pattern LAB_0011780c (line 15818-15820)'))
story.append(code('LAB_0011780c:\n  iGpffffaa28 = iGpffffaa28 + 1;\n  return uVar3;'))
story.append(p('<b>Proof</b>: 4 goto sites (lines 15679, 15693, 15709, 15778) all inside loader switch cases. '
    'iGpffffaa28 is the loader-state variable, not combat state.'))

story.append(h2('7.5 FUN_00108908 camera math (line 5376-5398)'))
story.append(code(
    'fVar31 = fVar33 - fGpffff803c;                          // delta Y\n'
    'fVar32 = fVar36 - fVar34 * fGpffff8038;                 // delta X\n'
    'fVar27 = SQRT(fVar32 * fVar32 + fVar31 * fVar31);      // Pythagorean distance\n'
    '*piVar20 = *piVar20 + (int)(fVar28 * (fVar32 / fVar27) * 3.0 * 16.0);  // normalized dir × scale'))
story.append(p('<b>Proof</b>: Pythagorean distance + normalized direction × 3.0 × 16.0 (screen-space offset multiplier). '
    'This is camera/HUD math, not input-translation.'))

story.append(h2('7.6 Script VM (line 6870-6883)'))
story.append(code(
    'sVar1 = *(short *)(iVar3 + aiStack_2c[0]);              // read 16-bit opcode\n'
    'aiStack_2c[0] = aiStack_2c[0] + 2;                       // advance PC by 2\n'
    'switch(sVar1) {\n'
    '  case 4:   FUN_0010b090(param_1,param_2,aiStack_2c); break;\n'
    '  case 5:   FUN_0010b3d8(param_1,param_2,aiStack_2c); break;\n'
    '  case 0xc: FUN_0010b700(param_1,param_2,aiStack_2c); break;'))
story.append(p('<b>Proof</b>: 16-bit opcode read from data buffer, PC advances by 2, switch dispatches to handler functions. '
    'This is a bytecode interpreter — BT3\'s embedded scripting language.'))

story.append(h2('7.7 Timer FSM (line 17610-17624)'))
story.append(code(
    'switch(*(int *)(iGpffffaa50 + 0x24)) {\n'
    'case 2:\n'
    '  iVar3 = *(int *)(iGpffffaa50 + 0x2c) + -1;   // decrement timer\n'
    '  if (iVar3 < 0) {\n'
    '    *(iGpffffaa50 + 0x24) = 4;                  // transition to state 4\n'
    '    *(iGpffffaa50 + 0x2c) = 100;                // reset timer to 100 frames'))
story.append(p('<b>Proof</b>: behavior-context struct with +0x24 state, +0x2c countdown timer (resets to 100 = ~1.67s @ 60fps), '
    '+0x28 active flag, +0x30 sub-state. Timer-driven AI/behavior FSM.'))

story.append(h2('7.8 iGpffffa9c4 loaded per-char data table (4 references)'))
story.append(mk([
    ['Line','Code','Proof'],
    ['1883','iGpffffa9c4 = piGpffffa9b0[1];','Pointer set from disc-loaded data, not fixed array'],
    ['35661','iVar7 = iGpffffa9c4 + param_10 * 8;','8-byte stride (2 floats/ints)'],
    ['37964','iVar3 = iVar4 * 0x10 + iGpffffa9c4;','16-byte stride (4 floats) — different layout, same buffer'],
    ['37967','iVar3 = iGpffffa9c4 + 0xfff0;','+0xfff0 = 65520 ≈ 64 KB — END of array'],
], [12*mm, 78*mm, 90*mm]))
story.append(p('<b>Reference count</b>: 94 (most-referenced per-char array).'))

story.append(h2('7.9 Math primitives (PS2 SIMD)'))
story.append(mk([
    ['Function','Line','Purpose','Key instructions'],
    ['FUN_00122128','23472','Dot product','_lqc2 / _vmul / _vaddbc / _vmaddbc / _qmfc2'],
    ['FUN_00121f78','23455','Vector subtract','_lqc2 / _lqc2 / _vsub / _sqc2'],
    ['FUN_00122150','23497','Cross product','_lqc2 / _vopmula / _vopmsub'],
    ['FUN_00231d00','194762','Float approx-eq','ABS(a-b) ≤ tolerance'],
    ['FUN_00231d20','194778','Vector projection','uses FUN_00122128 (dot) + FUN_00231d00'],
    ['FUN_00232478','194764','Ray-triangle-mesh hitbox (1,311 lines)','uses all the above; returns face index 0x0-0xe'],
], [28*mm, 18*mm, 44*mm, 80*mm]))

# ═══════════════════════════════════════════════════════════════════
# PART VIII — SOURCES & BIBLIOGRAPHY
# ═══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(h1('Part VIII — Sources and Bibliography'))

story.append(h2('8.1 Primary source documents (this workspace)'))
story.append(b('<b>sles_549.45_decompiled.c</b> — Ghidra decompilation of BT3 PAL main ELF (7.2 MB, 292,589 lines, 7,610 functions, SHA 908332…0e1dec7), github.com/BenDaOvah/My-dragon-ball-game'))
story.append(b('<b>Dragon_Ball_Game_Design_Blueprint.pdf</b> (25 pp) — the 15-chapter build spec, synthesized in this chat'))
story.append(b('<b>Dragon_Ball_Z_FactChecked_Power_Levels.pdf</b> (12 pp) — canon PL with 8 corrections'))
story.append(b('<b>Dragon_Ball_Sparking_Zero_Combat_Controls_Guide.pdf</b> (7 pp) — the Sparking ZERO combat reference'))
story.append(b('<b>Dragon_Block_Noea_Deep_Research_Guide.pdf</b> (9 pp) — the Noea/DragonMineZ RPG systems'))
story.append(b('<b>Dragon_Block_C_Deep_Research_Guide.pdf</b> (14 pp) — companion mod research'))
story.append(b('<b>Dragon_Ball_Research_Master_Review.pdf</b> (9 pp) — index of the 5 source PDFs'))
story.append(b('<b>Dragon_Ball_Z_Chapter_Power_Levels.pdf</b> (12 pp) — prior chapter-by-chapter guide'))
story.append(b('<b>dragon-arena.tsx</b> (976 lines) — the playable Sparking-Zero-style web demo'))
story.append(b('<b>build_game_design.py</b> / <b>build_dbz_factchecked.py</b> — ReportLab build scripts for the PDFs'))

story.append(h2('8.2 Web research sources (cited throughout)'))
story.append(b('<b>SerialStation</b> (serialstation.com) — SLES-54945 = BT3 PAL disc identity'))
story.append(b('<b>VGCollect</b> (vgcollect.com) — SLES-54945 barcode/release date confirmation'))
story.append(b('<b>Redump</b> (redump.org) — disc database'))
story.append(b('<b>Wikipedia</b> — Budokai Tenkaichi series; Spike → Spike Chunfort lineage; confirms Sparking ZERO same studio'))
story.append(b('<b>TCRF</b> (tcrf.net) — BT3 developer/publisher/platform confirmation'))
story.append(b('<b>Kanzenshuu</b> — Dragon Ball fan-research community of record; manga readings'))
story.append(b('<b>Bandai Namco Europe</b> — Sparking ZERO Beginner\'s Guide, Combos and Features, NEO DLC announcement'))
story.append(b('<b>Ars Technica</b> — "Explaining how fighting games use delay-based and rollback netcode" (2019)'))
story.append(b('<b>infil.net</b> — The Fighting Game Glossary (rollback, delay-based, terminology)'))
story.append(b('<b>CNET / Rolling Stone / Hardcore Gamer</b> — Sparking ZERO reviews'))
story.append(b('<b>GameFAQs / Steam community</b> — player-base analysis ("Ki management is the name of the game", "every character is a setup archetype")'))
story.append(b('<b>gamedev.net / mocaponline.com / gamedev.stackexchange.com</b> — fighting-game state machine design, 200+ state patterns'))
story.append(b('<b>Universal Fighting Engine (UFE)</b> — Unity forum frame-data reference'))
story.append(b('<b>GitHub: Marching-Cubes-On-The-GPU / benwindley.github.io</b> — GPU compute-shader marching-cubes'))
story.append(b('<b>DragonMineZ CurseForge / Modrinth / GitHub</b> — base mod documentation'))
story.append(b('<b>CurseForge — DragonMine Z</b> — 538,000+ downloads; GeckoLib 4.8.3+, TerraBlender'))
story.append(b('<b>GitHub: MatrixDJ96/DBZBT3</b> — open-source BT3 modding tools (extractor, ISO repacker, archive browser)'))
story.append(b('<b>r/decomps</b> — fan decompilation community; BT3 Wii Recomp project'))
story.append(b('<b>Roblox DevForum</b> — fighting-game framework discussions; anime VFX guide'))
story.append(b('<b>kitsblox.com</b> — "How to Make a Roblox Anime Game" guide'))
story.append(b('<b>Luau</b> (github.com/luau-lang/luau) — Roblox\'s open-source scripting language'))
story.append(b('<b>Roblox DBZ games</b> — Dragon Ball Z Final Stand Remastered, Dragon Soul, DragonBlox, Dragon Ball Rage, Super Evolution'))

story.append(h2('8.3 Canon power-level sources (cited in the fact-checked guide)'))
story.append(b('<b>Kanzenshuu</b> — manga compilation readings; the "Over 8,000" (not 9,000) correction'))
story.append(b('<b>Daizenshuu 7</b> — Shueisha\'s official databook; source for SSJ ×50, SSJ2 ×100, SSJ3 ×400, Goku SSJ 150M, Frieza 100% 120M'))
story.append(b('<b>V-Jump magazine</b> — source for the SSJ3 Goku = 24 billion promo value'))
story.append(b('<b>Dragon Ball manga</b> (ch. 195-519) — on-panel scouter readings: Raditz 1,500, Vegeta 18,000, Frieza 1st 530,000, Ginyu 120,000, Gohan enraged 1,307'))
story.append(b('<b>Super Exciting Guide</b> — companion to Daizenshuu; form multiplier confirmation'))

story.append(h2('8.4 Technical reference (PS2/architecture)'))
story.append(b('<b>Sony PS2 EE User\'s Manual</b> — semantics of _lqc2/_vmul/_vsub/_vopmula/_qmfc2/_sqc2 SIMD instructions'))
story.append(b('<b>PS2 libpad headers</b> — standard bitmask definitions (0x1000 Triangle / 0x2000 Circle / 0x4000 Cross / 0x8000 Square, active-low)'))
story.append(b('<b>IEEE 754</b> — 0x3f800000 = 1.0, 0x43000000 = 128.0 (field-type verification)'))
story.append(b('<b>0x10000000</b> = EE register base; <b>0x12000000</b> = GS register base; <b>VIF1</b> = Vector Interface 1 (DMA path to VU1)'))
story.append(b('<b>Möller-Trumbore ray-triangle algorithm</b> — the canonical reference for FUN_00232478\'s math pattern'))
story.append(b('<b>Universal fighting-game architecture</b> — SF .bac / Tekken .bin / MK .txt (the data-driven engine/content split)'))

story.append(h2('8.5 Methodology notes'))
story.append(p('All code citations were verified by direct file read (sed/grep against the SHA-verified file). Where a claim '
    'could not be backed by a specific line citation (the input-translation-layer function body, the call site of '
    'FUN_00232478, the disc data contents), it is noted as "not isolated" / "would need the disc" rather than asserted. '
    'Corrections to earlier claims are documented inline with the corrected evidence.'))

story.append(Spacer(1, 8))
story.append(Paragraph(
    '— End of Master Compendium —',
    ParagraphStyle('End', parent=BODY_S, alignment=TA_CENTER, fontName=BODYI, textColor=TEXT_MUTED)))

# ═══════════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════════
doc = TocDocTemplate(OUTPUT, pagesize=A4,
    leftMargin=14*mm, rightMargin=14*mm, topMargin=18*mm, bottomMargin=16*mm,
    title='Dragon Ball Game — Master Compendium',
    author='Z.ai', creator='Z.ai')
doc.multiBuild(story, onFirstPage=cover_bg, onLaterPages=page_bg)
print(f'Built: {OUTPUT}')
sz = os.path.getsize(OUTPUT)
print(f'Size: {sz:,} bytes ({sz/1024:.1f} KB)')
