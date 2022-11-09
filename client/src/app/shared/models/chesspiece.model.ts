type ChessPiece = {
    image: string,
    is_white: boolean
} | undefined

enum ChessPieceName {
    PAWN = "pawn",
    ROOK = "rook",
    KNIGHT = "knight",
    BISHOP = "bishop",
    QUEEN = "queen",
    KING = "king"
}

const ChessPieces = {
    PAWN_BLACK: get_chesspiece(ChessPieceName.PAWN, false),
    ROOK_BLACK: get_chesspiece(ChessPieceName.ROOK, false),
    KNIGHT_BLACK: get_chesspiece(ChessPieceName.KNIGHT, false),
    BISHOP_BLACK: get_chesspiece(ChessPieceName.BISHOP, false),
    QUEEN_BLACK: get_chesspiece(ChessPieceName.QUEEN, false),
    KING_BLACK: get_chesspiece(ChessPieceName.KING, false),
    PAWN_WHITE: get_chesspiece(ChessPieceName.PAWN, true),
    ROOK_WHITE: get_chesspiece(ChessPieceName.ROOK, true),
    KNIGHT_WHITE: get_chesspiece(ChessPieceName.KNIGHT, true),
    BISHOP_WHITE: get_chesspiece(ChessPieceName.BISHOP, true),
    QUEEN_WHITE: get_chesspiece(ChessPieceName.QUEEN, true),
    KING_WHITE: get_chesspiece(ChessPieceName.KING, true)
}

function get_chesspiece(name: ChessPieceName, is_white: boolean): ChessPiece {
    return {
        image: `assets/${name}_${is_white ? "white" : "black"}.png`,
        is_white: is_white
    }
}

export const DEFAULT_CHESSBOARD: (ChessPiece[])[] =
    [
        [
            ChessPieces.ROOK_BLACK,
            ChessPieces.BISHOP_BLACK,
            ChessPieces.KNIGHT_BLACK,
            ChessPieces.QUEEN_BLACK,
            ChessPieces.KING_BLACK,
            ChessPieces.KNIGHT_BLACK,
            ChessPieces.BISHOP_BLACK,
            ChessPieces.ROOK_BLACK,
        ],
        [
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK,
            ChessPieces.PAWN_BLACK
        ],
        [undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined],
        [undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined],
        [undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined],
        [undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined],
        [
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE,
            ChessPieces.PAWN_WHITE
        ],
        [
            ChessPieces.ROOK_WHITE,
            ChessPieces.BISHOP_WHITE,
            ChessPieces.KNIGHT_WHITE,
            ChessPieces.QUEEN_WHITE,
            ChessPieces.KING_WHITE,
            ChessPieces.KNIGHT_WHITE,
            ChessPieces.BISHOP_WHITE,
            ChessPieces.ROOK_WHITE
        ]
    ]