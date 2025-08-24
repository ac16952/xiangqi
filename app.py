import streamlit as st
import random
from typing import List, Dict, Any
from models.xiangqi import XiangqiBoard, ChessPiece, Color, PieceType, DivinationResult, WuXing
from divination_engine import perform_divination

# 設定頁面配置
st.set_page_config(
    page_title="象棋卜卦",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def generate_board():
    """生成隨機棋盤並重設狀態"""
    board = XiangqiBoard()
    st.session_state.board_pieces = board.pieces
    st.session_state.board_generated = True
    st.session_state.divination_result = None  # 清除卜卦結果
    st.query_params.clear()  # 清空URL參數以開始新的一局

def start_divination(selected_pieces):
    """開始卜卦"""
    if len(selected_pieces) == 5:
        result = perform_divination(selected_pieces)
        st.session_state.divination_result = result
    else:
        st.session_state.divination_result = None

def render_gua_piece(position_name: str, position_number: int, selected_positions: Dict[str, Any]):
    """Renders a single piece or a placeholder in the Gua display area."""
    piece = selected_positions.get(position_name)
    if piece:
        color_class = "chess-piece-red" if piece.color == Color.RED else "chess-piece-black"
        st.markdown(
            f'<div class="chess-piece {color_class}" style="margin: 0 auto;">{piece.display_name}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="gua-number">{position_number}</div>',
            unsafe_allow_html=True
        )

def render_analysis_sections(result: DivinationResult):
    """Renders the expandable analysis sections."""
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

# 自定義CSS樣式 (只保留卦象區和通用樣式)
st.markdown("""
<style>
.chess-piece {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 16px;
    margin: 2px auto;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.chess-piece-red {
    background-color: #dc3545 !important;
    color: white !important;
}

.chess-piece-black {
    background-color: #343a40 !important;
    color: white !important;
}

.gua-display {
    display: grid;
    grid-template-areas: 
        "title top ."
        "left center right"
        ". bottom ."
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: 1fr 1fr 1fr;
    gap: 15px;
    max-width: 350px;
    margin: 0 auto;
    border: 2px solid #333;
    padding: 20px;
    background-color: #f8f9fa;
}

.gua-title {
    grid-area: title;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #e9ecef;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 10px;
    min-height: 80px;
}

.gua-title-text {
    font-size: 14px;
    font-weight: bold;
    color: #6c757d;
    line-height: 1.2;
    margin: 0;
}

.gua-position-top { grid-area: top; text-align: center; }
.gua-position-left { grid-area: left; text-align: center; }
.gua-position-center { grid-area: center; text-align: center; }
.gua-position-right { grid-area: right; text-align: center; }
.gua-position-bottom { grid-area: bottom; text-align: center; }

.gua-number {
    width: 60px;
    height: 60px;
    border: 2px solid #333;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    background-color: white;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

# 主應用程式
def main():
    # 1. 狀態初始化
    if 'board_generated' not in st.session_state or not hasattr(st.session_state, 'board_pieces'):
        board = XiangqiBoard()
        st.session_state.board_pieces = board.pieces
        st.session_state.board_generated = True

    # 2. 從URL讀取狀態 (Single Source of Truth)
    params = st.query_params
    revealed_indices = {int(i) for i in params.get_all("r") if i.isdigit()}
    selected_indices = [int(i) for i in params.get_all("s") if i.isdigit()]

    # 3. 根據URL狀態更新衍生資料
    board_pieces = st.session_state.board_pieces
    selected_pieces = [board_pieces[i] for i in selected_indices]
    selected_positions = {}
    position_order = ['center', 'left', 'right', 'top', 'bottom']
    for i, piece in enumerate(selected_pieces):
        selected_positions[position_order[i]] = piece

    # 4. UI 渲染
    st.title("♟️ 象棋卜卦")
    st.markdown("點擊象棋翻面並選擇，探索您的運勢")

    # 如果URL中有參數，說明剛發生過點擊，執行JS滾動到錨點
    if "r" in params or "s" in params:
        st.html(
            '''
            <script>
                window.setTimeout(function() {
                    var anchor = document.getElementById('board-anchor');
                    if (anchor) {
                        anchor.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 100);
            </script>
            '''
        )

    st.markdown("---")

    # 控制按鈕
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🎲 重新生成棋盤", type="primary"):
            generate_board()
            st.rerun()
    with col2:
        if st.button("🧹 清除選擇"):
            st.session_state.divination_result = None # 清除卜卦結果
            st.query_params.clear()
            st.rerun()
    with col3:
        if st.button("🔮 開始卜卦", disabled=len(selected_indices) != 5):
            start_divination(selected_pieces)

    with col4:
        st.metric("已選擇", f"{len(selected_indices)}/5")
    
    st.markdown("---")
    
    # 主要內容區域
    col_board, col_gua = st.columns([2, 1])
    
    with col_board:
        st.markdown('<div id="board-anchor"></div>', unsafe_allow_html=True)
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

                    # --- 產生點擊後的URL ---
                    new_revealed_set = revealed_indices.copy()
                    new_revealed_set.add(index)
                    
                    new_selected_list = selected_indices.copy()
                    if is_selected:
                        new_selected_list.remove(index)
                    elif len(new_selected_list) < 5:
                        new_selected_list.append(index)
                    
                    from urllib.parse import urlencode
                    query_dict = [("r", r_idx) for r_idx in new_revealed_set] + \
                                 [("s", s_idx) for s_idx in new_selected_list]
                    href = f"?{urlencode(query_dict)}"

                    # --- 產生棋子外觀 (Inline CSS) ---
                    style = (
                        "width:60px; height:60px; display:flex; align-items:center; "
                        "justify-content:center; font-weight:bold; text-decoration:none; "
                        "border-radius:50%; margin: 5px auto; transition: all 0.2s ease;"
                    )
                    
                    if is_revealed:
                        color = piece.color
                        if color == Color.RED:
                            style += "background-color:#dc3545; color:white;"
                        else:
                            style += "background-color:#343a40; color:white;"
                    else:
                        style += "background-color:#F5F5DC; color:#F5F5DC;"

                    if is_selected:
                        style += "border: 4px solid #ffc107; box-shadow: 0 0 10px #ffc107;"
                    else:
                        style += "border: 4px solid #888;"

                    label = piece.display_name if is_revealed else "&nbsp;"
                    
                    st.markdown(f'<a href="{href}" style="{style}" target="_self">{label}</a>', unsafe_allow_html=True)

    with col_gua:
        # 使用一個外層欄位來約束整體寬度，讓卦象更集中
        _l, center_col, _r = st.columns([0.5, 2, 0.5])
        with center_col:
            st.subheader("卦象")
            
            # 使用對稱的欄位來控制間距
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

    # 顯示卜卦結果
    if 'divination_result' in st.session_state and st.session_state.divination_result:
        st.divider()
        st.subheader("🔮 卜卦結果")
        result = st.session_state.divination_result
        # ... (顯示結果的剩餘部分保持不變)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("陰陽平衡", "平衡" if result.yin_yang_balance else "不平衡")
        with col2:
            st.metric("平衡分數", f"{result.balance_score}/100")
        with col3:
            red_count = sum(1 for piece in result.selected_pieces if piece.color == Color.RED)
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