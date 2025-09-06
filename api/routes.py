from flask import Blueprint, jsonify, request
from models.xiangqi import XiangqiBoard, ChessPiece, PieceType, Color, WuXing
from divination_engine import perform_divination

api = Blueprint('api', __name__)

PIECE_TYPE_MAP = {p.value: p for p in PieceType}
COLOR_MAP = {c.value: c for c in Color}
WU_XING_MAP = {w.value: w for w in WuXing}

def piece_from_dict(d: dict) -> ChessPiece:
    """Helper function to create a ChessPiece from a dictionary."""
    return ChessPiece(
        piece_type=PIECE_TYPE_MAP[d['type']],
        color=COLOR_MAP[d['color']],
        points=d['points'],
        wu_xing=WU_XING_MAP[d['wu_xing']]
    )

@api.route('/board/new', methods=['GET'])
def new_board():
    """
    Generates a new, shuffled Xiangqi board.
    """
    board = XiangqiBoard()
    # The new XiangqiBoard initializes with a shuffled list of 32 pieces.
    # We'll just return the list of pieces.
    return jsonify({
        'pieces': [piece.to_dict() for piece in board.pieces]
    })

@api.route('/divination', methods=['POST'])
def divination():
    """
    Performs divination based on a selection of 5 chess pieces.
    """
    data = request.get_json()
    if not data or 'pieces' not in data:
        return jsonify({'error': 'Missing piece selection'}), 400

    selected_piece_dicts = data['pieces']
    if len(selected_piece_dicts) != 5:
        return jsonify({'error': 'Exactly 5 pieces must be selected'}), 400

    try:
        selected_pieces = [piece_from_dict(p) for p in selected_piece_dicts]
    except (KeyError, TypeError):
        return jsonify({'error': 'Invalid piece data format'}), 400

    result = perform_divination(selected_pieces)
    return jsonify(result.to_dict())
