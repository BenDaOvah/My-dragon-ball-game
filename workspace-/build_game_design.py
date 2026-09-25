#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dragon Ball Game — Design & Engineering Research Blueprint
How to build a Dragon Ball game that fuses:
  (1) canon-accurate power levels (manga / Daizenshuu 7 / V-Jump sourced),
  (2) Dragon Block Noea / DragonMineZ-style RPG progression (races, six-stat
      sheet, Training Points, Power Release, mastery, transformations),
  (3) Dragon Ball: Sparking! ZERO-style 3D arena-fighter combat.

Research-grounded: every claim is traced to the Sparking! ZERO combat guide,
the Dragon Block Noea deep-research PDF, the fact-checked canon power-level
guide, or independent web sources on fighting-game engine design, rollback
netcode, animation state machines, and destructible voxel terrain.
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

# ━━ Blueprint palette (deep navy + cyan lines + DBZ orange accent) ━━
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
WARN         = colors.HexColor('#ef6c5a')
GOOD         = colors.HexColor('#7bc97a')
TEXT_PRIMARY = colors.HexColor('#e6eaf2')
TEXT_MUTED   = colors.HexColor('#8a94a8')

OUTPUT = '/home/z/my-project/public/Dragon_Ball_Game_Design_Blueprint.pdf'

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
H1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName=BODYB, fontSize=18,
    textColor=ACCENT, spaceBefore=14, spaceAfter=7, leading=22)
H2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName=BODYB, fontSize=12.5,
    textColor=ACCENT_2, spaceBefore=11, spaceAfter=5, leading=16)
H3 = ParagraphStyle('H3', parent=styles['Heading3'], fontName=BODYB, fontSize=10.5,
    textColor=TEXT_PRIMARY, spaceBefore=8, spaceAfter=3, leading=13)
BODY_S = ParagraphStyle('Body', parent=styles['BodyText'], fontName=BODY, fontSize=9.3,
    textColor=TEXT_PRIMARY, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=6)
BULLET = ParagraphStyle('Bullet', parent=BODY_S, leftIndent=12, bulletIndent=2, spaceAfter=3)
CAPTION = ParagraphStyle('Cap', parent=BODY_S, fontName=BODYI, fontSize=8.2,
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
CODE = ParagraphStyle('Code', parent=BODY_S, fontName=MONO, fontSize=8.2,
    textColor=ACCENT, leading=11, alignment=TA_LEFT, leftIndent=10,
    backColor=colors.HexColor('#0d1322'), borderPadding=6, spaceBefore=4, spaceAfter=8)
TOC_L0 = ParagraphStyle('TOC0', fontName=BODYB, fontSize=10.5, textColor=ACCENT,
    leftIndent=0, spaceBefore=5, spaceAfter=1, leading=14)
TOC_L1 = ParagraphStyle('TOC1', fontName=BODY, fontSize=9, textColor=TEXT_PRIMARY,
    leftIndent=16, spaceBefore=0, spaceAfter=0, leading=12)

def page_bg(canv, doc):
    canv.saveState()
    canv.setFillColor(PAGE_BG); canv.rect(0,0,A4[0],A4[1], fill=1, stroke=0)
    # blueprint grid
    canv.setStrokeColor(colors.HexColor('#16203a')); canv.setLineWidth(0.3)
    for x in range(0, int(A4[0]/mm)+1, 10):
        canv.line(x*mm, 12*mm, x*mm, A4[1]-12*mm)
    for y in range(1, int((A4[1]-24*mm)/mm)//10 + 1):
        canv.line(12*mm, y*10*mm + 12*mm, A4[0]-12*mm, y*10*mm + 12*mm)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(1.0)
    canv.line(12*mm, A4[1]-14*mm, A4[0]-12*mm, A4[1]-14*mm)
    canv.setFont(BODY, 8); canv.setFillColor(TEXT_MUTED)
    canv.drawString(12*mm, 7*mm, 'Dragon Ball Game — Design & Engineering Blueprint')
    canv.drawRightString(A4[0]-12*mm, 7*mm, f'Page {doc.page}')
    canv.restoreState()

def cover_bg(canv, doc):
    canv.saveState()
    canv.setFillColor(PAGE_BG); canv.rect(0,0,A4[0],A4[1], fill=1, stroke=0)
    # dense blueprint grid
    canv.setStrokeColor(colors.HexColor('#16203a')); canv.setLineWidth(0.3)
    for x in range(0, int(A4[0]/mm)+1, 8):
        canv.line(x*mm, 0, x*mm, A4[1])
    for y in range(0, int(A4[1]/mm)//8 + 1):
        canv.line(0, y*8*mm, A4[0], y*8*mm)
    # major construction lines
    canv.setStrokeColor(ACCENT); canv.setLineWidth(1.2)
    canv.line(0, A4[1]-60*mm, A4[0], A4[1]-60*mm)
    canv.line(0, 60*mm, A4[0], 60*mm)
    canv.setStrokeColor(ACCENT_2); canv.setLineWidth(0.8)
    canv.line(18*mm, A4[1]-60*mm, 18*mm, 60*mm)
    canv.line(A4[0]-18*mm, A4[1]-60*mm, A4[0]-18*mm, 60*mm)
    # corner detail circles (blueprint compass marks)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(0.6)
    for cx, cy in [(25*mm, A4[1]-25*mm),(A4[0]-25*mm, A4[1]-25*mm),
                   (25*mm, 25*mm),(A4[0]-25*mm, 25*mm)]:
        canv.circle(cx, cy, 8*mm, fill=0, stroke=1)
        canv.circle(cx, cy, 3*mm, fill=0, stroke=1)
    # title block (lower-right, drafting-style)
    canv.setFillColor(COVER_BLOCK); canv.rect(A4[0]-78*mm, 14*mm, 66*mm, 34*mm, fill=1, stroke=0)
    canv.setStrokeColor(ACCENT); canv.setLineWidth(0.6)
    canv.rect(A4[0]-78*mm, 14*mm, 66*mm, 34*mm, fill=0, stroke=1)
    canv.setFont(BODYB, 7); canv.setFillColor(ACCENT)
    canv.drawString(A4[0]-75*mm, 41*mm, 'TITLE BLOCK')
    canv.setFont(BODY, 6.5); canv.setFillColor(TEXT_MUTED)
    canv.drawString(A4[0]-75*mm, 37*mm, 'Project:  Dragon Ball Game')
    canv.drawString(A4[0]-75*mm, 34*mm, 'Scale:    N/A (design doc)')
    canv.drawString(A4[0]-75*mm, 31*mm, 'Sheet:    01 of 01')
    canv.drawString(A67*mm if False else A4[0]-75*mm, 28*mm, 'Drawn:    Z.ai Research')
    canv.drawString(A4[0]-75*mm, 25*mm, 'Date:     2026')
    canv.drawString(A4[0]-75*mm, 22*mm, 'Rev:      A — Final')
    canv.drawString(A4[0]-75*mm, 18*mm, 'Status:   RESEARCH BLUEPRINT')
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
        ('FONTNAME',(0,0),(-1,-1),BODY), ('FONTSIZE',(0,0),(-1,-1),8.0),
        ('TEXTCOLOR',(0,0),(-1,-1),TEXT_PRIMARY), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('GRID',(0,0),(-1,-1),0.35,BORDER),
        ('BACKGROUND',(0,0),(-1,-1),SECTION_BG),
    ]
    if header:
        cmds += [('BACKGROUND',(0,0),(-1,0),HEADER_FILL),('FONTNAME',(0,0),(-1,0),BODYB),
                 ('TEXTCOLOR',(0,0),(-1,0),ACCENT), ('FONTSIZE',(0,0),(-1,0),8.3)]
        for i in range(1,nrows):
            if i%2==1: cmds.append(('BACKGROUND',(0,i),(-1,i),TABLE_STRIPE))
    else:
        for i in range(0,nrows):
            if i%2==1: cmds.append(('BACKGROUND',(0,i),(-1,i),TABLE_STRIPE))
    return TableStyle(cmds)
def mk(rows, widths, header=True):
    t = Table(rows, colWidths=widths); t.setStyle(tstyle(len(rows),header)); return t

story = []

# ════════════ COVER ════════════
ct  = ParagraphStyle('CT',  fontName=BODYB, fontSize=34, textColor=ACCENT, leading=40, leftIndent=20*mm, alignment=TA_LEFT)
ct2 = ParagraphStyle('CT2', fontName=BODY,  fontSize=17, textColor=TEXT_PRIMARY, leading=21, leftIndent=20*mm, spaceBefore=4, alignment=TA_LEFT)
cs  = ParagraphStyle('CS',  fontName=BODY,  fontSize=11.5, textColor=TEXT_PRIMARY, leading=16, leftIndent=20*mm, spaceBefore=10, alignment=TA_LEFT)
cg  = ParagraphStyle('CG',  fontName=BODYI, fontSize=9.2, textColor=TEXT_MUTED, leading=13, leftIndent=20*mm, spaceBefore=14, alignment=TA_LEFT)
story.append(Spacer(1, 48*mm))
story.append(Paragraph('DRAGON BALL', ct))
story.append(Paragraph('Game Design &amp; Engineering Blueprint', ct2))
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    'A research-grounded plan for building a Dragon Ball game that fuses<br/>'
    '<b><font color="#ff8c2a">Sparking! ZERO-style 3D arena combat</font></b>, '
    '<b><font color="#7bc97a">Dragon Block Noea / DragonMineZ RPG progression</font></b>,<br/>'
    'and <b><font color="#00e5ff">canon-accurate power levels</font></b> '
    'into a single coherent title.', cs))
story.append(Spacer(1, 14*mm))
story.append(Paragraph(
    'Synthesizes four research inputs:<br/>'
    '&nbsp;&nbsp;1. Dragon Ball: Sparking! ZERO — Combat &amp; Controls Guide (7 pp)<br/>'
    '&nbsp;&nbsp;2. Dragon Block Noea — Deep Research Guide (9 pp)<br/>'
    '&nbsp;&nbsp;3. Dragon Ball Z — Fact-Checked Power Levels (12 pp)<br/>'
    '&nbsp;&nbsp;4. Independent web research on fighting-game engine design,<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rollback netcode, animation state machines, voxel terrain', cg))
story.append(PageBreak())

# ════════════ TOC ════════════
toc = TableOfContents(); toc.levelStyles = [TOC_L0, TOC_L1]
story.append(Paragraph('Table of Contents', H1))
story.append(Spacer(1, 4)); story.append(toc)
story.append(PageBreak())

# ════════════ CH 1 — EXECUTIVE SUMMARY ════════════
story.append(h1('1. Executive Summary — The Game Concept'))
story.append(p(
    'This document specifies how to build a Dragon Ball game that combines the three things the research '
    'established as the genre\'s best practices: the <b>combat feel</b> of <i>Dragon Ball: Sparking! ZERO</i> '
    '(Bandai Namco, 2024), the <b>progression depth</b> of the fan-made <i>Dragon Block Noea / DragonMineZ</i> '
    'Minecraft mod ecosystem (Forge 1.20.1, 2024–2026), and the <b>canon-accurate power levels</b> documented in '
    'the fact-checked power-scaling guide (sourced to the manga, Daizenshuu 7, and V-Jump).'))
story.append(p(
    'The core thesis: <b>Sparking! ZERO\'s combat is effective because it is not a combo-memory game — it is a '
    'positioning and resource-read game</b>. The 3D arena, the Ki economy, and the layered counter system make '
    'every exchange a series of small reads rather than one long executable string. Layering Noea-style RPG '
    'progression (races, six-stat sheet, Training Points, Power Release, mastery) on top gives the player '
    'something to <i>do between fights</i>, and canon power levels give every number a defensible meaning '
    'instead of an arbitrary one.'))
story.append(h2('1.1 The Three Pillars'))
story.append(mk([
    ['Pillar','Source game/mod','What it contributes','Research basis'],
    ['Combat','Sparking! ZERO','3D arena movement, Ki economy, layered counters, '
     'Sparking! Mode climax, transformation-as-resource','Sparking! ZERO Combat Guide (7 pp)'],
    ['Progression','Dragon Block Noea / DragonMineZ','Races, six-stat sheet, Training Points, '
     'Power Release, mastery curve, skill trees, space/planet systems','Noea Deep Research Guide (9 pp)'],
    ['Data','Canon power-scaling','Every character\'s PL tagged to manga/Daizenshuu/V-Jump; '
     'combat-ratio damage formula; contested values flagged','Fact-Checked Power Levels (12 pp)'],
], [22*mm, 38*mm, 64*mm, 50*mm]))
story.append(Spacer(1, 4))
story.append(note(
    'Each pillar is independently proven. Sparking! ZERO shipped to strong reviews for its combat depth; '
    'DragonMineZ has 538,000+ CurseForge downloads; the canon power-level guide cross-references every value '
    'against Kanzenshuu, the manga\'s own scouter readings, and Daizenshuu 7. Combining them is the design '
    'challenge this document solves.'))

story.append(h2('1.2 The One-Sentence Pitch'))
story.append(p(
    '<i>"A 3D arena Dragon Ball fighter where every number on the screen means something real — '
    'your power level is canon-accurate, your training earned it, and every fight is a read-and-punish '
    'duel in the sky, not a combo-execution test."</i>'))

# ════════════ CH 2 — THE THREE SOURCE GAMES ════════════
story.append(PageBreak())
story.append(h1('2. The Three Source Systems — What Each Teaches'))
story.append(p(
    'Before specifying the merged design, it is worth establishing exactly what each source system does well '
    'and where each is weak. The merged game takes the strong half of each and discards the weak half.'))

story.append(h2('2.1 Comparative Matrix'))
story.append(mk([
    ['Dimension','Sparking! ZERO','Dragon Block Noea','Canon PL research'],
    ['Genre','3D arena fighter (fighting game)','Character-progression RPG (Minecraft mod)','Reference dataset'],
    ['Combat depth','Very high — layered counters, Ki economy','Low — auto-attack + ability keys','N/A (data)'],
    ['Progression','Flat — 5-point stat spread per character','Deep — 6 stats + TP + mastery + skills','N/A'],
    ['Power accuracy','Loosely canon-flavored (stat-spread shifts per form)','Canon-faithful multipliers (×50/×100/×400), ceiling extends past canon','Rigorously sourced'],
    ['Content scope','164-character roster, story + offline','Solo-modded sagas, space, planets, raids','Manga ch.1–325 + DBS'],
    ['Multiplayer','Online PvP (delay/rollback)','Minecraft server co-op','N/A'],
    ['Built with','Unreal Engine 5 (Bandai)','Minecraft Forge + GeckoLib + Java','N/A'],
    ['Strength to take','Combat feel, counter layering','RPG systems, transformation mastery','Damage math, PL data'],
    ['Weakness to drop','Shallow progression, no training','Shallow combat, auto-attack','No game — pure reference'],
], [26*mm, 38*mm, 40*mm, 38*mm, 32*mm]))

story.append(h2('2.2 What "Accurate Power Levels" Means in Practice'))
story.append(p(
    'The fact-checked canon guide establishes a five-tier source hierarchy: [C] manga-stated on-panel, '
    '[D] Daizenshuu 7 (Shueisha\'s official databook), [V] V-Jump magazine promo values, [G] game tie-in '
    '(Kakarot / Scouter Battle Taikan Kamehameha), [S] community scaling via canon multipliers, and [!] '
    'contested where sources disagree. A faithful game should treat these tiers as data flags on every '
    'character record — so a modder or designer can see at a glance whether a number is Toriyama-stated or '
    'community-derived, and tune accordingly.'))
story.append(mk([
    ['Tier','Source','Example value','Reliability'],
    ['[C]','Manga (on-panel scouter)','Raditz 1,500 — Vegeta 18,000 — Frieza 1st 530,000','Highest'],
    ['[D]','Daizenshuu 7','Goku SSJ 150,000,000 — Frieza 100% 120,000,000','High (official databook)'],
    ['[V]','V-Jump magazine','SSJ3 Goku 24,000,000,000','Medium (promo, sometimes inconsistent)'],
    ['[G]','Game tie-in','Android 17/18/16 V-Jump-style values','Low (often inconsistent)'],
    ['[S]','Scaling via canon multipliers','SSJ2 Gohan ~1.8B (×100 of ~7M base, manga-stated multiplier)','Medium-high'],
    ['[!]','Contested','Nappa 4,000 (Daizenshuu vs manga showings); Kid Buu 1.15B (arcade) vs 24B (manga equality)','Flag both, prefer manga'],
], [14*mm, 50*mm, 70*mm, 40*mm]))
story.append(Spacer(1, 4))
story.append(ok(
    'Takeaway: tag every power-level field in the character database with its source tier. This makes '
    'tuning, modding, and balance review auditable — and lets players who care about canon verify any number.'))

# ════════════ CH 3 — WHY SPARKING ZERO WORKS ════════════
story.append(PageBreak())
story.append(h1('3. Why Sparking! ZERO\'s Combat Is So Effective'))
story.append(p(
    'Independent reviews (CNET, Rolling Stone, Hardcore Gamer) and the player-base consensus on GameFAQs / '
    'Steam all converge on the same read: Sparking! ZERO is "anime fighting perfection" specifically because '
    'its combat is <b>simple to learn and takes time to master</b>, and because it produces a <b>theatrical '
    'look</b> (the source of the Steam-forum complaint that the system "neuters itself once you learn it" — '
    'which is the same property, viewed from the casual side). The design rests on five interlocking choices.'))

story.append(h2('3.1 Reason 1 — Movement is the backbone, not combos'))
story.append(p(
    'Sparking! ZERO is described by its own guide as <i>"closer to footsies in the sky than a traditional 2D '
    'fighter"</i>. The kit is built around <b>Step/Short Dash</b> (spacing), <b>Dragon Dash</b> (close '
    'distance, Ki-cost), <b>Z-Burst Dash</b> (reposition behind the opponent for extra Ki — the engine behind '
    'the hard-to-block Burst Rush), and <b>Quick Ascend/Descend</b> (vertical fighting, which several attacks '
    'specifically exploit). The result: <b>positional reads matter more than memorized strings</b>. A player '
    'who never learns a single long combo can still win by out-positioning and out-resource-managing the '
    'opponent. This is the single biggest lesson to take from Sparking! ZERO — the combat ceiling is set by '
    'movement, not by combo length.'))
story.append(note(
    'Design implication: the character controller must make movement feel <i>good</i> before any attack is '
    'wired up. If the dash, step, fly and ascend don\'t feel responsive, the entire combat model collapses. '
    'This is the first system to prototype and the last to polish.'))

story.append(h2('3.2 Reason 2 — Ki is the universal economy'))
story.append(p(
    'Ki is the single resource that gates <i>everything</i>: Ki Blasts, Blast Attacks (Super Attacks), Dragon '
    'Dash, Z-Burst Dash, Quick Ascend/Descend, Vanishing Assault follow-ups, Super Perception (sometimes), '
    'and the path to filling the Sparking Gauge. There is no separate "stamina" or "meter" pool fragmenting '
    'attention — just Ki. The GameFAQs thread puts it directly: <i>"Ki management is the name of the game here. '
    'If you win the war, you get smash damage and oki advantage."</i>'))
story.append(p(
    'The reason this works: <b>one resource = one decision tree</b>. Every action can be evaluated against '
    'every other action on the same scale ("does this Ki spend beat that Ki spend?"), which makes the game '
    'readable for spectators and learnable for newcomers. Splitting resources (stamina + super meter + burst '
    'gauge + transformation stock, as some fighters do) fragments the read and raises the floor without '
    'raising the ceiling.'))

story.append(h2('3.3 Reason 3 — Layered counters with different costs'))
story.append(p(
    'The defense tree is where the skill ceiling actually lives. Sparking! ZERO layers five counter tools, '
    'each with a different cost and a different best-case target — so defense is never "guard or die":'))
story.append(mk([
    ['Counter','Cost','Best against','Risk'],
    ['Super Perception','Ki, or 2 Skill Count vs blasts','Rush Attacks (Sonic Sway on perfect timing); Kamehameha','Free vs melee — baitable'],
    ['Z-Counter','Timing only','Vanishing Assault — escalating damage duel','Mistime = take the hit'],
    ['Revenge Counter','1 Skill Count','Being actively combo\'d, any direction','Predictable — baitable by free Perception'],
    ['Super Counter','Precise timing, no resource','Almost any attack, incl. from behind / mid-hit','Hardest timing in the game'],
    ['High-Speed Evasion / Step-in Sway','Timing only','General attack avoidance','No punish on whiff'],
], [38*mm, 32*mm, 60*mm, 38*mm]))
story.append(Spacer(1, 4))
story.append(p(
    'The intended defensive loop, per the guide: <i>guard or evade against unclear pressure → use Perception '
    'or Z-Counter to punish predictable offense for free → save Revenge/Super Counter as a Skill-Count-backed '
    'panic button once you\'re actually being combo\'d</i>. This is a <b>tiered risk ladder</b> — the player '
    'always has a cheaper option that requires more skill, and a more expensive option that requires less. '
    'That ladder is what produces the "simple to learn, hard to master" curve.'))

story.append(h2('3.4 Reason 4 — Sparking! Mode is the shared climax'))
story.append(p(
    'Sparking! Mode (Sparking Gauge full + ≥1 Skill Count) is the game\'s comeback / payoff state: it unlocks '
    'the Ultimate Blast, makes normally Ki-costing actions free, grants Ki-Blast-stun immunity, and adds '
    'damage/speed/HP-regen. The advanced sequence — <b>Burst Rush → Burst Finish → Sparking Combo → Ultimate '
    'Blast</b> — is the canonical "win condition" both players are racing toward.'))
story.append(p(
    'Why this is effective: it gives every match a <b>shared dramatic arc</b>. Both players can see the '
    'Sparking Gauge fill; both know the climax is coming; the question is who gets there first and whether '
    'they can land the setup. This is the structural reason Sparking! ZERO feels "theatrical" — the resource '
    'economy is literally a three-act structure (neutral → Sparking race → Ultimate Blast resolution).'))

story.append(h2('3.5 Reason 5 — Every character is a "setup archetype"'))
story.append(p(
    'A Steam-community observation that captures the design intent: <i>"Every character is a setup archetype. '
    'It is designed to work off these systems to make a theatrical look."</i> Unlike traditional fighters '
    'where characters are differentiated by their combo strings (rushdown / zoner / grappler), Sparking! '
    'ZERO differentiates by <b>what they want to set up</b> — which Blast Attack, which Ultimate, which '
    'transformation chain. The shared core kit means a player who learns the system can pilot any character; '
    'the character select is a question of <i>preference in setup style</i>, not of learning a new control '
    'scheme.'))
story.append(ok(
    'Takeaway for our build: keep the core combat kit identical across all characters. Differentiate by '
    '(a) Blast/Ultimate moveset, (b) transformation ladder, (c) stat-spread weights, (d) unique passives. '
    'Do NOT give different characters different control schemes — that fragments the read for both players '
    'and spectators.'))

# ════════════ CH 4 — COMBAT LOOP ANATOMY ════════════
story.append(PageBreak())
story.append(h1('4. The Combat Loop — Anatomy of One Exchange'))
story.append(p(
    'A high-level Sparking! ZERO exchange, as documented in the official Bandai beginner guide and '
    'breakdowns by TheGamer / NoobFeed / GamingBolt, follows a repeatable five-phase loop. Mapping it '
    'explicitly is the foundation of the merged game\'s combat design — every system in the build must serve '
    'one of these five phases.'))

story.append(h2('4.1 The Five-Phase Loop'))
story.append(mk([
    ['Phase','Player goal','Primary tools','Resource state'],
    ['1. Neutral','Bait a guard or force movement without overspending Ki','Ki Blasts, Smash Attacks at range','Ki building up'],
    ['2. Approach','Close distance; punish a whiffed/over-held guard','Dragon Dash, Z-Burst Dash','Ki spent on dash'],
    ['3. Conversion','Convert one read into a full offensive sequence','Vanishing Assault → Dragon Homing / Vanishing / Lightning Attack','Skill Count banked'],
    ['4. Defense read','Defender picks the right counter from the ladder','Super Perception / Z-Counter / Revenge / Super Counter','Skill Count spent if panic'],
    ['5. Climax','Race to Sparking Mode; land Ultimate Blast','Sparking Mode → Burst Rush → Burst Finish → Ultimate Blast','Sparking Gauge + Skill Count'],
], [22*mm, 50*mm, 56*mm, 38*mm]))
story.append(Spacer(1, 4))
story.append(p(
    'The loop is <b>symmetric</b> — both players are running it simultaneously, which is what makes the game '
    'a duel rather than a single-player combo exhibition. The Ki economy (Phase 1), the Skill Count bank '
    '(Phase 3), and the Sparking Gauge (Phase 5) are three resource clocks ticking in parallel, and the '
    'player who reads their opponent\'s clock-state best wins.'))

story.append(h2('4.2 Where the RPG Layer Plugs In'))
story.append(p(
    'The canon power-level system and the Noea-style RPG layer sit at <b>two specific points</b> in this loop, '
    'not across all of it — which is why they can be added without breaking the combat feel:'))
story.append(mk([
    ['Plug-in point','What the RPG/canon layer adds','Effect on combat feel'],
    ['Pre-match (loadout)','Race + six-stat sheet + trained PL + chosen transformation ladder','Determines the damage ratio and form options — but the in-fight kit is identical'],
    ['Phase 3 (Conversion)','Mid-battle transformation costs Skill Count + shifts stat spread (Sparking model) OR costs Ki-upkeep + mastery (Noea model)','A strategic resource decision, not a combo interruption'],
    ['Phase 5 (Climax)','Ultimate Blast is the form-appropriate finisher (Kamehameha / Final Flash / Big Bang Attack)','The payoff is canon-accurate to the character\'s saga peak'],
], [32*mm, 70*mm, 64*mm]))
story.append(Spacer(1, 4))
story.append(note(
    'The combat loop itself is untouched by the RPG layer. A Goku at 416 PL and a Goku at 150,000,000 PL '
    'pilot the same character controller with the same moves — only the damage numbers and the available '
    'forms differ. This is exactly how Sparking! ZERO handles its 164-character roster, and it is the '
    'only sane way to merge an RPG grind with a fighting game.'))

# ════════════ CH 5 — CANON POWER LEVEL SYSTEM ════════════
story.append(PageBreak())
story.append(h1('5. Canon Power-Level System — The Data Backbone'))
story.append(p(
    'This chapter specifies how to turn the fact-checked canon power levels into a working in-game damage '
    'system. The core problem: canon PL spans <b>seven orders of magnitude</b> (Farmer 5 → Vegito ~70 billion), '
    'and a linear damage formula makes 99% of matchups one-shot kills. The solution is a <b>log-scaled combat '
    'ratio</b>, which is exactly the approach the Dragon Block Noea mod takes ("damage scales with effective '
    'PL vs enemy PL") and which the dragon-power.js prototype in this very workspace implements.'))

story.append(h2('5.1 The Data Model'))
story.append(p(
    'Every character record carries the following fields, each tagged with the source tier from Chapter 2.2:'))
story.append(code(
    'CharacterRecord {\n'
    '  id:           "goku"\n'
    '  name:         "Goku"\n'
    '  race:         SAIYAN\n'
    '  basePL:        416              // [C] manga ch.215 (weighted)\n'
    '  basePLSource: "MANGA_CH215"\n'
    '  forms: [\n'
    '    { name:"Base",        plMul:1,   tier:"[C]"  },\n'
    '    { name:"Kaio-ken",    plMul:4,   tier:"[C]"  },  // manga-stated\n'
    '    { name:"Super Saiyan",plMul:50,  tier:"[D]"  },  // Daizenshuu 7\n'
    '    { name:"SSJ2",        plMul:100, tier:"[D]"  },\n'
    '    { name:"SSJ3",        plMul:400, tier:"[D]"  },\n'
    '  ]\n'
    '  statSpread:   { STR:7, SKP:8, RES:7, VIT:8, PWR:9, ENE:7 } // /10\n'
    '  passives:     ["ZENKAI"]\n'
    '  blast:        "Kamehameha"\n'
    '  ultimate:     "Super Kamehameha"\n'
    '}'))
story.append(p(
    'The <b>effectivePL</b> at any moment is <code>basePL × form.plMul × powerRelease%</code>, exactly '
    'mirroring the Noea mod\'s Power Release throttle (raw stats are not fully "on" by default — release '
    'charges from 0% to a 50% cap, raised to 100% by the Potential Unlock passive).'))

story.append(h2('5.2 The Combat-Ratio Damage Formula'))
story.append(p(
    'The damage formula must compress seven orders of magnitude into a playable range. The proven approach '
    '(used by Noea, used by the dragon-power.js prototype in this workspace, and recommended by RPG-design '
    'literature for "ratio-based" scaling) is:'))
story.append(code(
    'ratio      = attacker.effectivePL / max(defender.effectivePL, 1)\n'
    'ratioScale = log10(ratio + 9)        // 1× → ~1, 10× → ~2, 100× → ~3, 1000× → ~4\n'
    'baseDamage = move.baseDamage * ratioScale * move.typeMultiplier\n'
    'finalDamage = baseDamage * (1 - defender.guardReduction)\n'
    '// example: Goku 416 (Kaio-ken ×4 = 1664) vs Vegeta 18000\n'
    '//   ratio = 1664/18000 = 0.092\n'
    '//   ratioScale = log10(0.092 + 9) = log10(9.092) ≈ 0.959\n'
    '//   → Goku hits Vegeta for ~baseDamage × 0.96  (he\'s outmatched ~11×, hits ~4% weak)\n'
    '// example: SSJ Goku 150,000,000 vs Frieza 100% 120,000,000\n'
    '//   ratio = 1.25, ratioScale = log10(10.25) ≈ 1.01\n'
    '//   → roughly even exchange, slight Goku edge'))
story.append(p(
    'The log curve means: a 10× PL advantage is a meaningful but not fight-ending edge (~1.0× base damage '
    'vs ~0.95× for an even match); a 100× advantage is decisive but the underdog still does <i>some</i> damage; '
    'a 1000× advantage is a one-shot. This <b>preserves the drama of the source material</b> — Raditz '
    'torturing Goku and Piccolo (1,500 vs 416/408, ~3.6× advantage) plays out as a real fight, not a one-hit '
    'kill, which is exactly what the manga shows.'))

story.append(h2('5.3 Why Linear PL Fails (and Noea Avoids It)'))
story.append(p(
    'A naive <code>damage = attackerPL - defenderPL</code> or '
    '<code>damage = attackerPL / defenderPL × base</code> formula produces absurd results: Goku at 416 vs '
    'Frieza at 120,000,000 would do 0.00035% of a hit, and the reverse would be a 288,000× one-shot. The '
    'log-scaled ratio is the minimum viable compression. Noea\'s own implementation (per the Noea guide: '
    '"damage scales with effectivePL vs enemyPL") uses the same family of formula, which is why its 200M vs '
    '600M immortal-vs-Vegeta demo still produces a watchable exchange rather than an instant kill.'))

story.append(h2('5.4 Verified Canon Reference Table (Saga Peaks)'))
story.append(p(
    'The following peaks are the canon-verified damage anchors for the saga-difficulty curve. Every other '
    'value in the character database scales multiplicatively from these via the Daizenshuu 7 multipliers '
    '(×50 SSJ, ×100 SSJ2, ×400 SSJ3) and the manga-stated form relationships.'))
story.append(mk([
    ['Character (peak form)','PL','Source','Saga'],
    ['Raditz','1,500','[C] Daizenshuu 7','Saiyan'],
    ['Vegeta (Saiyan saga)','18,000','[C] manga ch.249','Saiyan'],
    ['Ginyu','120,000','[C] manga ch.285','Namek'],
    ['Frieza 1st form','530,000','[C] manga ch.294','Namek'],
    ['Frieza 100%','120,000,000','[D] Daizenshuu 7','Namek'],
    ['Goku SSJ','150,000,000','[D] Daizenshuu 7','Namek'],
    ['SSJ2 Gohan','~1,800,000,000','[S] (> Super Perfect Cell ~1.6B)','Cell'],
    ['SSJ3 Goku','24,000,000,000','[V] V-Jump','Buu'],
    ['SSJ3 Gotenks','~30,000,000,000','[S] (> SSJ3 Goku, manga-stated)','Buu'],
    ['Ultimate Gohan','~35,000,000,000','[S] (> Super Buu, > Gotenks, > Goku)','Buu'],
    ['Kid Buu','~24,000,000,000','[V]/[S] (≈ SSJ3 Goku, manga equality)','Buu'],
    ['Vegito (base)','~70,000,000,000+','[S] (> Buuhan)','Buu'],
], [56*mm, 38*mm, 56*mm, 26*mm]))
story.append(Spacer(1, 4))
story.append(warn(
    'Contested values (Nappa 4,000; the V-Jump Android 17/18/16 numbers; Kid Buu 1.15B from the arcade '
    'game) must be flagged [!] in the database and presented with both numbers, preferring the manga '
    'equality (Kid Buu ≈ SSJ3 Goku ≈ 24B) over the arcade value. See the fact-checked guide for the full '
    'corrections log.'))

# ════════════ CH 6 — RPG PROGRESSION LAYER ════════════
story.append(PageBreak())
story.append(h1('6. RPG Progression Layer — The Noea Inheritance'))
story.append(p(
    'The progression system is adapted directly from DragonMineZ (the base mod) and Dragon Block Noea (the '
    'add-on), because that ecosystem has already solved the hard problem of making a Dragon Ball RPG feel '
    'like Dragon Ball — race choice that matters, a six-stat sheet that feeds a single Battle Power number, '
    'Training Points as the universal progression currency, Power Release as the in-combat throttle, and a '
    'mastery curve that rewards using a form repeatedly.'))

story.append(h2('6.1 Races and Form Ladders'))
story.append(p(
    'Race choice fixes two things: the <b>passive skill</b> and the <b>core transformation ladder</b>. '
    'Visual customization (hair, eyes, aura color) is cosmetic and does not affect stats — exactly as in '
    'DragonMineZ.'))
story.append(mk([
    ['Race','Passive','Core transformation ladder','Notes'],
    ['Human','Recharge (faster Ki charge)','Buffed → Full Power → Potential Unleashed → Beyond the Limits',
     'Can also learn Kaioken, Ultra Instinct; Gamma hero chain via Dr. Gero'],
    ['Saiyan','Zenkai (small permanent boost + partial heal on near-death survival, cooldown)',
     'Oozaru → SSJ → Grade 2/3 → Mastered SSJ → SSJ2 → SSJ3',
     'God Ki (SSG → SSB → SSJ Rosé) gated behind Shenron wish; Ultra Instinct/Ego learnable'],
    ['Namekian','Meditation (faster passive Ki regen)','Giant → Full Power → Potential Unleashed → Orange (awakened)',
     'Golden/Orange Namekian chain via God Ki wish; classic Giant form'],
    ['Bio-Android','Absorption (heals % of damage dealt when low HP)','Semi-Perfect → Perfect → Super-Perfect → Ultra',
     'Temporary Cell Max via Shenron wish; can learn Ultra Ego'],
    ['Cold Demon (Frieza race)','Mutant (higher TP gain, boosted in HTC/Kai planet)',
     '2nd → 3rd → Final → Full Power → 5th Form','Golden (Final/5th); Black Frieza (manga DBS ch.88+)'],
    ['Majin','Regeneration (passive HP regen)','Evil → Kid → Super → Ultra','Reworked absorption ("margin" mechanic)'],
], [26*mm, 42*mm, 62*mm, 46*mm]))

story.append(h2('6.2 The Six-Stat Sheet → Battle Power'))
story.append(p(
    'DragonMineZ uses six core attributes, opened with the stats menu. The three offensive stats stack '
    'additively into total offensive output; the three defensive stats build survivability and resource '
    'pools. All of it feeds a single derived number — <b>Battle Power</b>, the modern equivalent of a classic '
    'Dragon Ball power level.'))
story.append(mk([
    ['Stat','Drives','Stacks into'],
    ['STR (Strength)','Melee (physical) damage','Offense'],
    ['SKP (Strike Power)','Ki-enhanced melee / technique "strike" damage','Offense'],
    ['PWR (Ki Power)','Ki blast / energy-wave damage','Offense'],
    ['RES (Resistance)','Defense/damage mitigation + max Stamina + max Poise','Survivability'],
    ['VIT (Vitality)','Max Health + Health/Stamina regen rate','Survivability'],
    ['ENE (Energy)','Max Ki (energy pool)','Survivability'],
], [38*mm, 80*mm, 44*mm]))
story.append(Spacer(1, 4))
story.append(p(
    '<b>Battle Power</b> = f(offense_stats) × powerRelease% × form.plMul × masteryBonus. This is the number '
    'that climbs into the billions (Noea\'s narrator cites 135 billion at the god-tier ceiling) and that '
    'feeds the combat-ratio formula from Chapter 5.2.'))

story.append(h2('6.3 Training Points — The Universal Currency'))
story.append(p(
    'TP is spent on stats, skills, Ki techniques, and transformation mastery. It is earned from parallel '
    'sources, all run through TP-boost multipliers:'))
story.append(b('<b>Kills</b> — TP scales with the target\'s Battle Power, so fighting stronger enemies is far '
               'more efficient than farming weak mobs (anti-grind design).'))
story.append(b('<b>Landed hits</b> — small TP per combat hit, independent of the kill (rewards aggressive play).'))
story.append(b('<b>Passive trickle</b> — small constant gain just for playing (rewards time-in-game).'))
story.append(b('<b>Travel / block-breaking / crafting</b> — each awards TP, scaled to distance/amount '
               '(rewards exploration).'))
story.append(b('<b>Training minigames</b> — five NPC Masters each teach one (Rhythm/Mr. Popo, Control/Krillin, '
               'Shadow Boxing/Gohan, Precision/Trunks, Gravity/Vegeta); rewards scale with current power up '
               'to a per-session cap — the single biggest deliberate TP source.'))
story.append(b('<b>Environment multipliers</b> — Gravity Devices, the Hyperbolic Time Chamber, and weighted '
               'training gear all multiply TP gain; Cold Demons get a passive ×1.25 TP bonus.'))

story.append(h2('6.4 Power Release — The In-Combat Throttle'))
story.append(p(
    'A character\'s raw stats are not fully "on" by default. Holding the release key charges Power Release '
    'from 0% up to a base cap of 50%; the Potential Unlock passive (taught by King Kai) raises that ceiling '
    'to 100%. Release is a <b>throttle on how much of the underlying stat sheet is expressed in combat at '
    'any given moment</b> — low release means weaker attacks and lower visible Battle Power even though the '
    'trained stats haven\'t changed. This is the mechanical bridge between the RPG grind and the fighting-game '
    'match: a player who has trained hard but doesn\'t charge release enters the fight at half-strength.'))
story.append(note(
    'Design implication for the merged game: Power Release is the player\'s "I\'m taking this fight '
    'seriously" button. It maps cleanly onto the Sparking! ZERO Ki-Charge mechanic — hold to fill, '
    'vulnerable while charging, fills the resource that gates your peak output.'))

story.append(h2('6.5 Mastery — The Form-Use Curve'))
story.append(p(
    'Each transformation has a TP unlock cost and, while active, an ongoing <b>Ki-drain upkeep</b>. Repeated '
    'use of a form builds Mastery, which both <i>reduces</i> that upkeep and <i>increases</i> the form\'s '
    'stat multiplier — a fully mastered form can reach up to ×1.5 stats while upkeep drops to ×0.75 of its '
    'base cost, and some forms even become free to hold once fully mastered. Related forms can share mastery '
    'progress.'))
story.append(p(
    'This is the single best idea in the Noea system and must be preserved wholesale. It does three jobs at '
    'once: (1) it gives the player a long-term reason to use forms they\'ve "outgrown" stat-wise; '
    '(2) it produces a satisfying mastery curve that mirrors the anime (Goku\'s first SSJ3 is exhausting; '
    'his later ones are stable); (3) it gives the form a second balance dial (upkeep + multiplier) instead '
    'of just one, making balance tuning far more expressive.'))

# ════════════ CH 7 — TRANSFORMATION SYSTEM ════════════
story.append(PageBreak())
story.append(h1('7. Transformation System — Merging Two Models'))
story.append(p(
    'Both source systems handle mid-battle transformation, but differently. The merged game takes '
    '<b>Sparking! ZERO\'s resource model</b> (transformation costs Skill Count, shifts the 5-point stat '
    'spread) for the in-fight layer, and <b>Noea\'s mastery model</b> (Ki-drain upkeep, mastery curve) for '
    'the progression layer. The two coexist because they operate at different time scales.'))

story.append(h2('7.1 The Two Models Side by Side'))
story.append(mk([
    ['Property','Sparking! ZERO model','Noea model','Merged game uses'],
    ['Cost to activate','Skill Count stock','TP unlock (one-time) + Ki-drain (ongoing)','Skill Count (fight) + TP unlock (meta)'],
    ['Effect','Shifts the 5-point stat spread; may change moveset','Stat multiplier + Ki-upkeep','Stat spread shift + multiplier + upkeep'],
    ['In-fight limitation','None — form persists until reverted','Ki drains; form drops when Ki hits 0','Ki-drain upkeep (Noea-style) — form drops at 0 Ki'],
    ['Long-term progression','None — flat per character','Mastery curve reduces upkeep + raises multiplier','Mastery curve (Noea-style)'],
    ['Climax interaction','Transformed → Sparking Mode → Ultimate Blast','Form-appropriate ultimate (Kamehameha, etc.)','Form-appropriate Ultimate Blast (canon-accurate)'],
], [34*mm, 40*mm, 44*mm, 46*mm]))

story.append(h2('7.2 Why This Merge Works'))
story.append(p(
    'Sparking! ZERO\'s "transformation = Skill Count spend" is a clean <b>in-fight</b> resource decision — '
    'do I transform now, or save the Skill Count for a Revenge Counter? But it has no long-term arc: a Goku '
    'who has used SSJ3 a thousand times pilots it identically to one using it for the first time. Noea\'s '
    'mastery model is a clean <b>meta</b> arc — your SSJ3 gets better the more you use it — but its in-fight '
    'transformation is just "press key, pay Ki."'))
story.append(p(
    'The merge: <b>in-fight, transformation costs Skill Count and immediately shifts your stat spread</b> '
    '(Sparking) <b>AND imposes a Ki-drain upkeep that drops you out of form if Ki hits zero</b> (Noea). '
    '<b>Meta-game, the mastery you\'ve earned on that form reduces the upkeep and raises the multiplier</b> '
    '(Noea). This gives the player both a per-fight resource puzzle and a long-term training arc, and '
    'neither breaks the combat loop from Chapter 4.'))

story.append(h2('7.3 The Canon-Accurate Form Multipliers'))
story.append(p(
    'Every form multiplier in the database must trace to its canon source. The Daizenshuu 7 + Super Exciting '
    'Guide chain is the backbone:'))
story.append(mk([
    ['Form','Multiplier (over base)','Source','Notes'],
    ['Base','×1','—','—'],
    ['Kaio-ken','×4 (×2 base, ×2 Kaio-ken)','[C] manga','Goku vs Vegeta; scales ×2/×3/×4/×10/×20'],
    ['Super Saiyan','×50','[D] Daizenshuu 7 p.44','SSJ Goku 150M = 3M base × 50'],
    ['SSJ2','×100','[D] Daizenshuu 7 + SEG','×2 over SSJ'],
    ['SSJ3','×400','[D] Daizenshuu 7 p.83','×4 over SSJ3 (= ×8 over SSJ? contested; SEG says ×4 over SSJ2)'],
    ['Oozaru','×10','[C] manga','Vegeta 18,000 → ~180,000 Oozaru'],
    ['Golden Oozaru','×500 (×50 Oozaru)','[S] scaling','SSJ4 precursor (GT scaling)'],
    ['Super Saiyan God','×? (god-tier)','[G] game tie-in','Below SSB; exact multiplier not canon-stated'],
    ['Ultra Instinct (Sign)','~10% dodge → ~70% at mastery','[S] add-on ecosystem','Mastery-scaled dodge chance'],
    ['Ultra Instinct (Mastered)','~40% → ~80% at mastery','[S] add-on ecosystem','Top of the dodge ladder'],
    ['Ultra Ego','rage/damage-scaled','[S] add-on ecosystem','Vegeta\'s god form'],
], [40*mm, 38*mm, 40*mm, 56*mm]))
story.append(Spacer(1, 4))
story.append(warn(
    'God-tier multipliers (SSG/SSB/UI/UE/Beast/Rosé) are NOT canon-stated as hard numbers — the manga and '
    'Daizenshuu stop at SSJ3 ×400. Any number above that is game-balanced or community-scaled and must be '
    'tagged [S] or [G], never presented as canon.'))

# ════════════ CH 8 — ARCHITECTURE BLUEPRINT ════════════
story.append(PageBreak())
story.append(h1('8. Architecture Blueprint — Engine and Core Systems'))
story.append(p(
    'This chapter specifies the engineering architecture. The research (Unity vs Unreal forum consensus, '
    'UE5 fighting-game tutorial ecosystem, the fact that Bandai Namco builds Sparking! ZERO on Unreal '
    'Engine 5) points to a clear engine choice and a clean system decomposition.'))

story.append(h2('8.1 Engine Choice — Unreal Engine 5'))
story.append(p(
    'For a Sparking! ZERO-style 3D arena fighter, <b>Unreal Engine 5 is the correct choice</b>. The reasons:'))
story.append(b('<b>AAA graphics out of the box</b> — Nanite + Lumen produce the cinematic anime-cel-shaded look '
               'Sparking! ZERO ships with; Unity can match it only with significant custom shader work.'))
story.append(b('<b>Built-in fighting-game references</b> — the UE5 "Fighting Game" tutorial series and the '
               'Universal Fighting Engine (UFE) for Unity both exist, but UE5\'s Chaos physics, Niagara VFX, '
               'and Animation Blueprint system are better suited to the destructible-terrain + transformation + '
               'aura-VFX load this game demands.'))
story.append(b('<b>Bandai uses it</b> — Sparking! ZERO itself is UE5, meaning the reference target runs on the '
               'same engine; shaders, animation pipelines, and netcode patterns can be directly informed by '
               'what Bandai shipped.'))
story.append(b('<b>Gameplay Abilities System (GAS)</b> — UE5\'s GAS is a data-driven ability framework that '
               'maps almost 1:1 onto the Noea skill tree (skills leveled with TP, with tags, costs, and '
               'cooldowns). It is the right tool for the RPG layer.'))
story.append(note(
    'Caveat: if team size is small and C++ is a blocker, Unity (with the Universal Fighting Engine asset and '
    'a custom RPG layer) is the viable second choice. The architecture below is engine-agnostic in shape; '
    'only the implementation library names change.'))

story.append(h2('8.2 Core System Decomposition'))
story.append(p(
    'The game decomposes into nine core systems. Each is independently testable and independently replaceable '
    '— a modder (or a future developer) can swap any one without touching the others.'))
story.append(mk([
    ['#','System','Responsibility','Key tech'],
    ['1','Character Controller','Movement (walk/dash/fly/ascend), camera, input mapping','UE5 CharacterMovementComponent'],
    ['2','Combat System','Move execution, hitboxes, damage, guard, counters','Custom + GAS for abilities'],
    ['3','Power-Level Engine','effectivePL calc, combat-ratio damage formula, source-tier flags','Pure data layer'],
    ['4','Progression System','Races, six-stat sheet, TP, Power Release, mastery','GAS + GameplayTags + SaveGame'],
    ['5','Transformation System','Form state, stat-spread shift, Ki-upkeep, mastery curve','Sub-system of Combat + Progression'],
    ['6','Animation System','State machine, blend trees, frame data, cancels','UE5 Animation Blueprint + AnimMontage'],
    ['7','Netcode','Rollback for PvP; relay for co-op; spectator','GGPO-style rollback layer'],
    ['8','World Systems','Space travel, planets, destructible terrain, raids','Voxel/marching-cubes + Niagara'],
    ['9','Content layer','Saga story, masters, tournaments, dialogue','Data tables + quest system'],
], [8*mm, 34*mm, 72*mm, 56*mm]))

story.append(h2('8.3 Data-Driven Character Definition'))
story.append(p(
    'Characters, moves, and forms are <b>data, not code</b>. A designer (or modder) adds Goku by editing a '
    'data table, not by writing a class. This is how Sparking! ZERO ships 164 characters and how Noea ships '
    'its full form ladders — and it is the only way the canon power-level data stays maintainable.'))
story.append(code(
    '// DataTable: /Game/DB/Characters/Goku.uasset\n'
    'BasePL=416  BasePLSource="MANGA_CH215"  Race=SAIYAN\n'
    'Forms=[ Base, Kaio-ken(x4), SSJ(x50), SSJ2(x100), SSJ3(x400) ]\n'
    'StatSpread={STR:7,SKP:8,RES:7,VIT:8,PWR:9,ENE:7}\n'
    'Passives=[ZENKAI]  Blast=Kamehameha  Ultimate=SuperKamehameha\n'
    '\n'
    '// DataTable: /Game/DB/Moves/Kamehameha.uasset\n'
    'Type=BLAST  BaseDamage=42  KiCost=300  ChargeTime=0.6s\n'
    'Startup=14  Active=6  Recovery=38  CancelWindows=[24,30]\n'
    'Hitbox=Beam(length=1200,width=80)  Knockback=900\n'
    'SourceTier="[C]"  Source="Manga ch.179 (Goku vs Piccolo)"'))

# ════════════ CH 9 — COMBAT SYSTEM IMPLEMENTATION ════════════
story.append(PageBreak())
story.append(h1('9. Combat System Implementation — Frame Data and State Machines'))
story.append(p(
    'The combat system is the heart of the game and the part most likely to be under-engineered. The research '
    'on fighting-game state machines (gamedev.net, mocaponline.com on 200+ state systems, the Universal '
    'Fighting Engine framework) converges on a small set of principles.'))

story.append(h2('9.1 Animation State Machine Design'))
story.append(p(
    'The single most important principle from the research: <b>"use as few states as possible"</b> '
    '(gamedev.net). A naive fighting game has 200+ animation states (every move × every cancel × every '
    'follow-up); the correct architecture layers rather than enumerates.'))
story.append(mk([
    ['Layer','What it holds','Tech'],
    ['Locomotion','Idle / walk / run / fly / dash — continuously blended by speed & direction','Blend tree (1D/2D)'],
    ['Action','Punch / ki-blast / smash / throw — discrete montages with frame data','AnimMontage + state'],
    ['Reaction','Hit-stun / guard / knockback / getup — driven by the combat system, not the player','State, auto-transitions'],
    ['Transformation','Form-change cinematic + stat-shift — overlays on top of action layer','Overlay slot'],
    ['Aura/VFX','Sparking! glow, Ki aura, charge particles — cosmetic, always-on overlay','Niagara + skeleton sockets'],
], [26*mm, 78*mm, 48*mm]))
story.append(Spacer(1, 4))
story.append(p(
    'Blend trees handle continuous locomotion; a discrete state machine handles discrete actions. The two '
    'do not need to know about each other. mocaponline\'s "patterns for 200+ states" research is explicit '
    'that layering (not a single flat FSM) is the only sustainable architecture.'))

story.append(h2('9.2 Frame Data — The Move Definition Schema'))
story.append(p(
    'Every move is defined by frame data, exactly as in traditional 2D fighters (and as UFE implements). '
    'The schema:'))
story.append(mk([
    ['Phase','Frames','What happens'],
    ['Startup','N frames','Move is animating but no hitbox active — interruptible here is a "gimp"'],
    ['Active','M frames','Hitbox live; connects if it overlaps a hurtbox'],
    ['Recovery','R frames','Hitbox gone; cannot act — the "whiff punish" window'],
    ['Cancel windows','specific frames','Frames where the move can be cancelled into a designated follow-up'],
    ['On hit / on block','+/- frame advantage','Frame advantage the attacker has after the move resolves'],
], [34*mm, 28*mm, 90*mm]))
story.append(Spacer(1, 4))
story.append(p(
    'At 60 FPS, Sparking! ZERO\'s timing windows translate roughly to: Smash Attack charge ≈ 30 frames '
    '(0.5s), Super Counter window ≈ 4–6 frames (the "hardest timing in the game" per the guide), '
    'Z-Counter window ≈ 8–10 frames. These windows are the skill-ceiling knobs — tightening them raises '
    'the ceiling, loosening them lowers it.'))

story.append(h2('9.3 Hitboxes and Hurtboxes'))
story.append(p(
    'Every animated move carries one or more <b>hitboxes</b> (the damage volume) and every character carries '
    '<b>hurtboxes</b> (the damageable volumes). The collision is sphere/capsule-based for performance (UE5 '
    'supports thousands of these per frame). The research consensus: <b>do not use mesh-accurate hitboxes</b> '
    '— they are visually impressive but make the game unreadable (a fist that whiffs by 2mm feels like a bug). '
    'Use generous capsules that match the visual intent, not the visual geometry.'))

story.append(h2('9.4 The Counter Implementation'))
story.append(p(
    'The five-counter ladder from Chapter 3.3 is implemented as a state-check on the defender\'s input '
    'during the attacker\'s Active frames:'))
story.append(code(
    'onDefenderInput(frame, incomingMove):\n'
    '  if frame in SuperCounterWindow:        # ±3 frames, no cost\n'
    '      return COUNTER_SUPER\n'
    '  if frame in ZCounterWindow and incomingMove.type == VANISHING_ASSAULT:\n'
    '      return COUNTER_Z                    # escalating damage duel\n'
    '  if frame in RevengeWindow and defender.skillCount >= 1:\n'
    '      return COUNTER_REVENGE              # costs 1 Skill Count\n'
    '  if frame in PerceptionWindow:\n'
    '      if incomingMove.type == RUSH:        return PERCEPTION_SONIC_SWAY  # free\n'
    '      elif incomingMove.type == BLAST and defender.skillCount >= 2:\n'
    '          return PERCEPTION_BLAST_COUNTER  # costs 2 Skill Count\n'
    '  if frame in EvasionWindow:              return EVASION  # timing only\n'
    '  return GUARD_OR_HIT'))

# ════════════ CH 10 — NETCODE ════════════
story.append(PageBreak())
story.append(h1('10. Netcode — Rollback for PvP, Relay for Co-op'))
story.append(p(
    'Netcode is the single most consequential engineering decision after engine choice. The research (Ars '
    'Technica\'s rollback explainer, infil.net\'s fighting-game glossary, the rollback-vs-delay debate on '
    'ResetEra / teamfortress.tv) is unambiguous: <b>PvP fighting games must use rollback netcode; delay-based '
    'netcode feels bad in practice and is the wrong choice for a read-heavy game</b>.'))

story.append(h2('10.1 Why Rollback, Not Delay'))
story.append(p(
    'In <b>delay-based</b> netcode, the local game waits for the opponent\'s input to arrive before '
    'advancing the simulation. This adds input latency proportional to ping — a 100ms connection makes a '
    '4-frame Super Counter window literally unreactable. In <b>rollback</b> netcode, the local game never '
    'waits: it advances the simulation using the local player\'s real input and the opponent\'s '
    '<i>predicted</i> input. When the opponent\'s real input arrives, if it differed from the prediction, '
    'the game rolls the state back to the divergence point and re-simulates forward with the correct inputs. '
    'The result (per Ars Technica): <i>"rollback\'s main strength is that it never waits for missing input '
    'from the opponent. Instead, rollback netcode continues to run the game."</i>'))

story.append(h2('10.2 The Determinism Requirement'))
story.append(p(
    'Rollback requires that the game simulation is <b>fully deterministic</b> — given the same inputs and '
    'the same starting state, the simulation must produce the identical ending state, bit-for-bit, on both '
    'machines. This is the hard part. It means:'))
story.append(b('<b>No floating-point non-determinism</b> — UE5 floats are not deterministic across CPUs; the '
               'combat simulation must use fixed-point math (e.g. 16.16 fixed) or a deterministic float library.'))
story.append(b('<b>No unlocked-thread race conditions</b> — the simulation runs on a single thread; rendering '
               'and VFX can be on other threads, but the gameplay state must be single-threaded.'))
story.append(b('<b>No system-time randomness in combat</b> — all RNG must come from a shared seeded PRNG '
               'synchronized across both clients.'))
story.append(b('<b>State save/restore</b> — the game must be able to snapshot its full state every frame and '
               'restore it in <2ms for the rollback. This is what makes the architecture demanding.'))

story.append(h2('10.3 Co-op and Spectator'))
story.append(p(
    'For co-op modes (saga co-op, raids — the Noea-style content), strict determinism is overkill: a small '
    'state desync is invisible when players aren\'t reading each other frame-by-frame. Use a <b>relay '
    'server with periodic state reconciliation</b> for co-op, reserving rollback for the 1v1 PvP ladder. '
    'Spectator mode is a third path: the server (or a designated client) runs the authoritative simulation '
    'and broadcasts a compressed state stream to spectators at 20Hz, with client-side interpolation.'))

# ════════════ CH 11 — DESTRUCTIBLE TERRAIN ════════════
story.append(PageBreak())
story.append(h1('11. Destructible Terrain & Planet Destruction'))
story.append(p(
    'The Noea mod\'s headline feature — and the one that most distinguishes a Dragon Ball game from a '
    'generic fighter — is destructible terrain and planet destruction. The research on voxel/marching-cubes '
    'terrain (Unity discussions, gamedev.net, benwindley.github.io, GitHub "Marching-Cubes-On-The-GPU") '
    'establishes the implementation path.'))

story.append(h2('11.1 Voxel Terrain with GPU Marching Cubes'))
story.append(p(
    'Destructible terrain requires a <b>voxel representation</b> (a 3D grid of density values) rendered to '
    'a mesh via the <b>marching-cubes algorithm</b>. The canonical approach, per the GitHub project and '
    'benwindley\'s write-up: run marching-cubes in a <b>compute shader</b> on the GPU, generating the mesh '
    'in a vertex buffer that updates only when voxels change. A Kamehamha carve becomes: write zeros to a '
    'voxel region → re-run marching cubes for affected chunks → the mesh updates.'))
story.append(mk([
    ['Property','Value','Note'],
    ['Voxel resolution','0.5m – 2m cubes','Fine enough for ki-blast carves; coarse enough to render'],
    ['Chunk size','16³ or 32³ voxels','One GPU dispatch per chunk per rebuild'],
    ['Rebuild scope','Only chunks that changed','Differential update — not the whole planet'],
    ['Storage','3D texture / StructuredBuffer','GPU-resident; CPU only for saves'],
    ['Planet size','500–5000 block radius (Noea spec)','Seamless spherical wrap (Noea v1.0)'],
], [34*mm, 50*mm, 68*mm]))

story.append(h2('11.2 The Planet-Integrity Model'))
story.append(p(
    'Noea\'s planet-destruction model (per the Noea guide) is the right design: a planet has an '
    '<b>integrity</b> value; if a sufficiently powerful attack\'s effectivePL exceeds the planet\'s integrity, '
    'the planet is destroyed outright (leaving collectible debris, killing anyone present, awarding an Evil '
    'alignment shift). This is a clean single-number threshold that maps onto the canon power-level system '
    'directly: a planet\'s integrity is a PL value, and the check is the same combat-ratio formula.'))

story.append(h2('11.3 Star Destruction Cinematic'))
story.append(p(
    'Noea v1.0 documents a full star-destruction sequence: the star brightens, shrinks, collapses, and '
    'explodes, visible from extreme range. This is a <b>Niagara VFX sequence + camera event</b>, not a '
    'simulation — there is no point simulating a star\'s physics in voxels. The right implementation: a '
    'scripted cinematic triggered by the attack landing, with the star\'s mesh/shader running a state '
    'machine (brighten → shrink → collapse → supernova), and a screen-shake + shockwave Niagara effect at '
    'the moment of collapse.'))

# ════════════ CH 12 — CONTENT & SAGA STRUCTURE ════════════
story.append(PageBreak())
story.append(h1('12. Content & Saga Structure'))
story.append(p(
    'The content layer is what makes the game a <i>Dragon Ball</i> game rather than a combat sandbox. The '
    'canon saga structure (DBZ ch. 1–325 + DBS) provides the story backbone; the Noea mod provides the '
    'meta-systems (masters, tournaments, raids) that give the player something to do between story beats.'))

story.append(h2('12.1 The Saga Backbone'))
story.append(mk([
    ['Saga','Manga chapters','Power-level range','Boss'],
    ['Raditz / Saiyan','Ch. 195–241','Farmer 5 → Vegeta 18,000','Vegeta (Oozaru ~180,000)'],
    ['Namek / Ginyu','Ch. 242–285','Cui 18K → Ginyu 120K','Captain Ginyu'],
    ['Frieza','Ch. 286–329','Frieza 1st 530K → 100% 120M','Frieza (100%)'],
    ['Trunks / Androids','Ch. 330–419','Androids 17/18/16','Imperfect / Semi-Perfect Cell'],
    ['Cell Games','Ch. 420–444','Perfect Cell 900M–1.2B → SSJ2 Gohan ~1.8B','Super Perfect Cell'],
    ['Babidi / Majin Buu','Ch. 445–486','Majin Vegeta → Fat Buu → Super Buu','Super Buu (base)'],
    ['Fusion / Kid Buu','Ch. 487–519','Buuutenks → Buuhan → Ultimate Gohan → Kid Buu','Kid Buu (≈ SSJ3 Goku)'],
    ['DBS: God tier','DBS manga','SSG → SSB → UI/UE → Beast','Beerus, Golden Frieza, Broly, Jiren'],
], [34*mm, 32*mm, 50*mm, 36*mm]))

story.append(h2('12.2 Masters and Training Minigames'))
story.append(p(
    'Five NPC Masters, each teaching one training minigame (Rhythm/Mr. Popo, Control/Krillin, Shadow '
    'Boxing/Gohan, Precision/Trunks, Gravity/Vegeta). Rewards scale with the player\'s current power up to '
    'a per-session cap — the single biggest deliberate TP source. This is a directly portable system; it '
    'solves the problem of "how does the player grind TP without it feeling like a grind" by making the '
    'minigames themselves the gameplay.'))

story.append(h2('12.3 Tournament Bracket Mode'))
story.append(p(
    'Noea v1.0\'s bracket mode (per the Noea guide) is the model: an Announcer NPC opens a bracket; survival-'
    'mode players create a single-elimination tournament, fighters auto-filled with NPCs or hand-picked. '
    'Difficulty scales <b>opposing NPC health, not raw damage</b>, to stop one-shot outcomes at matched power '
    '(Easy 2× HP, Normal 3×, Hard 5×, Extreme 10×, plus a "story power" mode). This is the right way to '
    'handle PvE difficulty in a power-level-scaled game — scaling damage would make every fight a coin '
    'flip, while scaling HP gives the player time to express skill.'))

story.append(h2('12.4 Custom Raid Bosses'))
story.append(p(
    'Noea v1.0\'s Legendary Core raids (Broly, Janemba, Beerus, Noa) are the model for endgame content. '
    'Key documented mechanics worth porting:'))
story.append(b('<b>Motion-capture-referenced attack animations</b> that adapt in real time to the attacking '
               'party\'s stats, rather than fixed damage numbers.'))
story.append(b('<b>Boss-specific mechanics</b> — area "ring" zones to vacate, super-dash gap-closer, '
               'teleport-behind heavy "flow state" attack.'))
story.append(b('<b>Multiple phases</b> (documented "phase two" power-up on Broly) — the boss transforms at '
               'HP thresholds, requiring the player to have enough forms banked to match.'))
story.append(b('<b>Out-of-raid healing disabled inside arenas</b> — forces reliance on teammates in party '
               'raids; shared teammate-health HUD.'))
story.append(b('<b>Accessibility options</b> to reduce raid VFX and disable screen shake for lower-end PCs '
               'and motion-sensitive players.'))

# ════════════ CH 13 — BUILD ROADMAP ════════════
story.append(PageBreak())
story.append(h1('13. Build Roadmap — Phased Plan'))
story.append(p(
    'A phased plan keeps scope under control and produces a playable artifact at every milestone. The '
    'research on how Noea itself was built (solo modder, public alpha → beta → v1.0 across roughly a year) '
    'and how fighting games are typically scoped (UE5 tutorial series, AAA production cycles) suggests four '
    'phases.'))

story.append(h2('13.1 Phase 1 — Combat Prototype (Weeks 1–8)'))
story.append(p(
    'One character (Goku), one arena (rocky field), the full core combat kit. Goal: prove the Sparking! '
    'ZERO feel is achievable before any RPG layer is added.'))
story.append(mk([
    ['Deliverable','Done when'],
    ['Character controller','Walk, dash, fly, ascend, descend all feel responsive; camera tracks 3D arena'],
    ['Core moveset','Rush Chain (4-hit), Smash Attack (charge+release), Ki Blast, Ki Charge, Throw'],
    ['Movement kit','Step, Dragon Dash, Z-Burst Dash, Quick Ascend/Descend'],
    ['Counter ladder','All 5 counters (Super Perception, Z, Revenge, Super, Evasion) with correct windows'],
    ['Sparking! Mode','Gauge fill, activation, Ultimate Blast, Ki-cost-free actions'],
    ['Two-character local PvP','Goku vs Goku, first-to-3 matches, no online'],
], [50*mm, 96*mm]))

story.append(h2('13.2 Phase 2 — Vertical Slice (Weeks 9–20)'))
story.append(p(
    'Three characters (Goku, Vegeta, Piccolo), one full saga (Saiyan saga: Raditz → Nappa → Vegeta), the '
    'RPG layer wired in. Goal: prove the merge works — that the RPG grind doesn\'t break the combat feel.'))
story.append(mk([
    ['Deliverable','Done when'],
    ['RPG layer','Races (Saiyan + 1), six-stat sheet, TP, Power Release, mastery curve wired'],
    ['Transformation system','SSJ unlock + mastery; Ki-upkeep; mid-fight transform via Skill Count'],
    ['Canon PL data','Saiyan saga characters in the DB with source-tier tags; combat-ratio damage live'],
    ['Saga content','Raditz → Nappa → Vegeta story missions; Mr. Popo training minigame'],
    ['Destructible terrain','Voxel arena; Kamehameha carves terrain; planet-integrity check'],
    ['Online PvP (rollback)','Goku vs Goku vs Vegeta vs Piccolo, 1v1, rollback netcode'],
], [50*mm, 96*mm]))

story.append(h2('13.3 Phase 3 — Beta (Weeks 21–44)'))
story.append(p(
    'Full DBZ roster (Saiyan → Buu saga), all six races, all sagas, full transformation ladders, tournament '
    'mode, first raid boss. Goal: content-complete enough to ship early access.'))

story.append(h2('13.4 Phase 4 — v1.0 (Weeks 45–60)'))
story.append(p(
    'DBS god-tier content (UI, UE, Beast, Rosé), space travel, full planet system, all raid bosses, '
    'tournament bracket mode, accessibility polish. Goal: the full merged vision.'))

story.append(h2('13.5 Effort and Team-Size Estimate'))
story.append(mk([
    ['Phase','Calendar','Team size','Note'],
    ['1. Prototype','~2 months','1–2 (programmer + animator)','Solo-moddable scope'],
    ['2. Vertical slice','~3 months','3–5 (+ designer, FX artist, writer)','First hire: combat animator'],
    ['3. Beta','~6 months','6–10 (+ content designers, netcode specialist)','Rollback specialist is critical hire'],
    ['4. v1.0','~4 months','8–12 (+ DBS content, space/planet systems)','Polish + accessibility pass'],
], [26*mm, 26*mm, 50*mm, 64*mm]))
story.append(Spacer(1, 4))
story.append(note(
    'These are rough order-of-magnitude estimates informed by Noea\'s actual solo-dev timeline (one year '
    'across v0.3 → v1.0) and typical indie fighting-game scope (Project L, TFH, etc.). A solo developer '
    'can reach Phase 1; reaching Phase 3+ realistically requires a small team.'))

# ════════════ CH 14 — RISKS & LEGAL ════════════
story.append(PageBreak())
story.append(h1('14. Risks, Legal, and Caveats'))

story.append(h2('14.1 Trademark and Legal'))
story.append(warn(
    'Dragon Ball, Dragon Ball Z, Dragon Ball Super, Dragon Ball: Sparking! ZERO, and all character names '
    '(Goku, Vegeta, etc.) are trademarks of Bird Studio / Shueisha / Toei Animation / Bandai Namco. A '
    'commercial game using these names and likenesses requires a license from Bandai Namco (the interactive '
    'rights holder). The Dragon Block Noea / DragonMineZ mods operate in a legally gray fan-work space and '
    'are unaffiliated with the rights holders. This document is a research/design blueprint, not legal '
    'clearance to ship a Dragon Ball game commercially.'))

story.append(h2('14.2 The "Original IP" Alternative'))
story.append(p(
    'The cleanest legal path is to build the game with an <b>original IP inspired by Dragon Ball</b> — '
    'original character names, original planet names, but the same combat feel, the same RPG progression, '
    'and the same power-level architecture. The dragon-power.js prototype already in this workspace takes '
    'exactly this approach ("Dragon Ball-inspired" with original assets). The canon power-level research '
    'transfers directly (it is a numerical-design pattern, not trademarked); the Sparking! ZERO combat '
    'mechanics transfer (game mechanics are not copyrightable); only the names and likenesses need to be '
    'original.'))

story.append(h2('14.3 Scope-Creep Warnings'))
story.append(b('<b>Do not build 164 characters</b> before the core loop feels right. Sparking! ZERO shipped '
               '164 because the core kit was shared; building the roster before the kit is the classic '
               'fighting-game scope-creep trap.'))
story.append(b('<b>Do not build the space/planet system before combat is fun</b>. Noea added space in v0.75, '
               'well after the combat and progression were proven. Reversing this order produces a pretty '
               'sandbox with nothing to do in it.'))
story.append(b('<b>Do not skip rollback</b>. Shipping a PvP fighting game on delay-based netcode in 2026 is '
               'a launch-killer — the fighting-game community will reject it within a week of release, '
               'regardless of how good the combat is.'))

story.append(h2('14.4 The "Sparking Clone vs Original" Line'))
story.append(p(
    'The merged game should be a <b>Sparking! ZERO-style</b> arena fighter, not a Sparking! ZERO <i>clone</i>. '
    'The difference: take the design principles (movement as backbone, Ki as universal economy, layered '
    'counters, Sparking!-as-climax, shared core kit) and the RPG inheritance (races, six-stat sheet, TP, '
    'mastery), but build original movesets, original transformation cinematics, original characters. The '
    'goal is a game that <i>plays like</i> the best of both sources without <i>being</i> either of them.'))

# ════════════ CH 15 — BIBLIOGRAPHY ════════════
story.append(PageBreak())
story.append(h1('15. Bibliography — Research Sources'))
story.append(p('This blueprint synthesizes four research inputs and supplementary web sources.'))

story.append(h2('15.1 Primary Source PDFs (supplied / built in this workspace)'))
story.append(b('<b>Dragon Ball: Sparking! ZERO — Combat &amp; Controls Guide</b> (7 pp) — compiled from '
               'Bandai Namco Europe\'s beginner guide, the combo/features page, the NEO DLC announcement, '
               'and TheGamer / NoobFeed / GamingBolt / Game8 breakdowns. The source for all combat mechanics.'))
story.append(b('<b>Dragon Block Noea — Deep Research Guide</b> (9 pp) — documents DragonMineZ (Forge 1.20.1 '
               'base mod, 538K+ CurseForge downloads) and the Dragon Block Noea add-on (BuD-eR / ButterJaffa). '
               'The source for all RPG progression systems.'))
story.append(b('<b>Dragon Ball Z — Fact-Checked Power Levels</b> (12 pp) — every PL cross-referenced against '
               'Kanzenshuu, Daizenshuu 7, V-Jump, manga chapter readings, and the Kakarot game. The source '
               'for all canon power-level data and the source-tier tagging system.'))
story.append(b('<b>Dragon Block C — Deep Research Guide</b> (14 pp) — the companion research on the older '
               'JinGames Java 1.7.10 mod; its canon tables remain valid, its mod-identification was '
               'superseded by the Noea guide.'))

story.append(h2('15.2 Canon Power-Level Sources (cited in the fact-checked guide)'))
story.append(b('<b>Kanzenshuu</b> — the Dragon Ball fan-research community of record; manga compilation '
               'readings and the "Over 8,000" (not 9,000) correction.'))
story.append(b('<b>Daizenshuu 7</b> — Shueisha\'s official databook; the source for SSJ ×50, SSJ2 ×100, '
               'SSJ3 ×400, and Goku SSJ 150M / Frieza 100% 120M.'))
story.append(b('<b>V-Jump magazine</b> — the source for the SSJ3 Goku = 24 billion promo value.'))
story.append(b('<b>Dragon Ball manga</b> (ch. 195–519) — on-panel scouter readings: Raditz 1,500, Vegeta '
               '18,000, Frieza 1st 530,000, Ginyu 120,000, Gohan enraged 1,307.'))

story.append(h2('15.3 Game-Design and Engineering Sources (web research)'))
story.append(b('<b>Ars Technica</b> — "Explaining how fighting games use delay-based and rollback netcode" '
               '(2019). The source for the rollback vs delay analysis in Chapter 10.'))
story.append(b('<b>infil.net — The Fighting Game Glossary</b> — the canonical reference for rollback, '
               'delay-based, and fighting-game terminology.'))
story.append(b('<b>CNET / Rolling Stone / Hardcore Gamer</b> — Sparking! ZERO reviews establishing the '
               '"simple to learn, hard to master" and "theatrical look" consensus.'))
story.append(b('<b>GameFAQs / Steam community</b> — player-base analysis ("Ki management is the name of the '
               'game", "every character is a setup archetype") that informs the design-philosophy chapter.'))
story.append(b('<b>gamedev.net / mocaponline.com / gamedev.stackexchange.com</b> — fighting-game state '
               'machine design, blend-tree vs FSM, and patterns for 200+ state systems.'))
story.append(b('<b>Universal Fighting Engine (UFE) — Unity forum discussions</b> — frame-data and '
               'move-definition schema reference.'))
story.append(b('<b>GitHub: Marching-Cubes-On-The-GPU / benwindley.github.io</b> — GPU compute-shader '
               'marching-cubes for destructible voxel terrain.'))
story.append(b('<b>DragonMineZ CurseForge / Modrinth / GitHub</b> — the base mod\'s own documentation '
               '(GeckoLib 4.8.3+, TerraBlender, six-stat sheet, TP, mastery).'))
story.append(b('<b>Bandai Namco Europe — Sparking! ZERO Beginner\'s Guide, Combos and Features, NEO DLC '
               'announcement</b> — the official source for all combat mechanics in Chapter 3 and 4.'))
story.append(b('<b>Bandai Namco — Dragon Ball Xenoverse 3 Battle System Guide</b> — reference for the '
               'transformation-as-resource design and the 4-Super/1-Ultimate/1-Assist loadout structure.'))

story.append(Spacer(1, 10))
story.append(Paragraph(
    '— End of Blueprint —', ParagraphStyle('End', parent=BODY_S, alignment=TA_CENTER,
    fontName=BODYI, textColor=TEXT_MUTED)))

# ════════════ BUILD ════════════
doc = TocDocTemplate(OUTPUT, pagesize=A4,
    leftMargin=14*mm, rightMargin=14*mm, topMargin=18*mm, bottomMargin=16*mm,
    title='Dragon Ball Game — Design & Engineering Blueprint',
    author='Z.ai', creator='Z.ai')
doc.multiBuild(story, onFirstPage=cover_bg, onLaterPages=page_bg)
print(f'Built: {OUTPUT}')
sz = os.path.getsize(OUTPUT)
print(f'Size: {sz:,} bytes ({sz/1024:.1f} KB)')
