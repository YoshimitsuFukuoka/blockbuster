import SpriteKit

final class Block: SKSpriteNode {

    let scoreValue: Int
    private(set) var hp: Int

    init(width: CGFloat = GameConfig.blockWidth,
         height: CGFloat = GameConfig.blockHeight,
         hp: Int = 1,
         color: UIColor,
         scoreValue: Int) {
        self.hp = hp
        self.scoreValue = scoreValue
        super.init(texture: nil, color: color, size: CGSize(width: width, height: height))
        name = "block"
        setupPhysics(width: width, height: height)
    }

    required init?(coder aDecoder: NSCoder) { fatalError() }

    private func setupPhysics(width: CGFloat, height: CGFloat) {
        physicsBody = SKPhysicsBody(rectangleOf: CGSize(width: width, height: height))
        physicsBody?.isDynamic = false
        physicsBody?.restitution = 1.0
        physicsBody?.friction = 0
        physicsBody?.categoryBitMask = GameConfig.blockCategory
        physicsBody?.contactTestBitMask = GameConfig.ballCategory
        physicsBody?.collisionBitMask = GameConfig.ballCategory
    }

    @discardableResult
    func hit() -> Bool {
        hp -= 1
        if hp <= 0 {
            return true
        }
        alpha = CGFloat(hp) / 2.0 + 0.5
        return false
    }

    func spawnBreakEffect(in scene: SKScene) {
        let emitter = SKEmitterNode()
        emitter.particleTexture = SKTexture(imageNamed: "spark")
        emitter.particleBirthRate = 80
        emitter.numParticlesToEmit = 20
        emitter.particleLifetime = 0.4
        emitter.particleSpeed = 80
        emitter.particleSpeedRange = 60
        emitter.emissionAngleRange = .pi * 2
        emitter.particleAlpha = 1
        emitter.particleAlphaSpeed = -2.5
        emitter.particleScale = 0.3
        emitter.particleScaleRange = 0.2
        emitter.particleColor = color
        emitter.position = position
        scene.addChild(emitter)
        let wait = SKAction.wait(forDuration: 0.5)
        let remove = SKAction.removeFromParent()
        emitter.run(.sequence([wait, remove]))
    }
}
