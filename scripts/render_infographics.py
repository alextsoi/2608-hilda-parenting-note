#!/usr/bin/env python3
"""Render zh-HK infographic cards from FHS note content. Not medical advice."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
FONT_MED = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"

BG = (247, 244, 238)
HEADER = (11, 94, 96)
TEXT = (28, 42, 58)
MUTED = (96, 104, 112)
WHITE = (255, 255, 255)
LINE = (220, 214, 204)
WARN = (154, 48, 42)
OK = (36, 110, 86)
CHIP = (232, 244, 242)
FOOT = "衞生署家庭健康服務網頁文字摘要　·　唔構成醫療建議"


def font(size: int, medium: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_MED if medium else FONT_LIGHT
    return ImageFont.truetype(path, size, index=0)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines or [""]


def new_canvas(h: int, w: int = 1080) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (w, h), BG)
    return im, ImageDraw.Draw(im)


def header_bar(draw, w: int, title: str, subtitle: str) -> int:
    draw.rectangle((0, 0, w, 168), fill=HEADER)
    draw.rectangle((0, 168, w, 176), fill=(232, 168, 88))
    tf, sf = font(42), font(22, False)
    draw.text((48, 36), title, font=tf, fill=WHITE)
    draw.text((48, 104), subtitle, font=sf, fill=(210, 232, 228))
    return 200


def footer(draw, w: int, h: int) -> None:
    draw.rectangle((0, h - 64, w, h), fill=HEADER)
    draw.text((48, h - 44), FOOT, font=font(18, False), fill=(210, 232, 228))


def draw_items(draw, items: list[str], y: int, w: int, max_w: int = 960) -> int:
    fnt = font(28, False)
    numf = font(26)
    for i, item in enumerate(items, 1):
        draw.ellipse((48, y + 6, 84, y + 42), fill=HEADER)
        tw = draw.textlength(str(i), font=numf)
        draw.text((66 - tw / 2, y + 8), str(i), font=numf, fill=WHITE)
        lines = wrap(draw, item, fnt, max_w - 60)
        for j, line in enumerate(lines):
            draw.text((104, y + j * 38), line, font=fnt, fill=TEXT)
        y += max(52, 16 + 38 * len(lines))
    return y


def save_card(rel: str, title: str, subtitle: str, items: list[str], note: str | None = None) -> str:
    w = 1080
    # estimate height
    dummy = Image.new("RGB", (w, 10), BG)
    d = ImageDraw.Draw(dummy)
    y = 200
    fnt = font(28, False)
    for item in items:
        lines = wrap(d, item, fnt, 900)
        y += max(52, 16 + 38 * len(lines))
    if note:
        y += 120
    h = max(720, y + 100)
    im, draw = new_canvas(h, w)
    header_bar(draw, w, title, subtitle)
    y = draw_items(draw, items, 208, w)
    if note:
        draw.rounded_rectangle((40, y + 8, w - 40, y + 88), 16, fill=(255, 236, 230))
        nf = font(24, False)
        for j, line in enumerate(wrap(draw, note, nf, 960)):
            draw.text((64, y + 24 + j * 32), line, font=nf, fill=WARN)
    footer(draw, w, h)
    dest = IMG / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG", optimize=True)
    return str(dest.relative_to(ROOT))


def save_split(
    rel: str,
    title: str,
    subtitle: str,
    left_h: str,
    left: list[str],
    right_h: str,
    right: list[str],
) -> str:
    w, h = 1080, 1280
    im, draw = new_canvas(h, w)
    header_bar(draw, w, title, subtitle)
    mid, top, box_h = w // 2, 208, 980
    draw.rounded_rectangle((36, top, mid - 16, box_h), 20, fill=WHITE, outline=LINE, width=2)
    draw.rounded_rectangle((mid + 16, top, w - 36, box_h), 20, fill=WHITE, outline=LINE, width=2)
    draw.rounded_rectangle((52, top + 20, mid - 32, top + 72), 12, fill=OK)
    draw.rounded_rectangle((mid + 32, top + 20, w - 52, top + 72), 12, fill=WARN)
    hf = font(26)
    draw.text((72, top + 32), left_h, font=hf, fill=WHITE)
    draw.text((mid + 52, top + 32), right_h, font=hf, fill=WHITE)
    bf = font(24, False)

    def col(items, x, yw):
        yy = top + 96
        for t in items:
            for line in wrap(draw, "• " + t, bf, yw):
                draw.text((x, yy), line, font=bf, fill=TEXT)
                yy += 36
            yy += 10

    col(left, 56, mid - 90)
    col(right, mid + 36, mid - 90)
    footer(draw, w, h)
    dest = IMG / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "PNG", optimize=True)
    return str(dest.relative_to(ROOT))


# path -> list of (rel_image, title, subtitle, items, note)
CARDS: list[tuple[str, str, str, str, list[str], str | None]] = [
    (
        "00-0-to-1-month/jaundice.md",
        "00-0-to-1-month/jaundice-timeline.png",
        "新生嬰兒黃疸",
        "初生數周　·　衞生署摘要",
        [
            "好常見：膽紅素積聚，皮膚同眼白發黃",
            "多數第 2–3 天出現，約兩至三星期減退",
            "食得夠就繼續母乳，無須為母乳性黃疸轉配方奶",
            "唔好靠曬太陽治療",
            "出院後盡快去母嬰健康院或醫生跟進",
        ],
        "大便轉淡、超過兩至三星期未退、退咗再黃：要覆診",
    ),
    (
        "00-0-to-1-month/jaundice.md",
        "00-0-to-1-month/jaundice-risk.png",
        "黃疸：較高風險",
        "要特別跟進嘅情況",
        [
            "早產、餵哺唔理想、脫水",
            "G6PD 缺乏症（唔好接觸臭丸、蠶豆、指定藥物）",
            "同媽媽血型不吻合、感染",
            "滿月後仍黃：抽血排除病理性成因（包括罕有膽管閉塞）",
            "膽紅素極高或急升可能要照燈，跟醫生指示",
        ],
        None,
    ),
    (
        "00-0-to-1-month/breastfeeding.md",
        "00-0-to-1-month/breastfeeding-keys.png",
        "母乳餵哺三件事",
        "初生至約 6 個月全母乳",
        [
            "母嬰同房：BB 瞓喺牀邊，方便回應日夜需要",
            "回應式餵哺：見到早期肚餓信號就餵，唔使等到大喊",
            "家人支持：有支持嘅媽媽較易持續餵哺",
            "首天至少 3–4 次；第 2 天起一般每天最少約 8 次，唔設上限",
            "少食多餐係初生正常，唔等於奶量不足",
        ],
        "唔好隨便加水或加奶粉",
    ),
    (
        "00-0-to-1-month/breastfeeding.md",
        "00-0-to-1-month/breastfeeding-enough.png",
        "點知食得夠",
        "睇濕片、大便同體重",
        [
            "第 1 天：濕片 1–2、胎糞至少 1–2 次",
            "第 2 天：濕片 1–2、大便至少 2 次",
            "第 3–4 天：濕片 3–4 片略重，大便轉黃",
            "第 5 天起：濕片 5–6 片相當重，小便淡黃",
            "約 1–2 周回復出生體重，之後穩步增長",
        ],
        None,
    ),
    (
        "00-0-to-1-month/bottle-feeding.md",
        "00-0-to-1-month/bottle-feeding.png",
        "奶瓶餵哺安全",
        "沖調配方奶　·　衞生署指引",
        [
            "用具要徹底清潔同消毒",
            "最好即沖即餵，餵前試温",
            "唔好用微波爐加熱",
            "唔好墊高奶瓶畀 BB 獨食",
            "水溫同沖調比例跟官方同產品說明",
        ],
        "沖調不當有健康風險；決定用配方奶前先問醫護",
    ),
    (
        "00-0-to-1-month/health-warning-signs.md",
        "00-0-to-1-month/warning-signs.png",
        "立即睇醫生",
        "出生至三個月　·　健康須知",
        [
            "突然呆滯、昏睡、到食奶時間都唔醒",
            "發燒：腋探 >37.3°C 或耳探 >38°C",
            "呼吸急速／吃力、鼻翼搗動、唇或面持續發藍",
            "嘔吐綠色或帶血、抽搐、呼吸停頓 15 秒或以上",
            "不肯進食或胃口驟降、持續腹脹堅實",
        ],
        "周末假期都可先去私家醫生或急症室",
    ),
    (
        "00-0-to-1-month/safety.md",
        "00-0-to-1-month/sleep-safety.png",
        "安全睡眠",
        "給寶寶一個安全環境",
        [
            "仰睡、獨立嬰兒牀、面部同手外露",
            "牀上無雜物、唔瞓鬆軟物件",
            "無煙、空氣流通、着輕巧衫",
            "牀欄柱距少於 6 厘米；墊褥緊貼欄邊",
            "一般揹帶由三個月或以上先適用",
        ],
        "唔好同瞓梳化；同牀要用睡籃分隔",
    ),
    (
        "00-0-to-1-month/umbilical-cord.md",
        "00-0-to-1-month/umbilical-cord.png",
        "臍帶護理",
        "保持乾爽清潔",
        [
            "用清水清潔，抹乾，保持空氣流通",
            "唔好搽粉、酒精或其他非醫護建議嘅藥",
            "尿片摺低，避免摩擦同潮濕",
            "多數一兩周內脫落",
            "紅腫滲液惡臭或發燒：盡快求醫",
        ],
        None,
    ),
    (
        "00-0-to-1-month/development.md",
        "00-0-to-1-month/development.png",
        "滿月發展重點",
        "新生至一個月",
        [
            "多數時間瞓，清醒時對聲音同面孔有反應",
            "認得媽媽聲音，喜歡肌膚接觸",
            "啼哭係主要表達；回應唔會寵壞",
            "聽力視力有警示要跟進（見發展筆記）",
            "每個寶寶節奏唔同，持續停滯先擔心",
        ],
        None,
    ),
    (
        "00-0-to-1-month/parenting.md",
        "00-0-to-1-month/parenting.png",
        "初生社交情緒",
        "連繫．情感",
        [
            "社交情緒出世已開始",
            "清醒時說話、唱歌、輕撫",
            "哭時先處理肚餓換片，再用短句安慰",
            "接納正負面情緒，陪伴過渡",
            "媽媽情緒會影響寶寶，有困擾要求助",
        ],
        None,
    ),
    (
        "00-0-to-1-month/screening.md",
        "00-0-to-1-month/screening.png",
        "初生篩查",
        "出院前後常見檢查",
        [
            "身體檢查唔保證發現所有問題",
            "聽力篩查、先天性代謝病等按醫院安排",
            "G6PD 臍帶血：陽性通常出院前通知",
            "出院後盡快去母嬰健康院跟進黃疸同體重",
            "有疑問帶齊出院摘要去健康院",
        ],
        None,
    ),
    (
        "00-0-to-1-month/vaccines.md",
        "00-0-to-1-month/vaccines.png",
        "初生疫苗",
        "出生後盡快",
        [
            "卡介苗（預防結核）",
            "乙型肝炎疫苗第一次",
            "之後針期見完整疫苗表",
            "離開香港要繼續當地免疫接種",
            "發燒或嚴重不適應暫停並問醫生",
        ],
        None,
    ),
    (
        "00-0-to-1-month/oral.md",
        "00-0-to-1-month/oral.png",
        "初生口腔",
        "未出牙都要護理",
        [
            "清潔口腔黏膜，養成習慣",
            "唔好含住奶瓶瞓（出牙後易蛀）",
            "衞生署「牙齒俱樂部」有六歲以下系列",
            "出牙後再用紗布或指套刷清潔",
            "詳情見官方口腔健康目錄",
        ],
        None,
    ),
    (
        "00-0-to-1-month/mchc-first-visit.md",
        "00-0-to-1-month/mchc-first-visit.png",
        "首次母嬰健康院",
        "帶備文件同期望",
        [
            "帶身份證、住址證明、出院紙、針卡",
            "可預先填兒童健康服務登記表",
            "跟進體重、黃疸、餵哺同媽媽情緒",
            "各院時間地址見資源頁",
            "熱線 2112 9900",
        ],
        None,
    ),
    (
        "mother/postnatal-exercise.md",
        "mother/postnatal-exercise.png",
        "產後運動原則",
        "衞生署及醫管局物理治療部",
        [
            "順產一般 24 小時後可開始；手術產先問醫生",
            "先練深層腹橫肌同盆骨底，夠穩先練外層",
            "呼吸暢順、動作慢、循序漸進",
            "腹肌未復元：唔好仰臥起坐或仰臥抬腿",
            "搬嘢曲膝，抱 BB 都保持收腹同盆骨底",
        ],
        "抬頭時腹部隆起 = 未適宜加難度",
    ),
    (
        "mother/postnatal-mental-health.md",
        "mother/postnatal-mental-health.png",
        "產後三種情緒",
        "持續兩星期或影響生活就要求助",
        [
            "情緒低落：約 40–80%，產後 3–5 天，多數數日可緩",
            "抑鬱：香港約每十人一個，可喺一年內出現",
            "精神病：約 0.1–0.5%，多喺兩星期內，屬急症",
            "幻聽、被害想法、傷害自己或嬰兒念頭：立即急症室",
            "醫管局精神健康專線 2466 7350（24 小時）",
        ],
        None,
    ),
    (
        "mother/partner-support.md",
        "mother/partner-support.png",
        "點照顧她的心",
        "給伴侶、長輩、朋友",
        [
            "主動分擔家務同湊仔，等媽媽有得休息",
            "耐心聽，唔好一句「唔好諗咁多」",
            "用說話肯定付出，期望要實際",
            "長輩用開放態度，唔使一定跟舊做法",
            "照顧者都要照顧自己，唔係超人",
        ],
        None,
    ),
    (
        "mother/postnatal-care.md",
        "mother/postnatal-care.png",
        "產褥期復元",
        "大約六周　·　產後護理及家庭計劃",
        [
            "惡露：鮮紅約一周 → 淡紅約兩周 → 逐漸乾淨",
            "六星期後做一次檢查確認復元",
            "未有經期都可以懷孕，恢復性生活就要避孕",
            "惡露增多、惡臭、發燒、下腹痛：睇醫生",
            "脫髮可持續數月，多數六個月內改善",
        ],
        None,
    ),
    (
        "mother/breastfeeding-nutrition.md",
        "mother/breastfeeding-nutrition.png",
        "哺乳媽媽營養",
        "碘、均衡、唔飲酒",
        [
            "每天含至少 150 微克碘嘅孕婦綜合補充劑",
            "用加碘鹽，全日鹽少於 5 克；海帶每星期最多一次",
            "均衡五大類，每天有肉魚蛋奶",
            "唔好飲酒；限制咖啡因",
            "中藥補品只跟註冊中醫",
        ],
        None,
    ),
    (
        "mother/breastfeeding.md",
        "mother/breastfeeding-start.png",
        "母乳：媽媽角度",
        "黃金首小時同上奶",
        [
            "產前學知識、參加健康院或醫院講座",
            "出生後盡快肌膚相親，等 BB 食初乳",
            "上奶前就學埋身，主動問姿勢",
            "第 2–3 天谷奶正常；第 4 天未上奶要搵人",
            "唔好過度擠奶，唔好大力按塞奶硬塊",
        ],
        "乳腺炎：紅腫熱痛或體温超過 38.5°C 盡快求診",
    ),
    (
        "mother/lifestyle.md",
        "mother/lifestyle.png",
        "產後生活模式",
        "無論餵唔餵母乳",
        [
            "每天穀物、蔬菜、水果、肉魚蛋、奶類",
            "肉去皮去肥；每天最多 5–6 茶匙油",
            "少食餅乾蛋糕煎炸",
            "推車去公園散步；家人幫手先上運動班",
            "減重靠均衡同郁動，唔好過度節食",
        ],
        None,
    ),
    (
        "mother/postnatal-needs.md",
        "mother/postnatal-needs.png",
        "產後母親的需要",
        "全家都要睇住媽媽",
        [
            "最需要：充足休息",
            "實際幫忙：家務、湊仔、陪月或家務助理",
            "心理支持：關懷、體諒、聆聽",
            "約一半婦女產後 3–5 天情緒低落",
            "嚴重或持續就要搵醫護",
        ],
        None,
    ),
    (
        "mother/services.md",
        "mother/services.png",
        "產後健康院服務",
        "檢查、避孕、子宮頸普查",
        [
            "約六星期產後檢查：身體、情緒、餵哺",
            "家庭計劃預約 3796 0879",
            "子宮頸普查 25–64 歲曾有性經驗：3166 6631",
            "所有健康院開放時間有事後避孕",
            "部分項目另收費",
        ],
        None,
    ),
    (
        "01-1-to-12-months/feeding.md",
        "01-1-to-12-months/feeding.png",
        "一至十二個月：奶類",
        "約 6 個月前以奶為主",
        [
            "首 6 個月全母乳或嬰兒配方",
            "約 6 個月開始加固體，繼續餵奶",
            "按需要餵，跟體重同濕片",
            "配方沖調見奶瓶指引",
            "唔好用普通牛奶代替嬰兒配方（一歲前）",
        ],
        None,
    ),
    (
        "01-1-to-12-months/feeding-solids.md",
        "01-1-to-12-months/feeding-solids.png",
        "約 6 個月加固體",
        "6 至 24 個月飲食起步篇",
        [
            "滿六個月鐵質需要大增，單靠母乳唔夠",
            "未足 4 個月加固體較易敏感",
            "由少量、一種新食物開始，唔好勉強",
            "可喺餵奶前約 30 分鐘試一兩茶匙",
            "選鐵質豐富、易做成蓉嘅食物",
        ],
        None,
    ),
    (
        "01-1-to-12-months/parenting.md",
        "01-1-to-12-months/parenting.png",
        "一至十二個月親職",
        "信號、睡眠、連繫",
        [
            "繼續回應式照顧，解讀肚餓同疲倦信號",
            "建立簡單日常，但保持彈性",
            "肌膚接觸同面對面玩耍",
            "家長都要休息，生活模式影響情緒",
            "詳見連繫．情感單張",
        ],
        None,
    ),
    (
        "01-1-to-12-months/development.md",
        "01-1-to-12-months/development.png",
        "一至十二個月發展",
        "大動作、精細、語言",
        [
            "跟健康院發展監察，唔好同第二個比進度",
            "提供安全地板時間同抓握玩具",
            "多講、多指、等多回應",
            "持續唔達里程或倒退：盡快評估",
            "聽力視力問題會影響發展",
        ],
        None,
    ),
    (
        "01-1-to-12-months/safety.md",
        "01-1-to-12-months/safety.png",
        "一至十二個月安全",
        "學翻、坐、爬之後",
        [
            "睡眠仍然仰睡、嬰兒牀、無雜物",
            "一般揹帶三個月或以上",
            "手推車扣帶、鎖轆",
            "唔好墊高奶瓶獨食",
            "藥物、清潔劑、細件要鎖高",
        ],
        None,
    ),
    (
        "01-1-to-12-months/vaccines.md",
        "01-1-to-12-months/vaccines.png",
        "一至十二個月針",
        "跟衞生署時間表",
        [
            "2、4、6 個月有多種聯合疫苗",
            "錯過要盡快補，唔好自行跳過",
            "完整月份見資源頁疫苗表",
            "打針當日輕微發燒常見，持續高燒要問醫生",
            "帶針卡去每一個健康院",
        ],
        None,
    ),
    (
        "01-1-to-12-months/hearing-vision.md",
        "01-1-to-12-months/hearing-vision.png",
        "聽力同視力",
        "一至十二個月警示",
        [
            "對突然巨響無反應、唔轉向聲音：查聽力",
            "對視無交流、唔追視：查視力",
            "斜視、瞳孔發白：盡快睇醫生",
            "健康院會跟階段做監察",
            "有疑問唔好等「大個就得」",
        ],
        None,
    ),
    (
        "01-1-to-12-months/oral.md",
        "01-1-to-12-months/oral.png",
        "出牙期口腔",
        "一至十二個月",
        [
            "出牙後用濕紗布或幼毛牙刷清潔",
            "唔好含奶瓶瞓",
            "牙齒初生已要護理，唔使等齊牙",
            "小冊子（三）有幼兒口腔護理",
            "流血腫痛持續要問牙醫或健康院",
        ],
        None,
    ),
    (
        "02-1-to-3-years/safety.md",
        "02-1-to-3-years/safety.png",
        "1–3 歲家居安全",
        "根據《你的寶寶安全嗎？》",
        [
            "唔好獨留在家或只交年長哥哥姐姐睇",
            "窗花上鎖、窗簾繩收高、插座加蓋",
            "廚房設圍欄；利器、藥、清潔劑鎖高",
            "家具尖角護角；唔好層層疊畀人爬",
            "沐浴先冷後熱，片刻都唔好獨留浴盆",
        ],
        "活動能力急升：跌墮、哽噎、誤食風險高",
    ),
    (
        "02-1-to-3-years/parenting.md",
        "02-1-to-3-years/parenting.png",
        "一歲至三歲親職",
        "說話、玩、界限",
        [
            "多對話、等佢回應，唔好只靠螢幕",
            "玩係學習：跟興趣、留選擇",
            "管教一致，多用鼓勵",
            "連繫情感同一歲至兩歲單張",
            "脾氣發作先安全身安全，再教方法",
        ],
        None,
    ),
    (
        "02-1-to-3-years/development.md",
        "02-1-to-3-years/development.png",
        "一至三歲發展",
        "行、講、玩",
        [
            "學行之後空間同安全要同步調整",
            "詞彙同兩字句逐漸出現，個別差異大",
            "假想玩同平行玩係正常",
            "18 個月發展評估好重要",
            "完全無指向、無詞彙要盡快評估",
        ],
        None,
    ),
    (
        "02-1-to-3-years/feeding-milk.md",
        "02-1-to-3-years/feeding-milk.png",
        "一歲後奶類",
        "可以轉鮮奶",
        [
            "一歲後可由配方轉全脂鮮奶",
            "繼續均衡固體食物，奶唔係唯一營養",
            "用杯取代長時間含奶瓶",
            "母乳可繼續至 2 歲或以上",
            "分量同過敏問題問健康院或營養師",
        ],
        None,
    ),
    (
        "02-1-to-3-years/vaccines.md",
        "02-1-to-3-years/vaccines.png",
        "一至三歲疫苗",
        "記住 18 個月",
        [
            "18 個月有加強劑，唔好漏",
            "帶針卡，錯過盡快補",
            "完整表見 resources/vaccination.md",
            "開學或託兒或會查接種紀錄",
            "有慢性病先同醫生對時間表",
        ],
        None,
    ),
    (
        "02-1-to-3-years/vision.md",
        "02-1-to-3-years/vision.png",
        "一至三歲視力",
        "盡早發現斜視同弱視",
        [
            "斜視、好近先睇到、瞇眼：求醫",
            "健康院階段頁有視力監察",
            "三歲後有學前視力普查",
            "家族深近視都要定期查",
            "唔好等「大個就會好」",
        ],
        None,
    ),
    (
        "03-3-to-6-years/safety.md",
        "03-3-to-6-years/safety.png",
        "3–6 歲安全",
        "出外、水、交通、藥物",
        [
            "過路牽手、用行人過路線，車內用合適座椅",
            "游水有成人近距離看管",
            "攀爬同窗邊仍然高風險",
            "藥物當糖？要鎖高同教唔好亂食",
            "小冊子（五）：愛護兒童慎防意外",
        ],
        None,
    ),
    (
        "03-3-to-6-years/vision.md",
        "03-3-to-6-years/vision.png",
        "學前視力普查",
        "三歲至六歲",
        [
            "按學校或母嬰健康院通知參加普查",
            "斜視、視力模糊、好近睇先睇到：盡早求醫",
            "普查係篩查，唔等於全面眼科檢查",
            "有通知覆檢唔好拖延",
            "保護眼睛：戶外時間、限制近距離螢幕",
        ],
        None,
    ),
    (
        "03-3-to-6-years/parenting.md",
        "03-3-to-6-years/parenting.png",
        "三至六歲親職",
        "抗逆、品德、準備上學",
        [
            "用故事同日常生活教同理心",
            "容許失敗，幫手拆解困難",
            "規矩清晰、後果合理、讚具體行為",
            "螢幕要限時同共看",
            "官方親職教育（三歲至六歲）頁有系列",
        ],
        None,
    ),
    (
        "03-3-to-6-years/development.md",
        "03-3-to-6-years/development.png",
        "三至六歲發展",
        "語言、社交、自理",
        [
            "句子更完整，開始講故事",
            "學輪流、分享、處理衝突",
            "自理：如廁、梳洗、穿簡單衫",
            "持續唔明指令或無朋友互動：評估",
            "玩仍然係主要學習方式",
        ],
        None,
    ),
    (
        "03-3-to-6-years/nutrition.md",
        "03-3-to-6-years/nutrition.png",
        "三至六歲營養",
        "均衡、少糖鹽油",
        [
            "跟兒童健康飲食金字塔（2–5 歲）",
            "三餐加健康小食，少甜飲",
            "自己食有助發展，容許骯髒同慢",
            "奶類適量，唔好當正餐替代",
            "偏食用重複接觸，唔好威逼",
        ],
        None,
    ),
    (
        "03-3-to-6-years/oral.md",
        "03-3-to-6-years/oral.png",
        "學前口腔",
        "換牙前都要護齒",
        [
            "早晚刷牙，家長補刷至約 7–8 歲",
            "用米粒至豌豆大含氟牙膏（跟牙醫指示）",
            "少甜食甜飲，尤其臨瞓",
            "定期睇牙醫，唔好等痛先去",
            "碰傷牙齒要即時處理",
        ],
        None,
    ),
    (
        "resources/vaccination.md",
        "resources/vaccination.png",
        "學前疫苗總覽",
        "跟衞生署時間表",
        [
            "出生：卡介苗、乙肝第一次",
            "其後 1、2、4、6、12、18 個月有聯合針",
            "小學前仲有加強劑，見官方全文表",
            "帶針卡；錯過補種",
            "完整表先以衞生署網頁為準",
        ],
        None,
    ),
    (
        "resources/formula-advice.md",
        "resources/formula-advice.png",
        "配方奶要知",
        "衞生署建議摘要",
        [
            "配方奶無抗體，亦唔係無菌產品",
            "沖調同儲存唔妥有風險",
            "用咗會減少造奶同餵母乳意欲",
            "一歲前只用嬰兒配方，唔好用普通牛奶",
            "決定前先問母嬰健康院或醫生",
        ],
        None,
    ),
    (
        "resources/parenting-tips.md",
        "resources/parenting-tips.png",
        "共享育兒樂要訣",
        "衞生署口訣",
        [
            "寶寶需求快回應，細心留意多表情",
            "溝通接觸不可少，傾談遊戲添高興",
            "家居安全須確保，建立常規應及早",
            "家人管教要一致，還需鼓勵常讚好",
            "教導子女莫心急，家庭和睦共享樂",
        ],
        None,
    ),
    (
        "resources/mchc-first-placeholder.md",
        "resources/mchc-locations.png",
        "母嬰健康院",
        "時間、地址、電話",
        [
            "各區健康院服務時間唔同，去之前查網",
            "首次帶齊證明文件同出院紙",
            "產後、兒童、家庭計劃、子宮頸或分開預約",
            "熱線 2112 9900",
            "完整名單見本頁表格",
        ],
        None,
    ),
]

# remap last card to real file
CARDS[-1] = (
    "resources/mchc-locations.md",
    *CARDS[-1][1:],
)

MORE = [
    (
        "resources/mchc-registration-form.md",
        "resources/mchc-registration.png",
        "兒童健康服務登記",
        "首次表格",
        [
            "表格可喺共享育兒樂（一）目錄下載",
            "填家長同嬰兒資料、住址、聯絡",
            "帶備身份證明同住址證明",
            "到院先交表，職員會核對",
            "詳見首次到院筆記",
        ],
        None,
    ),
    (
        "resources/ichip.md",
        "resources/ichip.png",
        "幼兒健康及發展綜合計劃",
        "ICHIP",
        [
            "健康院按年齡監察生長同發展",
            "有需要會轉介評估或專科",
            "家長觀察日常同健康院檢查互補",
            "準時覆診先跟到進度",
            "詳情問所屬母嬰健康院",
        ],
        None,
    ),
    (
        "resources/public-talks.md",
        "resources/public-talks.png",
        "公眾健康講座",
        "產前產後至學前",
        [
            "題目包括餵哺、飲食、發展、情緒",
            "部分線上，部分健康院現場",
            "時間表會更新，以官網為準",
            "引進固體食物講座好實用",
            "熱線或網頁查最近場次",
        ],
        None,
    ),
    (
        "resources/parent-child-elearning.md",
        "resources/parent-child-elearning.png",
        "親子網上學習",
        "親子一點通／易點明",
        [
            "短片同單元方便喺屋企學",
            "題目覆蓋餵哺、發展、親職",
            "唔取代健康院面見",
            "可同伴侶一齊睇",
            "入口見官方簡介頁",
        ],
        None,
    ),
]


def insert_images(md_rel: str, image_rels: list[str]) -> None:
    path = ROOT / md_rel
    text = path.read_text(encoding="utf-8")
    if "## 資訊圖" in text:
        return
    block = ["", "## 資訊圖", ""]
    for img in image_rels:
        # relative from the md file
        md_dir = path.parent
        img_path = IMG / img
        rel = Path(os.path.relpath(img_path, md_dir)).as_posix()
        alt = img_path.stem.replace("-", " ")
        block.append(f"![{alt}]({rel})")
        block.append("")
    block.append("圖内文字根據衞生署家庭健康服務網頁整理，**唔構成醫療建議**。")
    block.append("")
    chunk = "\n".join(block)
    if "## 參考來源" in text:
        text = text.replace("## 參考來源", chunk + "## 參考來源", 1)
    else:
        text = text.rstrip() + "\n" + chunk
    path.write_text(text, encoding="utf-8")


def os_rel(start: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start))


import os


def main() -> None:
    grouped: dict[str, list[str]] = {}
    for md, img, title, sub, items, note in CARDS + MORE:
        save_card(img, title, sub, items, note)
        grouped.setdefault(md, []).append(img)
        print("wrote", img)
    # extra split cards
    save_split(
        "00-0-to-1-month/hunger-cues.png",
        "肚餓信號",
        "先安撫，後餵哺",
        "早期（宜餵）",
        ["轉頭覓食", "嘴巴張開", "身體躍躍欲動", "伸手入口"],
        "較遲（先安撫）",
        ["大聲哭鬧", "煩躁扭動", "滿面通紅", "安撫後再餵"],
    )
    grouped.setdefault("00-0-to-1-month/breastfeeding.md", []).append(
        "00-0-to-1-month/hunger-cues.png"
    )
    save_split(
        "mother/postnatal-exercise-dont.png",
        "產後運動：做同唔好做",
        "量力、循序漸進",
        "可以",
        ["深層收腹同盆骨底", "腰背左右擺膝", "由步行 10 分鐘開始", "抱 BB 時收腹"],
        "未適宜",
        ["仰臥起坐", "仰臥抬腿", "抬頭時肚隆起仍加難", "手術產未問醫生就練"],
    )
    grouped.setdefault("mother/postnatal-exercise.md", []).append(
        "mother/postnatal-exercise-dont.png"
    )
    for md, imgs in grouped.items():
        insert_images(md, imgs)
        print("linked", md)


if __name__ == "__main__":
    main()
