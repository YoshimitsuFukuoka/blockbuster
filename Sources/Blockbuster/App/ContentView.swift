import SwiftUI
import SpriteKit

struct ContentView: View {

    var body: some View {
        GeometryReader { geo in
            SpriteView(scene: RootScene(size: geo.size))
                .ignoresSafeArea()
        }
    }
}

// RootScene manages the start → game → game-over flow via SKView.presentScene
final class RootScene: SKScene {

    override init(size: CGSize) {
        super.init(size: size)
        scaleMode = .resizeFill
    }

    required init?(coder aDecoder: NSCoder) { fatalError() }

    override func didMove(to view: SKView) {
        presentStart()
    }

    private func presentStart() {
        let start = StartScene(size: size)
        start.scaleMode = .resizeFill
        start.onStart = { [weak self] in self?.presentGame() }
        view?.presentScene(start, transition: .fade(withDuration: 0.3))
    }

    private func presentGame() {
        let game = GameScene(size: size)
        game.scaleMode = .resizeFill
        game.gameDelegate = self
        view?.presentScene(game, transition: .fade(withDuration: 0.3))
    }

    private func presentGameOver(score: Int) {
        let over = GameOverScene(size: size, score: score)
        over.scaleMode = .resizeFill
        over.onRestart = { [weak self] in self?.presentGame() }
        view?.presentScene(over, transition: .fade(withDuration: 0.5))
    }
}

extension RootScene: GameSceneDelegate {
    func gameSceneDidGameOver(score: Int) {
        presentGameOver(score: score)
    }
}
