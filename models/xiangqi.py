"""
象棋卜卦模型定義
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
import random

class PieceType(Enum):
    """棋子類型"""
    GENERAL = "將"  # 將/帥
    ADVISOR = "士"  # 士/仕
    ELEPHANT = "象"  # 象/相
    CHARIOT = "車"  # 車/俥
    HORSE = "馬"    # 馬/傌
    CANNON = "包"   # 包/炮
    SOLDIER = "兵"  # 兵/卒

class Color(Enum):
    """棋子顏色"""
    RED = "red"
    BLACK = "black"

class WuXing(Enum):
    """五行"""
    WOOD = "木"    # 車、馬
    FIRE = "火"    # 象
    EARTH = "土"   # 士、兵
    METAL = "金"   # 將、士
    WATER = "水"   # 包

@dataclass
class ChessPiece:
    """象棋棋子"""
    piece_type: PieceType
    color: Color
    points: int
    wu_xing: WuXing
    
    @property
    def display_name(self) -> str:
        """顯示名稱"""
        if self.color == Color.RED:
            names = {
                PieceType.GENERAL: "帥",
                PieceType.ADVISOR: "仕", 
                PieceType.ELEPHANT: "相",
                PieceType.CHARIOT: "俥",
                PieceType.HORSE: "傌",
                PieceType.CANNON: "炮",
                PieceType.SOLDIER: "兵"
            }
        else:
            names = {
                PieceType.GENERAL: "將",
                PieceType.ADVISOR: "士",
                PieceType.ELEPHANT: "象", 
                PieceType.CHARIOT: "車",
                PieceType.HORSE: "馬",
                PieceType.CANNON: "包",
                PieceType.SOLDIER: "卒"
            }
        return names[self.piece_type]

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'type': self.piece_type.value,
            'color': self.color.value,
            'display_name': self.display_name,
            'points': self.points,
            'wu_xing': self.wu_xing.value
        }

class XiangqiBoard:
    """象棋棋盤"""
    
    # 棋子定義
    PIECE_DEFINITIONS = [
        # 將/帥
        (PieceType.GENERAL, Color.RED, 80, WuXing.METAL),
        (PieceType.GENERAL, Color.BLACK, 80, WuXing.METAL),
        
        # 士/仕 (每方2個)
        (PieceType.ADVISOR, Color.RED, 60, WuXing.METAL),
        (PieceType.ADVISOR, Color.RED, 60, WuXing.METAL),
        (PieceType.ADVISOR, Color.BLACK, 60, WuXing.METAL),
        (PieceType.ADVISOR, Color.BLACK, 60, WuXing.METAL),
        
        # 象/相 (每方2個)
        (PieceType.ELEPHANT, Color.RED, 40, WuXing.FIRE),
        (PieceType.ELEPHANT, Color.RED, 40, WuXing.FIRE),
        (PieceType.ELEPHANT, Color.BLACK, 40, WuXing.FIRE),
        (PieceType.ELEPHANT, Color.BLACK, 40, WuXing.FIRE),
        
        # 車/俥 (每方2個)
        (PieceType.CHARIOT, Color.RED, 30, WuXing.WOOD),
        (PieceType.CHARIOT, Color.RED, 30, WuXing.WOOD),
        (PieceType.CHARIOT, Color.BLACK, 30, WuXing.WOOD),
        (PieceType.CHARIOT, Color.BLACK, 30, WuXing.WOOD),
        
        # 馬/傌 (每方2個)
        (PieceType.HORSE, Color.RED, 20, WuXing.WOOD),
        (PieceType.HORSE, Color.RED, 20, WuXing.WOOD),
        (PieceType.HORSE, Color.BLACK, 20, WuXing.WOOD),
        (PieceType.HORSE, Color.BLACK, 20, WuXing.WOOD),
        
        # 包/炮 (每方2個)
        (PieceType.CANNON, Color.RED, 15, WuXing.WATER),
        (PieceType.CANNON, Color.RED, 15, WuXing.WATER),
        (PieceType.CANNON, Color.BLACK, 15, WuXing.WATER),
        (PieceType.CANNON, Color.BLACK, 15, WuXing.WATER),
        
        # 兵/卒 (每方5個)
        (PieceType.SOLDIER, Color.RED, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.RED, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.RED, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.RED, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.RED, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.BLACK, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.BLACK, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.BLACK, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.BLACK, 10, WuXing.EARTH),
        (PieceType.SOLDIER, Color.BLACK, 10, WuXing.EARTH),
    ]
    
    def __init__(self):
        self.pieces = self._create_pieces()
        self._randomize_pieces()
    
    def _create_pieces(self) -> List[ChessPiece]:
        """創建所有棋子"""
        pieces = []
        for piece_type, color, points, wu_xing in self.PIECE_DEFINITIONS:
            pieces.append(ChessPiece(piece_type, color, points, wu_xing))
        return pieces
    
    def _randomize_pieces(self):
        """隨機化棋子順序"""
        random.shuffle(self.pieces)
    
    def _generate_random_board(self) -> List[List[ChessPiece]]:
        """生成隨機4x8棋盤（保持向後兼容）"""
        board = []
        for row in range(4):
            board_row = []
            for col in range(8):
                index = row * 8 + col
                board_row.append(self.pieces[index])
            board.append(board_row)
        
        return board
    
    def get_piece_at(self, row: int, col: int) -> ChessPiece:
        """獲取指定位置的棋子"""
        return self.board[row][col]
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        board_data = []
        for row in range(4):
            row_data = []
            for col in range(8):
                piece = self.board[row][col]
                piece_data = piece.to_dict()
                piece_data['position'] = {'row': row, 'col': col}
                row_data.append(piece_data)
            board_data.append(row_data)
        
        return {
            'board': board_data,
            'total_pieces': 32
        }

@dataclass
class DivinationResult:
    """卜卦結果"""
    selected_pieces: List[ChessPiece]
    positions: Dict[str, int]  # center, left, right, top, bottom -> piece index
    yin_yang_balance: bool
    balance_score: int
    missing_talents: List[str]  # 缺失的三才
    patterns: List[str]  # 符合的格局
    analysis: Dict[str, str]  # 各項分析結果
    health_analysis: str
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'selected_pieces': [piece.to_dict() for piece in self.selected_pieces],
            'positions': self.positions,
            'yin_yang_balance': self.yin_yang_balance,
            'balance_score': self.balance_score,
            'missing_talents': self.missing_talents,
            'patterns': self.patterns,
            'analysis': self.analysis,
            'health_analysis': self.health_analysis,
            'suggestions': self.suggestions
        }

