import SpriteKit

enum WallFactory {
    static func makeWalls(in scene: SKScene) {
        let size = scene.size

        // Top wall
        addWall(to: scene,
                rect: CGRect(x: 0, y: size.height - 2, width: size.width, height: 2))
        // Left wall
        addWall(to: scene,
                rect: CGRect(x: 0, y: 0, width: 2, height: size.height))
        // Right wall
        addWall(to: scene,
                rect: CGRect(x: size.width - 2, y: 0, width: 2, height: size.height))

        // Dead zone (bottom – triggers life loss)
        let deadZone = SKNode()
        deadZone.position = CGPoint(x: size.width / 2, y: -1)
        let deadBody = SKPhysicsBody(rectangleOf: CGSize(width: size.width, height: 2))
        deadBody.isDynamic = false
        deadBody.categoryBitMask = GameConfig.deadZoneCategory
        deadBody.contactTestBitMask = GameConfig.ballCategory
        deadBody.collisionBitMask = 0
        deadZone.physicsBody = deadBody
        deadZone.name = "deadZone"
        scene.addChild(deadZone)
    }

    private static func addWall(to scene: SKScene, rect: CGRect) {
        let node = SKNode()
        node.position = .zero
        let body = SKPhysicsBody(edgeLoopFrom: rect)
        body.isDynamic = false
        body.friction = 0
        body.restitution = 1.0
        body.categoryBitMask = GameConfig.wallCategory
        body.collisionBitMask = GameConfig.ballCategory
        node.physicsBody = body
        scene.addChild(node)
    }
}
