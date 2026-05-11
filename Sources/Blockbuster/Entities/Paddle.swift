import SpriteKit

final class Paddle: SKShapeNode {

    init(width: CGFloat = GameConfig.paddleWidth, height: CGFloat = GameConfig.paddleHeight) {
        super.init()
        let rect = CGRect(x: -width / 2, y: -height / 2, width: width, height: height)
        path = UIBezierPath(roundedRect: rect, cornerRadius: GameConfig.paddleCornerRadius).cgPath
        fillColor = UIColor(red: 0.3, green: 0.7, blue: 1.0, alpha: 1.0)
        strokeColor = .clear
        name = "paddle"
        setupPhysics(width: width, height: height)
    }

    required init?(coder aDecoder: NSCoder) { fatalError() }

    private func setupPhysics(width: CGFloat, height: CGFloat) {
        physicsBody = SKPhysicsBody(rectangleOf: CGSize(width: width, height: height))
        physicsBody?.isDynamic = false
        physicsBody?.restitution = 0
        physicsBody?.friction = 0
        physicsBody?.categoryBitMask = GameConfig.paddleCategory
        physicsBody?.collisionBitMask = GameConfig.ballCategory
    }

    func move(toX x: CGFloat, sceneWidth: CGFloat) {
        let halfWidth = (path.boundingBox.width) / 2
        let clamped = max(halfWidth, min(sceneWidth - halfWidth, x))
        position.x = clamped
    }
}
