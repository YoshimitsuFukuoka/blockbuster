import Foundation
import Combine

final class GameState: ObservableObject {
    @Published var score: Int = 0
    @Published var lives: Int = GameConfig.initialLives
    @Published var level: Int = 1

    var isGameOver: Bool { lives <= 0 }

    func reset() {
        score = 0
        lives = GameConfig.initialLives
        level = 1
    }

    func addScore(_ points: Int) {
        score += points
    }

    func loseLife() {
        lives = max(0, lives - 1)
    }

    func nextLevel() {
        level += 1
    }

    var ballSpeed: CGFloat {
        GameConfig.ballInitialSpeed + CGFloat(level - 1) * GameConfig.ballSpeedIncrement
    }
}
