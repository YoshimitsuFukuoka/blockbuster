import SpriteKit

final class StartScene: SKScene {

    var onStart: (() -> Void)?

    override func didMove(to view: SKView) {
        backgroundColor = UIColor(red: 0.05, green: 0.05, blue: 0.12, alpha: 1)

        let title = SKLabelNode(fontNamed: "AvenirNext-Heavy")
        title.text = "BLOCKBUSTER"
        title.fontSize = 40
        title.fontColor = UIColor(red: 1, green: 0.85, blue: 0.2, alpha: 1)
        title.position = CGPoint(x: size.width / 2, y: size.height * 0.6)
        addChild(title)

        let sub = SKLabelNode(fontNamed: "AvenirNext-Regular")
        sub.text = "ブロック崩し"
        sub.fontSize = 20
        sub.fontColor = UIColor(white: 0.8, alpha: 1)
        sub.position = CGPoint(x: size.width / 2, y: size.height * 0.53)
        addChild(sub)

        let tap = SKLabelNode(fontNamed: "AvenirNext-Bold")
        tap.text = "TAP TO PLAY"
        tap.fontSize = 22
        tap.fontColor = .white
        tap.position = CGPoint(x: size.width / 2, y: size.height * 0.35)
        let pulse = SKAction.sequence([
            SKAction.fadeAlpha(to: 0.3, duration: 0.6),
            SKAction.fadeAlpha(to: 1.0,  duration: 0.6)
        ])
        tap.run(.repeatForever(pulse))
        addChild(tap)
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        onStart?()
    }
}
