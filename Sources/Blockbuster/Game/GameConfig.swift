import CoreGraphics

enum GameConfig {
    // Ball
    static let ballRadius: CGFloat = 10
    static let ballInitialSpeed: CGFloat = 400
    static let ballSpeedIncrement: CGFloat = 30

    // Paddle
    static let paddleWidth: CGFloat = 100
    static let paddleHeight: CGFloat = 16
    static let paddleBottomMargin: CGFloat = 60
    static let paddleCornerRadius: CGFloat = 8

    // Block grid
    static let blockColumns: Int = 8
    static let blockRows: Int = 5
    static let blockWidth: CGFloat = 40
    static let blockHeight: CGFloat = 18
    static let blockHorizontalSpacing: CGFloat = 4
    static let blockVerticalSpacing: CGFloat = 6
    static let blockTopMargin: CGFloat = 120

    // Gameplay
    static let initialLives: Int = 3

    // Physics categories
    static let ballCategory:    UInt32 = 0x1 << 0
    static let paddleCategory:  UInt32 = 0x1 << 1
    static let blockCategory:   UInt32 = 0x1 << 2
    static let wallCategory:    UInt32 = 0x1 << 3
    static let deadZoneCategory: UInt32 = 0x1 << 4
}
