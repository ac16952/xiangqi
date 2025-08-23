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

# 自定義CSS樣式
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
    background-color: #dc3545;
    color: white;
}

.chess-piece-black {
    background-color: #343a40;
    color: white;
}

.chess-piece-hidden {
    background-color: #dc3545;
    color: white;
    opacity: 0.8;
}

.chess-piece-selected {
    border: 3px solid #ffc107 !important;
    box-shadow: 0 0 10px #ffc107 !important;
    transform: scale(1.1) !important;
}

.piece-slot {
    width: 80px;
    height: 80px;
    border: 2px dashed #ccc;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    background-color: #f8f9fa;
    transition: all 0.3s ease;
}

.piece-slot-filled {
    border: 2px solid #28a745;
    background-color: #d4edda;
    transform: scale(1.05);
}

/* 棋盤選擇按鈕樣式 */
.stButton > button[key^="btn_"] {
    width: 100%;
    height: 40px;
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
    margin-top: 5px;
}

.stButton > button[key^="btn_"]:hover {
    background: transparent !important;
    border: none !important;
}

.stButton > button[key^="btn_"]:focus {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.stButton > button[key^="btn_"]:active {
    background: transparent !important;
    border: none !important;
}

.gua-display {
    display: grid;
    grid-template-areas: 
        "title top ."
        "left center right"
        ". bottom .";
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

.gua-position-top {
    grid-area: top;
    text-align: center;
}

.gua-position-left {
    grid-area: left;
    text-align: center;
}

.gua-position-center {
    grid-area: center;
    text-align: center;
}

.gua-position-right {
    grid-area: right;
    text-align: center;
}

.gua-position-bottom {
    grid-area: bottom;
    text-align: center;
}

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

.gua-piece {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 16px;
    margin: 0 auto;
    border: 2px solid #333;
}
</style>
""", unsafe_allow_html=True)

# 初始化session state
def init_session_state():
    if 'board_pieces' not in st.session_state:
        st.session_state.board_pieces = []
    if 'revealed_pieces' not in st.session_state:
        st.session_state.revealed_pieces = set()
    if 'selected_pieces' not in st.session_state:
        st.session_state.selected_pieces = []
    if 'selected_indices' not in st.session_state:
        st.session_state.selected_indices = set()
    if 'selected_positions' not in st.session_state:
        st.session_state.selected_positions = {}
    if 'divination_result' not in st.session_state:
        st.session_state.divination_result = None
    if 'board_generated' not in st.session_state:
        st.session_state.board_generated = False

def generate_board():
    """生成隨機棋盤"""
    board = XiangqiBoard()
    st.session_state.board_pieces = board.pieces
    st.session_state.revealed_pieces = set()
    st.session_state.selected_pieces = []
    st.session_state.selected_indices = set()
    st.session_state.selected_positions = {}
    st.session_state.divination_result = None
    st.session_state.board_generated = True

def toggle_piece(index):
    """翻牌並選擇棋子"""
    # 如果已經選擇了5個棋子，或者這個位置已經被選擇過，則不允許再選擇
    if len(st.session_state.selected_pieces) >= 5 or index in st.session_state.selected_indices:
        return
    
    # 立即翻面
    st.session_state.revealed_pieces.add(index)

    piece = st.session_state.board_pieces[index]
    st.session_state.selected_pieces.append(piece)
    st.session_state.selected_indices.add(index)
    
    # 按順序分配位置
    position_order = ['center', 'left', 'right', 'top', 'bottom']
    position = position_order[len(st.session_state.selected_pieces) - 1]
    st.session_state.selected_positions[position] = piece

def clear_selection():
    """清除選擇並重新生成棋盤"""
    st.session_state.selected_pieces = []
    st.session_state.selected_indices = set()
    st.session_state.selected_positions = {}
    st.session_state.revealed_pieces = set()
    st.session_state.divination_result = None
    
    # 重新生成棋盤，讓用戶有新的排列可以選擇
    generate_board()

def start_divination():
    """開始卜卦"""
    if len(st.session_state.selected_pieces) == 5:
        result = perform_divination(st.session_state.selected_pieces)
        st.session_state.divination_result = result

# 主應用程式
def main():
    init_session_state()
    
    # 標題
    st.title("♟️ 象棋卜卦")
    st.markdown("點擊象棋翻面並選擇，探索您的運勢")
    
    # 控制按鈕
    st.markdown("---")  # 添加分隔線
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎲 重新生成棋盤", type="primary", key="btn_generate"):
            generate_board()
            st.rerun()  # 觸發頁面重新渲染
    
    with col2:
        if st.button("🧹 清除選擇", key="btn_clear"):
            clear_selection()
            st.rerun()  # 觸發頁面重新渲染
    
    with col3:
        if st.button("🔮 開始卜卦", disabled=len(st.session_state.selected_pieces) != 5, key="btn_divination"):
            start_divination()
            st.rerun()  # 觸發頁面重新渲染
    
    with col4:
        st.metric("已選擇", f"{len(st.session_state.selected_pieces)}/5")
    
    st.markdown("---")  # 添加分隔線
    
    if not st.session_state.board_generated:
        st.info("請點擊「重新生成棋盤」開始")
        return
    
    # 主要內容區域
    col_board, col_gua = st.columns([2, 1])
    
    with col_board:
        st.subheader("棋盤")
        st.markdown("點擊象棋翻面並選擇（最多5個）")
        
        # 渲染4x8棋盤網格
        for row in range(4):
            cols = st.columns(8)
            for col in range(8):
                index = row * 8 + col
                piece = st.session_state.board_pieces[index]
                is_revealed = index in st.session_state.revealed_pieces
                is_selected = index in st.session_state.selected_indices
                
                with cols[col]:
                    # 創建棋子顯示
                    if is_revealed:
                        color_class = "chess-piece-red" if piece.color == Color.RED else "chess-piece-black"
                        selected_class = " chess-piece-selected" if is_selected else ""
                        st.markdown(f'<div class="chess-piece {color_class}{selected_class}">{piece.display_name}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chess-piece chess-piece-hidden"></div>', unsafe_allow_html=True)
                    
                    # 創建按鈕來處理點擊
                    if st.button("選擇", key=f"btn_{index}", 
                                 disabled=(len(st.session_state.selected_pieces) >= 5 and index not in st.session_state.selected_indices) or index in st.session_state.selected_indices):
                        toggle_piece(index)
                        st.rerun()

    
    with col_gua:
        st.subheader("卦象")
        
        # 使用更緊湊的佈局創建十字形卦象
        # 第一行：空白、上方位置、空白
        col1, col2, col3 = st.columns([0.5, 1, 0.5])
        
        with col1:
            # 左上方空白位置
            st.write("")
        
        with col2:
            # 上方位置 (4)
            top_piece = st.session_state.selected_positions.get('top')
            if top_piece:
                color_class = "chess-piece-red" if top_piece.color == Color.RED else "chess-piece-black"
                st.markdown(f'<div class="chess-piece {color_class}" style="margin: 0 auto;">{top_piece.display_name}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; background-color: white; margin: 0 auto;">4</div>', unsafe_allow_html=True)
        
        with col3:
            # 右上方空白位置
            st.write("")
        
        # 第二行：左邊、中間、右邊 - 使用極緊湊的佈局
        col4, col5, col6 = st.columns([0.8, 1.4, 0.8])
        
        with col4:
            # 左邊位置 (2)
            left_piece = st.session_state.selected_positions.get('left')
            if left_piece:
                color_class = "chess-piece-red" if left_piece.color == Color.RED else "chess-piece-black"
                st.markdown(f'<div class="chess-piece {color_class}" style="margin: 0 auto;">{left_piece.display_name}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; background-color: white; margin: 0 auto;">2</div>', unsafe_allow_html=True)
        
        with col5:
            # 中間位置 (1)
            center_piece = st.session_state.selected_positions.get('center')
            if center_piece:
                color_class = "chess-piece-red" if center_piece.color == Color.RED else "chess-piece-black"
                st.markdown(f'<div class="chess-piece {color_class}" style="margin: 0 auto;">{center_piece.display_name}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; background-color: white; margin: 0 auto;">1</div>', unsafe_allow_html=True)
        
        with col6:
            # 右邊位置 (3)
            right_piece = st.session_state.selected_positions.get('right')
            if right_piece:
                color_class = "chess-piece-red" if right_piece.color == Color.RED else "chess-piece-black"
                st.markdown(f'<div class="chess-piece {color_class}" style="margin: 0 auto;">{right_piece.display_name}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; background-color: white; margin: 0 auto;">3</div>', unsafe_allow_html=True)
        
        # 第三行：空白、下方、空白
        col7, col8, col9 = st.columns([0.5, 1, 0.5])
        
        with col7:
            # 左下方空白位置
            st.write("")
        
        with col8:
            # 下方位置 (5)
            bottom_piece = st.session_state.selected_positions.get('bottom')
            if bottom_piece:
                color_class = "chess-piece-red" if bottom_piece.color == Color.RED else "chess-piece-black"
                st.markdown(f'<div class="chess-piece {color_class}" style="margin: 0 auto;">{bottom_piece.display_name}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width: 60px; height: 60px; border: 2px solid #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; background-color: white; margin: 0 auto;">5</div>', unsafe_allow_html=True)
        
        with col9:
            # 右下方空白位置
            st.write("")
    
    # 顯示卜卦結果
    if st.session_state.divination_result:
        st.divider()
        st.subheader("🔮 卜卦結果")
        
        result = st.session_state.divination_result
        
        # 基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("陰陽平衡", "平衡" if result.yin_yang_balance else "不平衡")
        with col2:
            st.metric("平衡分數", f"{result.balance_score}/100")
        with col3:
            red_count = sum(1 for piece in result.selected_pieces if piece.color == Color.RED)
            st.metric("紅黑比例", f"{red_count}:{5-red_count}")
        
        # 格局分析
        if result.patterns:
            st.subheader("📊 格局分析")
            for pattern in result.patterns:
                st.success(f"✨ {pattern}")
        
        # 三才分析
        if result.missing_talents:
            st.subheader("⚠️ 三才缺失")
            for talent in result.missing_talents:
                st.warning(f"缺少 {talent}")
        
        # 詳細分析
        with st.expander("🎭 呈現狀態", expanded=True):
            st.write(result.analysis['state'])
        
        with st.expander("🤝 互動關係", expanded=True):
            st.write(result.analysis['interaction'])
        
        with st.expander("💰 付出與收穫", expanded=True):
            st.write(result.analysis['give_and_take'])
        
        with st.expander("🏥 健康分析", expanded=True):
            st.write(result.health_analysis)
        
        # 建議
        if result.suggestions:
            st.subheader("💡 建議")
            for i, suggestion in enumerate(result.suggestions, 1):
                st.info(f"{i}. {suggestion}")

if __name__ == "__main__":
    main()

