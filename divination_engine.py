"""
象棋卜卦引擎
從原有的Flask路由中提取的卜卦邏輯
"""

from typing import List, Dict, Any
from models.xiangqi import ChessPiece, Color, PieceType, DivinationResult, WuXing

def perform_divination(selected_pieces: List[ChessPiece]) -> DivinationResult:
    """執行解卦邏輯"""
    
    # 位置映射：中間1，左邊2，右邊3，上方4，下方5
    positions = {
        'center': 0,  # 中間
        'left': 1,    # 左邊
        'right': 2,   # 右邊
        'top': 3,     # 上方
        'bottom': 4   # 下方
    }
    
    # 1. 陰陽平衡判斷
    red_count = sum(1 for piece in selected_pieces if piece.color == Color.RED)
    black_count = sum(1 for piece in selected_pieces if piece.color == Color.BLACK)
    
    yin_yang_balance = (red_count == 2 and black_count == 3) or (red_count == 3 and black_count == 2)
    balance_score = 100 if yin_yang_balance else 95  # 不平衡減5分
    
    # 2. 三才判斷
    missing_talents = check_missing_talents(selected_pieces)
    
    # 3. 格局判斷
    patterns = identify_patterns(selected_pieces)
    
    # 4. 分析
    analysis = {
        'state': analyze_state(selected_pieces),
        'interaction': analyze_interaction(selected_pieces),
        'give_and_take': analyze_give_and_take(selected_pieces)
    }
    
    # 5. 健康分析
    health_analysis = analyze_health(selected_pieces)
    
    # 6. 建議
    suggestions = generate_suggestions(selected_pieces, patterns, yin_yang_balance)
    
    return DivinationResult(
        selected_pieces=selected_pieces,
        positions=positions,
        yin_yang_balance=yin_yang_balance,
        balance_score=balance_score,
        missing_talents=missing_talents,
        patterns=patterns,
        analysis=analysis,
        health_analysis=health_analysis,
        suggestions=suggestions
    )

def check_missing_talents(pieces: List[ChessPiece]) -> List[str]:
    """檢查三才缺失"""
    missing = []
    
    # 天格：將帥、車俥、兵卒
    heaven_pieces = [PieceType.GENERAL, PieceType.CHARIOT, PieceType.SOLDIER]
    if not any(piece.piece_type in heaven_pieces for piece in pieces):
        missing.append("天格")
    
    # 人格：士仕、馬傌、炮包
    human_pieces = [PieceType.ADVISOR, PieceType.HORSE, PieceType.CANNON]
    if not any(piece.piece_type in human_pieces for piece in pieces):
        missing.append("人格")
    
    # 地格：象相、卒
    earth_pieces = [PieceType.ELEPHANT, PieceType.SOLDIER]
    if not any(piece.piece_type in earth_pieces for piece in pieces):
        missing.append("地格")
    
    return missing

def identify_patterns(pieces: List[ChessPiece]) -> List[str]:
    """識別格局"""
    patterns = []
    
    # 檢查全紅全黑格
    colors = [piece.color for piece in pieces]
    if all(color == Color.RED for color in colors):
        patterns.append("全紅格")
    elif all(color == Color.BLACK for color in colors):
        patterns.append("全黑格")
    
    # 檢查一枝獨秀格
    red_count = sum(1 for piece in pieces if piece.color == Color.RED)
    if red_count == 1 or red_count == 4:
        patterns.append("一枝獨秀格")
    
    # 檢查聲聲格（中間與四周顏色不同）
    center_piece = pieces[0]
    surrounding_pieces = pieces[1:5]
    if all(piece.color != center_piece.color for piece in surrounding_pieces):
        if center_piece.color == Color.BLACK:
            patterns.append("聲聲格（外人看好）")
        else:
            patterns.append("聲聲格（外人看不好）")
    
    # 檢查眾星拱月格（中間與四周顏色相同）
    if all(piece.color == center_piece.color for piece in surrounding_pieces):
        patterns.append("眾星拱月格")
    
    # 檢查十字天助格（1,2,3或1,4,5同色）
    if ((pieces[0].color == pieces[1].color == pieces[2].color) or 
        (pieces[0].color == pieces[3].color == pieces[4].color)):
        patterns.append("十字天助格")
    
    # 檢查勝利格（2,3,5同色）
    if pieces[1].color == pieces[2].color == pieces[4].color:
        patterns.append("勝利格")
    
    # 檢查雨傘格（2,3,4同色）
    if pieces[1].color == pieces[2].color == pieces[3].color:
        patterns.append("雨傘格")
    
    # 檢查桃花格（包包或包將組合）
    piece_types = [piece.piece_type for piece in pieces]
    cannon_count = sum(1 for pt in piece_types if pt == PieceType.CANNON)
    general_count = sum(1 for pt in piece_types if pt == PieceType.GENERAL)
    
    if cannon_count >= 2:
        patterns.append("桃花格（包包）")
    elif cannon_count >= 1 and general_count >= 1:
        patterns.append("桃花格（包將）")
    
    # 檢查三人同心格
    soldier_count = sum(1 for pt in piece_types if pt == PieceType.SOLDIER)
    if soldier_count >= 3:
        patterns.append("三人同心格")
    
    # 檢查事業格（象與車馬同時出現）
    has_elephant = any(piece.piece_type == PieceType.ELEPHANT for piece in pieces)
    has_chariot = any(piece.piece_type == PieceType.CHARIOT for piece in pieces)
    has_horse = any(piece.piece_type == PieceType.HORSE for piece in pieces)
    if has_elephant and (has_chariot or has_horse):
        patterns.append("事業格")
    
    # 檢查富貴格（將帥與士象同時出現）
    has_general = any(piece.piece_type == PieceType.GENERAL for piece in pieces)
    has_advisor = any(piece.piece_type == PieceType.ADVISOR for piece in pieces)
    if has_general and (has_advisor or has_elephant):
        patterns.append("富貴格")
    
    # 檢查困擾格（兩對好朋友）
    friend_pairs = count_friend_pairs(pieces)
    if friend_pairs >= 2:
        patterns.append("困擾格")
    
    # 檢查分離格（不同顏色的好朋友分開）
    if check_separation_pattern(pieces):
        patterns.append("分離格（離婚格）")
    
    # 檢查消耗格（兩支同色同類型棋子）
    if check_consumption_pattern(pieces):
        patterns.append("消耗格")
    
    # 檢查好朋友格
    if check_good_friend_pattern(pieces):
        patterns.append("好朋友格")
    
    return patterns

def count_friend_pairs(pieces: List[ChessPiece]) -> int:
    """計算好朋友對數"""
    pairs = 0
    piece_types = [piece.piece_type for piece in pieces]
    
    # 檢查士仕對
    advisor_count = sum(1 for pt in piece_types if pt == PieceType.ADVISOR)
    pairs += advisor_count // 2
    
    # 檢查包炮對
    cannon_count = sum(1 for pt in piece_types if pt == PieceType.CANNON)
    pairs += cannon_count // 2
    
    # 檢查馬傌對
    horse_count = sum(1 for pt in piece_types if pt == PieceType.HORSE)
    pairs += horse_count // 2
    
    return pairs

def check_separation_pattern(pieces: List[ChessPiece]) -> bool:
    """檢查分離格"""
    center = pieces[0]
    left = pieces[1]
    right = pieces[2]
    top = pieces[3]
    bottom = pieces[4]
    
    # 左右分離
    if (left.color != center.color and right.color != center.color and 
        left.color != right.color):
        return True
    
    # 上下分離
    if (top.color != center.color and bottom.color != center.color and 
        top.color != bottom.color):
        return True
    
    return False

def check_consumption_pattern(pieces: List[ChessPiece]) -> bool:
    """檢查消耗格"""
    for i in range(len(pieces)):
        for j in range(i + 1, len(pieces)):
            if (pieces[i].piece_type == pieces[j].piece_type and 
                pieces[i].color == pieces[j].color):
                return True
    return False

def check_good_friend_pattern(pieces: List[ChessPiece]) -> bool:
    """檢查好朋友格"""
    center = pieces[0]
    surrounding = pieces[1:5]
    
    for piece in surrounding:
        if piece.color != center.color:
            if is_good_friend_combination(center, piece):
                return True
    
    return False

def is_good_friend_combination(piece1: ChessPiece, piece2: ChessPiece) -> bool:
    """判斷是否為好朋友組合"""
    if piece1.color == piece2.color:
        return False
    
    good_combinations = [
        (PieceType.ADVISOR, PieceType.ADVISOR),
        (PieceType.ELEPHANT, PieceType.ELEPHANT),
        (PieceType.CHARIOT, PieceType.CHARIOT),
        (PieceType.SOLDIER, PieceType.SOLDIER),
        (PieceType.HORSE, PieceType.HORSE),
        (PieceType.CANNON, PieceType.CANNON)
    ]
    
    combination = (piece1.piece_type, piece2.piece_type)
    return combination in good_combinations or (combination[1], combination[0]) in good_combinations

def analyze_state(pieces: List[ChessPiece]) -> str:
    """分析呈現狀態，結合中心棋子與周圍棋子的影響，提供更動態的解讀。"""
    center_piece = pieces[0]
    surrounding_pieces = pieces[1:]

    # 核心狀態描述
    state_descriptions = {
        PieceType.GENERAL: "您目前的核心狀態展現出「帥」的特質：具有領導能力和影響力，喜歡指揮他人，但可能過於固執，需要學會傾聽他人意見",
        PieceType.ADVISOR: "您目前的核心狀態展現出「仕」的特質：智慧能力佳，善於輔佐，有指揮與發令的氣勢，但可能過於多慮，有時會忽略親近的人",
        PieceType.ELEPHANT: "您目前的核心狀態展現出「相」的特質：工作能力佳但較為被動，喜歡靜坐而言勝過於起而行，需要他人協助才能發揮潛力",
        PieceType.CHARIOT: "您目前的核心狀態展現出「俥」的特質：充滿積極進取的能量，敢於冒險，有強烈的主觀想法，但需注意過於衝動，不願受約束可能導致衝突",
        PieceType.HORSE: "您目前的核心狀態展現出「傌」的特質：勤奮努力且富有創意，有許多浪漫的想法，但方向可能不定，心太軟容易管閒事",
        PieceType.CANNON: "您目前的核心狀態展現出「炮」的特質：內心渴望突破現狀，充滿變動的能量，但這也可能帶來不穩定與風險，容易感到恐懼或尋求取巧",
        PieceType.SOLDIER: "您目前的核心狀態展現出「兵」的特質：做事踏實穩重，一步一腳印，重視現實和日常，但可能想太多，行動力較弱"
    }

    # 周圍棋子的影響描述 (同色, 異色)
    influence_descriptions = {
        PieceType.GENERAL: ("一股強大的領導力量在支持您", "一股不同的主導意見在影響您"),
        PieceType.ADVISOR: ("一份來自智囊的輔佐與支持", "一個需要您運用智慧去應對的建議"),
        PieceType.ELEPHANT: ("一股穩固的防守與支持力量", "一個提醒您需要穩固根基的信號"),
        PieceType.CHARIOT: ("一股強勁的行動力與衝勁", "一個來自外界的直接挑戰或衝擊"),
        PieceType.HORSE: ("一份靈活的創意與助力", "一個帶來變數與不確定性的因素"),
        PieceType.CANNON: ("一股突破性的變革能量", "一個潛在的衝突或需要跳躍式思維解決的問題"),
        PieceType.SOLDIER: ("一份務實肯幹的支持", "一個提醒您需要腳踏實地的聲音")
    }

    # 1. 取得核心狀態描述
    base_description = state_descriptions.get(center_piece.piece_type, "狀態分析中...")

    # 2. 根據中心棋子顏色判斷主要傾向
    if center_piece.color == Color.RED:
        color_trait = "您的外在表現較為積極主動，容易被他人看見與認可"
    else:
        color_trait = "您的內在力量較強，但外在表現可能較為內斂，謀定而後動"

    # 3. 分析周圍棋子的影響
    influence_texts = []
    for piece in surrounding_pieces:
        same_color_text, diff_color_text = influence_descriptions.get(
            piece.piece_type, ("一股未知的力量", "一股未知的力量")
        )
        
        if piece.color == center_piece.color:
            influence_texts.append(f"來自（{piece.display_name}）的{same_color_text}")
        else:
            influence_texts.append(f"來自（{piece.display_name}）的{diff_color_text}")

    # 4. 組合完整的分析文本
    full_analysis = [f"{base_description}，{color_trait}。"]
    if influence_texts:
        full_analysis.append("\n在您周圍，同時存在著以下幾種力量：")
        for text in influence_texts:
            full_analysis.append(f"- {text}。")

    return "\n".join(full_analysis)

def analyze_interaction(pieces: List[ChessPiece]) -> str:
    """分析互動關係"""
    center = pieces[0]
    left = pieces[1]
    right = pieces[2]
    top = pieces[3]
    bottom = pieces[4]
    
    interactions = []
    
    # 分析與左方的關係
    if left.color == center.color:
        interactions.append("與左方（同事/伴侶）關係和諧，價值觀相近")
    else:
        if is_good_friend_combination(center, left):
            interactions.append("與左方雖有差異但能互補，關係良好")
        else:
            interactions.append("與左方存在價值觀差異，需要更多溝通")
    
    # 分析與右方的關係
    if right.color == center.color:
        interactions.append("與右方（同事/家人）關係穩定，互相支持")
    else:
        if is_good_friend_combination(center, right):
            interactions.append("與右方能夠互相學習，關係有益")
        else:
            interactions.append("與右方關係需要調整，避免衝突")
    
    # 分析與上方的關係
    if top.color == center.color:
        interactions.append("與長輩/上司關係良好，容易獲得支持")
    else:
        if is_good_friend_combination(center, top):
            interactions.append("與長輩/上司雖有不同但能獲得指導")
        else:
            interactions.append("與長輩/上司關係需要改善，可能有代溝")
    
    # 分析與下方的關係
    if bottom.color == center.color:
        interactions.append("與晚輩/下屬關係融洽，能夠有效指導")
    else:
        if is_good_friend_combination(center, bottom):
            interactions.append("與晚輩/下屬能夠教學相長")
        else:
            interactions.append("與晚輩/下屬關係需要耐心經營")
    
    return "；".join(interactions)

def analyze_give_and_take(pieces: List[ChessPiece]) -> str:
    """分析付出與收穫"""
    total_points = sum(piece.points for piece in pieces)
    center_points = pieces[0].points
    
    personal_ratio = center_points / total_points
    
    center_color = pieces[0].color
    same_color_count = sum(1 for piece in pieces if piece.color == center_color)
    same_color_points = sum(piece.points for piece in pieces if piece.color == center_color)
    
    diff_color_count = 5 - same_color_count
    diff_color_points = total_points - same_color_points
    
    analysis_parts = []
    
    if personal_ratio >= 0.4:
        analysis_parts.append("個人能力強，在團隊中扮演重要角色")
    elif personal_ratio >= 0.25:
        analysis_parts.append("個人能力中等，需要與他人合作")
    else:
        analysis_parts.append("個人能力相對較弱，需要更多學習和成長")
    
    if same_color_count >= 4:
        analysis_parts.append("周圍支持力量強大，容易獲得幫助")
    elif same_color_count >= 3:
        analysis_parts.append("有一定的支持力量，但需要主動爭取")
    else:
        analysis_parts.append("支持力量較少，需要靠自己努力")
    
    if diff_color_count >= 3:
        analysis_parts.append("面臨較多挑戰，但也有更多學習機會")
    elif diff_color_count >= 2:
        analysis_parts.append("挑戰與機會並存，需要平衡應對")
    else:
        analysis_parts.append("環境相對穩定，但可能缺乏刺激和成長")
    
    if same_color_points > diff_color_points:
        analysis_parts.append("付出會有相應回報，整體收穫大於付出")
    elif same_color_points == diff_color_points:
        analysis_parts.append("付出與收穫基本平衡")
    else:
        analysis_parts.append("目前付出較多，收穫需要時間累積")
    
    return "；".join(analysis_parts)

def analyze_health(pieces: List[ChessPiece]) -> str:
    """分析健康狀況"""
    wu_xing_count = {}
    for piece in pieces:
        wu_xing = piece.wu_xing
        wu_xing_count[wu_xing] = wu_xing_count.get(wu_xing, 0) + 1
    
    health_issues = []
    
    # 檢查五行過多的情況
    for wu_xing, count in wu_xing_count.items():
        if count >= 3:
            if wu_xing.value == "木":
                health_issues.append("木過多：注意肝膽健康，避免過度勞累，控制情緒起伏")
            elif wu_xing.value == "火":
                health_issues.append("火過多：注意心臟血液循環，避免過度興奮，保持心情平靜")
            elif wu_xing.value == "土":
                health_issues.append("土過多：注意脾胃消化系統，避免思慮過度，規律飲食")
            elif wu_xing.value == "金":
                health_issues.append("金過多：注意肺部呼吸系統，避免過度悲觀，保持樂觀心態")
            elif wu_xing.value == "水":
                health_issues.append("水過多：注意腎臟泌尿系統，避免過度恐懼，增強自信")
    
    # 檢查五行缺失
    all_wu_xing = ["木", "火", "土", "金", "水"]
    present_wu_xing = [wu_xing.value for wu_xing in wu_xing_count.keys()]
    missing_wu_xing = [wx for wx in all_wu_xing if wx not in present_wu_xing]
    
    for missing in missing_wu_xing:
        if missing == "木":
            health_issues.append("缺木：可能肝膽功能較弱，建議多運動，培養耐心")
        elif missing == "火":
            health_issues.append("缺火：可能心臟功能較弱，建議保持熱情，多與人交流")
        elif missing == "土":
            health_issues.append("缺土：可能脾胃功能較弱，建議規律作息，穩定情緒")
        elif missing == "金":
            health_issues.append("缺金：可能肺部功能較弱，建議深呼吸練習，培養決斷力")
        elif missing == "水":
            health_issues.append("缺水：可能腎臟功能較弱，建議多喝水，培養智慧")
    
    # 特殊健康提醒
    center_piece = pieces[0]
    if center_piece.piece_type == PieceType.SOLDIER:
        health_issues.append("中間為兵卒：特別注意脾胃健康，避免暴飲暴食")
    elif center_piece.piece_type == PieceType.CANNON:
        health_issues.append("中間為包炮：注意腎臟和泌尿系統，避免過度緊張")
    
    if check_consumption_pattern(pieces):
        health_issues.append("存在消耗格：注意身心平衡，避免過度消耗體力和精神")
    
    if not health_issues:
        health_issues.append("五行相對平衡，整體健康狀況良好，建議保持現有的生活方式")
    
    return "；".join(health_issues)

def generate_suggestions(pieces: List[ChessPiece], patterns: List[str], yin_yang_balance: bool) -> List[str]:
    """生成建議"""
    suggestions = []
    
    # 陰陽平衡建議
    if not yin_yang_balance:
        red_count = sum(1 for piece in pieces if piece.color == Color.RED)
        if red_count > 3:
            suggestions.append("紅棋過多，建議多與內斂穩重的人交流，學習沉穩的處事方式")
        else:
            suggestions.append("黑棋過多，建議多與積極主動的人接觸，增加外向表達的機會")
    
    # 格局相關建議
    if "全紅格" in patterns or "全黑格" in patterns:
        suggestions.append("格局過於單一，建議多元化發展，接觸不同類型的人和事物，避免思維僵化")
    
    if "一枝獨秀格" in patterns:
        suggestions.append("雖然獨特出眾，但要注意與他人的協調合作，避免孤立無援")
    
    if any("聲聲格" in pattern for pattern in patterns):
        if "聲聲格（外人看好）" in patterns:
            suggestions.append("外界對您評價良好，但要注意內在修養，避免表裡不一")
        else:
            suggestions.append("外界可能對您有誤解，建議多展現真實的自己，改善外在形象")
    
    if "十字天助格" in patterns:
        suggestions.append("有天助之象，是發展的好時機，建議把握機會積極進取")
    
    if "勝利格" in patterns:
        suggestions.append("具有勝利的潛質，建議保持信心，堅持努力，成功在望")
    
    if "雨傘格" in patterns:
        suggestions.append("有長輩庇護，但也要培養獨立能力，避免過度依賴")
    
    if any("桃花格" in pattern for pattern in patterns):
        suggestions.append("人際關係豐富，異性緣佳，但要注意感情專一，避免桃花劫")
    
    if "事業格" in patterns:
        suggestions.append("適合專注事業發展，有成功的潛質，但要注意工作與生活的平衡")
    
    if "富貴格" in patterns:
        suggestions.append("有富貴之象，容易得到貴人相助，建議善用人際關係，回饋社會")
    
    if "困擾格" in patterns:
        suggestions.append("面臨選擇困難，建議冷靜分析利弊，必要時尋求專業建議")
    
    if "分離格" in patterns:
        suggestions.append("人際關係可能面臨考驗，建議加強溝通，化解誤會，維護重要關係")
    
    if "消耗格" in patterns:
        suggestions.append("存在能量消耗，建議適度休息，避免過度勞累，注意身心平衡")
    
    if "好朋友格" in patterns:
        suggestions.append("人際關係良好，有互助的朋友，建議珍惜友誼，互相扶持")
    
    # 根據中間棋子和組合給出具體建議
    center_piece = pieces[0]
    piece_types_in_selection = {p.piece_type for p in pieces}

    if center_piece.piece_type == PieceType.GENERAL:
        suggestion = "具有領導才能，建議培養包容心，學會授權，避免事必躬親。"
        if PieceType.CHARIOT in piece_types_in_selection and center_piece.piece_type != PieceType.CHARIOT:
            suggestion += " 結合（俥/車）的行動力，您的領導將更具執行效率。"
        if PieceType.ADVISOR in piece_types_in_selection and center_piece.piece_type != PieceType.ADVISOR:
            suggestion += " 善用（仕/士）的智慧，您的決策會更加周全。"
        suggestions.append(suggestion)
    elif center_piece.piece_type == PieceType.ADVISOR:
        suggestion = "智慧能力強，建議多關心身邊親近的人，平衡工作與家庭。"
        if PieceType.GENERAL in piece_types_in_selection and center_piece.piece_type != PieceType.GENERAL:
            suggestion += " 當前是您發揮輔佐才能，協助領導者（帥/將）的絕佳時機。"
        suggestions.append(suggestion)
    elif center_piece.piece_type == PieceType.ELEPHANT:
        suggestion = "需要提高行動力，建議設定明確目標，主動出擊，不要只是等待。"
        if PieceType.SOLDIER in piece_types_in_selection and center_piece.piece_type != PieceType.SOLDIER:
            suggestion += " 結合（兵/卒）的穩健，您的行動將會更加踏實可靠。"
        suggestions.append(suggestion)
    elif center_piece.piece_type == PieceType.CHARIOT:
        suggestion = "行動力強但需要方向，建議制定詳細計劃，避免盲目衝動。"
        if PieceType.HORSE in piece_types_in_selection and center_piece.piece_type != PieceType.HORSE:
            suggestion += " 搭配（傌/馬）的靈活，能讓您在衝刺時找到更多可能性。"
        suggestions.append(suggestion)
    elif center_piece.piece_type == PieceType.HORSE:
        suggestion = "富有創意但方向不定，建議專注一個領域深耕，避免三心二意。"
        if PieceType.CANNON in piece_types_in_selection and center_piece.piece_type != PieceType.CANNON:
            suggestion += " 若能將創意與（炮/包）的突破力結合，將有驚人成果。"
        suggestions.append(suggestion)
    elif center_piece.piece_type == PieceType.CANNON:
        suggestion = "想要突破但風險高，建議穩中求進，做好風險評估再行動。"
        if PieceType.SOLDIER in piece_types_in_selection and center_piece.piece_type != PieceType.SOLDIER:
            suggestion += " 奠基於（兵/卒）的穩固基礎上進行突破，成功率會更高。"
        suggestions.append(suggestion)
    elif center_piece.piece_type == PieceType.SOLDIER:
        suggestion = "踏實穩重是優點，建議適度冒險，抓住機會提升自己。"
        if PieceType.CHARIOT in piece_types_in_selection and center_piece.piece_type != PieceType.CHARIOT:
            suggestion += " 藉助（俥/車）的衝勁，能幫助您跨出舒適圈，迎接新挑戰。"
        suggestions.append(suggestion)
    
    # 健康相關建議
    wu_xing_count = {}
    for piece in pieces:
        wu_xing = piece.wu_xing
        wu_xing_count[wu_xing] = wu_xing_count.get(wu_xing, 0) + 1
    
    for wu_xing, count in wu_xing_count.items():
        if count >= 3:
            if wu_xing.value == "土":
                suggestions.append("脾胃較弱，建議規律飲食，少食多餐，避免暴飲暴食")
            elif wu_xing.value == "水":
                suggestions.append("腎氣不足，建議早睡早起，適度運動，避免過度勞累")
    
    # 如果沒有特殊建議，給出通用建議
    if not suggestions:
        suggestions.append("整體運勢平穩，建議保持現狀並適度進取，注意身心平衡")
        suggestions.append("多與不同類型的人交流，擴展視野，增加人生閱歷")
    
    return suggestions
