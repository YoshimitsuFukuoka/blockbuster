import SpriteKit

final class GameOverScene: SKScene {

    var onRestart: (() -> Void)?
    private let finalScore: Int

    init(size: CGSize, score: Int) {
        self.finalScore = score
        super.init(size: size)
    }

    required init?(coder aDecoder: NSCoder) { fatalError() }

    override func didMove(to view: SKView) {
        backgroundColor = UIColor(red: 0.05, green: 0.05, blue: 0.12, alpha: 1)

        let over = SKLabelNode(fontNamed: "AvenirNext-Heavy")
        over.text = "GAME OVER"
        over.fontSize = 44
        over.fontColor = UIColor(red: 0.95, green: 0.3, blue: 0.3, alpha: 1)
        over.position = CGPoint(x: size.width / 2, y: size.height * 0.6)
        addChild(over)

        let scoreLbl = SKLabelNode(fontNamed: "AvenirNext-Bold")
        scoreLbl.text = "SCORE: \(finalScore)"
        scoreLbl.fontSize = 28
        scoreLbl.fontColor = .white
        scoreLbl.position = CGPoint(x: size.width / 2, y: size.height * 0.5)
        addChild(scoreLbl)

        let restart = SKLabelNode(fontNamed: "AvenirNext-Bold")
        restart.text = "TAP TO RESTART"
        restart.fontSize = 20
        restart.fontColor = UIColor(white: 0.8, alpha: 1)
        restart.position = CGPoint(x: size.width / 2, y: size.height * 0.35)
        let pulse = SKAction.sequence([
            SKAction.fadeAlpha(to: 0.3, duration: 0.6),
            SKAction.fadeAlpha(to: 1.0,  duration: 0.6)
        ])
        restart.run(.repeatForever(pulse))
        addChild(restart)
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        onRestart?()
    }
}
