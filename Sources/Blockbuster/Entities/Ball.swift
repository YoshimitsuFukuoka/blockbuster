import SpriteKit

final class Ball: SKShapeNode {

    init(radius: CGFloat = GameConfig.ballRadius) {
        super.init()
        let path = CGMutablePath()
        path.addEllipse(in: CGRect(x: -radius, y: -radius, width: radius * 2, height: radius * 2))
        self.path = path
        fillColor = .white
        strokeColor = .clear
        name = "ball"
        setupPhysics(radius: radius)
    }

    required init?(coder aDecoder: NSCoder) { fatalError() }

    private func setupPhysics(radius: CGFloat) {
        physicsBody = SKPhysicsBody(circleOfRadius: radius)
        physicsBody?.isDynamic = true
        physicsBody?.affectedByGravity = false
        physicsBody?.restitution = 1.0
        physicsBody?.friction = 0
        physicsBody?.linearDamping = 0
        physicsBody?.angularDamping = 0
        physicsBody?.allowsRotation = false
        physicsBody?.categoryBitMask = GameConfig.ballCategory
        physicsBody?.contactTestBitMask = GameConfig.paddleCategory | GameConfig.blockCategory | GameConfig.deadZoneCategory
        physicsBody?.collisionBitMask = GameConfig.wallCategory | GameConfig.paddleCategory | GameConfig.blockCategory
    }

    func launch(speed: CGFloat) {
        let angle = CGFloat.random(in: CGFloat.pi / 4 ... 3 * CGFloat.pi / 4)
        let vx = cos(angle) * speed
        let vy = sin(angle) * speed
        physicsBody?.velocity = CGVector(dx: vx, dy: vy)
    }

    func enforceSpeed(_ speed: CGFloat) {
        guard let body = physicsBody else { return }
        let current = hypot(body.velocity.dx, body.velocity.dy)
        guard current > 0 else { return }
        let scale = speed / current
        body.velocity = CGVector(dx: body.velocity.dx * scale, dy: body.velocity.dy * scale)
    }
}
