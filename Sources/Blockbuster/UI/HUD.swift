import SpriteKit

final class HUD: SKNode {

    private let scoreLabel = SKLabelNode(fontNamed: "AvenirNext-Bold")
    private let livesLabel  = SKLabelNode(fontNamed: "AvenirNext-Bold")
    private let levelLabel  = SKLabelNode(fontNamed: "AvenirNext-Bold")

    override init() {
        super.init()
        zPosition = 100

        configure(scoreLabel, text: "SCORE: 0")
        configure(livesLabel,  text: "LIVES: 3")
        configure(levelLabel,  text: "LV 1")
    }

    required init?(coder aDecoder: NSCoder) { fatalError() }

    private func configure(_ label: SKLabelNode, text: String) {
        label.text = text
        label.fontSize = 14
        label.fontColor = .white
        addChild(label)
    }

    func layout(in size: CGSize) {
        let y = size.height - 30
        scoreLabel.position = CGPoint(x: size.width * 0.2, y: y)
        livesLabel.position  = CGPoint(x: size.width * 0.5,  y: y)
        levelLabel.position  = CGPoint(x: size.width * 0.8, y: y)
    }

    func update(score: Int, lives: Int, level: Int) {
        scoreLabel.text = "SCORE: \(score)"
        livesLabel.text  = "LIVES: \(lives)"
        levelLabel.text  = "LV \(level)"
    }
}
