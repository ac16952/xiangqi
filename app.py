import streamlit as st
import random
from typing import List, Dict, Any
from models.xiangqi import XiangqiBoard, ChessPiece, Color, PieceType, DivinationResult, WuXing
from divination_engine import perform_divination
from urllib.parse import urlencode

# --- CONFIG & SETUP ---
st.set_page_config(
    page_title="象棋卜卦",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE ENCODING & DECODING ---
PIECE_TYPE_TO_CODE = {p: p.name[0] for p in PieceType}
CODE_TO_PIECE_TYPE = {v: k for k, v in PIECE_TYPE_TO_CODE.items()}
COLOR_TO_CODE = {Color.RED: 'R', Color.BLACK: 'B'}
CODE_TO_COLOR = {v: k for k, v in COLOR_TO_CODE.items()}
PIECE_DEFINITIONS_MAP = {(p_type, color): (points, wu_xing) for p_type, color, points, wu_xing in XiangqiBoard.PIECE_DEFINITIONS}

def encode_board(pieces: List[ChessPiece]) -> str:
    codes = [COLOR_TO_CODE[p.color] + PIECE_TYPE_TO_CODE[p.piece_type] for p in pieces]
    return ",".join(codes)

def decode_board(board_str: str) -> List[ChessPiece]:
    pieces = []
    codes = board_str.split(',')
    for code in codes:
        if len(code) == 2:
            color = CODE_TO_COLOR.get(code[0])
            p_type = CODE_TO_PIECE_TYPE.get(code[1])
            if color and p_type:
                points, wu_xing = PIECE_DEFINITIONS_MAP.get((p_type, color), (0, None))
                if wu_xing:
                    pieces.append(ChessPiece(p_type, color, points, wu_xing))
    return pieces

# --- UI RENDERING ---
def render_gua_piece(position_name: str, position_number: int, selected_positions: Dict[str, Any]):
    piece = selected_positions.get(position_name)
    if piece:
        color_class = "chess-piece-red" if piece.color == Color.RED else "chess-piece-black"
        st.markdown(f'<div class="chess-piece {color_class}">{piece.display_name}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="gua-number">{position_number}</div>', unsafe_allow_html=True)

def render_analysis_sections(result: DivinationResult):
    analysis_sections = {
        "🎭 呈現狀態": result.analysis.get('state'),
        "🤝 互動關係": result.analysis.get('interaction'),
        "💰 付出與收穫": result.analysis.get('give_and_take'),
        "🏥 健康分析": result.health_analysis
    }
    for title, content in analysis_sections.items():
        if content:
            with st.expander(title, expanded=True):
                st.write(content)

st.markdown("""
<style>
.chess-piece, .gua-number {
    width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-weight: bold; font-size: 16px; margin: 5px auto;
    border: 2px solid #888; transition: all 0.3s ease; cursor: pointer;
}
.chess-piece-red { background-color: #dc3545 !important; color: white !important; }
.chess-piece-black { background-color: #343a40 !important; color: white !important; }
.gua-number { border: 2px solid #333; background-color: white; }
</style>
""", unsafe_allow_html=True)

def main():
    # --- 1. 狀態管理：從URL讀取或初始化 ---
    params = st.query_params
    board_str = params.get("b")

    if not board_str:
        initial_board = XiangqiBoard()
        st.query_params["b"] = encode_board(initial_board.pieces)
        st.rerun()

    board_pieces = decode_board(board_str)
    revealed_indices = {int(i) for i in params.get_all("r") if i.isdigit()}
    selected_indices = [int(i) for i in params.get_all("s") if i.isdigit()]
    show_divination = params.get("div") == "1"

    selected_pieces = [board_pieces[i] for i in selected_indices]
    selected_positions = {}
    position_order = ['center', 'left', 'right', 'top', 'bottom']
    for i, piece in enumerate(selected_pieces):
        selected_positions[position_order[i]] = piece

    # --- 2. UI 渲染 ---
    st.title("♟️ 象棋卜卦")
    st.markdown("點擊象棋翻面並選擇，探索您的運勢")
    st.markdown("---")

    # 控制按鈕
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🎲 重新生成棋盤", type="primary"):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button("🧹 清除選擇"):
            st.query_params.from_dict({"b": board_str})
            st.rerun()
    with col3:
        if st.button("🔮 開始卜卦", disabled=len(selected_indices) != 5):
            st.query_params["div"] = "1"
            st.rerun()
    with col4:
        st.metric("已選擇", f"{len(selected_indices)}/5")
    
    st.markdown("---")
    
    # 主要內容區域
    col_board, col_gua = st.columns([2, 1])
    with col_board:
        st.subheader("棋盤")
        st.markdown("點擊象棋翻面並選擇（最多5個）")
        for row in range(4):
            cols = st.columns(8)
            for col in range(8):
                with cols[col]:
                    index = row * 8 + col
                    piece = board_pieces[index]
                    is_revealed = index in revealed_indices
                    is_selected = index in selected_indices

                    new_revealed = revealed_indices.union({index})
                    new_selected = selected_indices.copy()
                    if is_selected:
                        new_selected.remove(index)
                    elif len(new_selected) < 5:
                        new_selected.append(index)
                    
                    query_dict = [("b", board_str)] + \
                                 [("r", r_idx) for r_idx in sorted(list(new_revealed))] + \
                                 [("s", s_idx) for s_idx in new_selected]
                    href = f"?{urlencode(query_dict)}"

                    style = (
                        "width:60px; height:60px; display:flex; align-items:center; "
                        "justify-content:center; font-weight:bold; text-decoration:none; "
                        "border-radius:50%; margin: 5px auto; transition: all 0.2s ease;"
                    )
                    if is_revealed:
                        style += "background-color:#dc3545; color:white;" if piece.color == Color.RED else "background-color:#343a40; color:white;"
                    else:
                        style += "background-color:#F5F5DC; color:#F5F5DC;"
                    if is_selected:
                        style += "border: 4px solid #ffc107; box-shadow: 0 0 10px #ffc107;"
                    else:
                        style += "border: 4px solid #888;"
                    label = piece.display_name if is_revealed else "&nbsp;"
                    st.markdown(f'<a href="{href}" style="{style}" target="_self">{label}</a>', unsafe_allow_html=True)

    with col_gua:
        _, center_col, _ = st.columns([0.5, 2, 0.5])
        with center_col:
            st.subheader("卦象")
            _, col_top, _ = st.columns([1, 1, 1])
            with col_top:
                render_gua_piece('top', 4, selected_positions)
            col_left, col_center, col_right = st.columns([1, 1, 1])
            with col_left:
                render_gua_piece('left', 2, selected_positions)
            with col_center:
                render_gua_piece('center', 1, selected_positions)
            with col_right:
                render_gua_piece('right', 3, selected_positions)
            _, col_bottom, _ = st.columns([1, 1, 1])
            with col_bottom:
                render_gua_piece('bottom', 5, selected_positions)

    # --- 3. 卜卦結果渲染 ---
    if show_divination and len(selected_pieces) == 5:
        result = perform_divination(selected_pieces)
        st.divider()
        st.subheader("🔮 卜卦結果")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("陰陽平衡", "平衡" if result.yin_yang_balance else "不平衡")
        with col2:
            st.metric("平衡分數", f"{result.balance_score}/100")
        with col3:
            red_count = sum(1 for p in result.selected_pieces if p.color == Color.RED)
            st.metric("紅黑比例", f"{red_count}:{5-red_count}")
        if result.patterns:
            st.subheader("📊 格局分析")
            for pattern in result.patterns:
                st.success(f"✨ {pattern}")
        if result.missing_talents:
            st.subheader("⚠️ 三才缺失")
            for talent in result.missing_talents:
                st.warning(f"缺少 {talent}")
        render_analysis_sections(result)
        if result.suggestions:
            st.subheader("💡 建議")
            for i, suggestion in enumerate(result.suggestions, 1):
                st.info(f"{i}. {suggestion}")

if __name__ == "__main__":
    main()
