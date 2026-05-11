import SpriteKit

protocol GameSceneDelegate: AnyObject {
    func gameSceneDidGameOver(score: Int)
}

final class GameScene: SKScene, SKPhysicsContactDelegate {

    weak var gameDelegate: GameSceneDelegate?

    private let state = GameState()
    private var ball: Ball!
    private var paddle: Paddle!
    private var hud: HUD!
    private var blocks: [Block] = []
    private var ballIsLaunched = false
    private var isResetting = false

    // MARK: - Lifecycle

    override func didMove(to view: SKView) {
        backgroundColor = UIColor(red: 0.05, green: 0.05, blue: 0.12, alpha: 1)
        physicsWorld.gravity = .zero
        physicsWorld.contactDelegate = self
        physicsWorld.speed = 1.0

        setupScene()
    }

    // MARK: - Setup

    private func setupScene() {
        removeAllChildren()
        blocks = []
        ballIsLaunched = false
        isResetting = false

        WallFactory.makeWalls(in: self)
        setupPaddle()
        setupBall()
        setupBlocks()
        setupHUD()
        showTapToStart()
    }

    private func setupPaddle() {
        paddle = Paddle()
        paddle.position = CGPoint(x: size.width / 2,
                                  y: GameConfig.paddleBottomMargin)
        addChild(paddle)
    }

    private func setupBall() {
        ball = Ball()
        ball.position = CGPoint(x: size.width / 2,
                                y: GameConfig.paddleBottomMargin + GameConfig.paddleHeight / 2 + GameConfig.ballRadius + 2)
        addChild(ball)
    }

    private func setupBlocks() {
        let newBlocks = BlockLayout.makeBlocks(forLevel: state.level)
        BlockLayout.place(blocks: newBlocks, in: self, level: state.level)
        blocks = newBlocks
    }

    private func setupHUD() {
        hud = HUD()
        hud.layout(in: size)
        addChild(hud)
        refreshHUD()
    }

    private func refreshHUD() {
        hud.update(score: state.score, lives: state.lives, level: state.level)
    }

    // MARK: - Tap to start overlay

    private func showTapToStart() {
        let label = SKLabelNode(fontNamed: "AvenirNext-Bold")
        label.text = "TAP TO LAUNCH"
        label.fontSize = 20
        label.fontColor = UIColor(white: 1, alpha: 0.8)
        label.position = CGPoint(x: size.width / 2, y: size.height * 0.35)
        label.name = "tapLabel"
        label.zPosition = 50
        let pulse = SKAction.sequence([
            SKAction.fadeAlpha(to: 0.3, duration: 0.7),
            SKAction.fadeAlpha(to: 1.0,  duration: 0.7)
        ])
        label.run(.repeatForever(pulse))
        addChild(label)
    }

    // MARK: - Touch handling

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        movePaddle(to: touch)

        if !ballIsLaunched {
            childNode(withName: "tapLabel")?.removeFromParent()
            ball.launch(speed: state.ballSpeed)
            ballIsLaunched = true
        }
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        movePaddle(to: touch)
    }

    private func movePaddle(to touch: UITouch) {
        let x = touch.location(in: self).x
        paddle.move(toX: x, sceneWidth: size.width)
        if !ballIsLaunched {
            ball.position.x = x
        }
    }

    // MARK: - Game loop

    override func update(_ currentTime: TimeInterval) {
        guard ballIsLaunched, !isResetting else { return }
        ball.enforceSpeed(state.ballSpeed)
    }

    // MARK: - Collision handling

    func didBegin(_ contact: SKPhysicsContact) {
        let a = contact.bodyA
        let b = contact.bodyB

        if hits(a, b, category: GameConfig.deadZoneCategory) {
            handleBallLost()
            return
        }

        if hits(a, b, category: GameConfig.blockCategory) {
            let blockBody = a.categoryBitMask == GameConfig.blockCategory ? a : b
            if let block = blockBody.node as? Block {
                handleBlockHit(block)
            }
        }
    }

    private func hits(_ a: SKPhysicsBody, _ b: SKPhysicsBody, category: UInt32) -> Bool {
        (a.categoryBitMask | b.categoryBitMask) & category != 0
    }

    private func handleBlockHit(_ block: Block) {
        guard block.parent != nil else { return }
        let destroyed = block.hit()
        if destroyed {
            state.addScore(block.scoreValue)
            block.spawnBreakEffect(in: self)
            block.removeFromParent()
            blocks.removeAll { $0 === block }
            refreshHUD()
            checkLevelClear()
        }
    }

    private func handleBallLost() {
        guard !isResetting else { return }
        isResetting = true
        ball.physicsBody?.velocity = .zero
        state.loseLife()
        refreshHUD()

        if state.isGameOver {
            triggerGameOver()
        } else {
            run(.wait(forDuration: 0.8)) { [weak self] in
                self?.resetBall()
            }
        }
    }

    private func resetBall() {
        ball.position = CGPoint(x: paddle.position.x,
                                y: GameConfig.paddleBottomMargin + GameConfig.paddleHeight / 2 + GameConfig.ballRadius + 2)
        ballIsLaunched = false
        isResetting = false
        showTapToStart()
    }

    // MARK: - Level clear

    private func checkLevelClear() {
        guard blocks.isEmpty else { return }
        isResetting = true
        ball.physicsBody?.velocity = .zero

        let label = SKLabelNode(fontNamed: "AvenirNext-Bold")
        label.text = "LEVEL CLEAR!"
        label.fontSize = 36
        label.fontColor = UIColor(red: 1, green: 0.85, blue: 0.2, alpha: 1)
        label.position = CGPoint(x: size.width / 2, y: size.height / 2)
        label.zPosition = 50
        addChild(label)

        run(.wait(forDuration: 1.5)) { [weak self] in
            guard let self else { return }
            label.removeFromParent()
            self.state.nextLevel()
            self.setupBlocks()
            self.resetBall()
        }
    }

    // MARK: - Game over

    private func triggerGameOver() {
        run(.wait(forDuration: 0.5)) { [weak self] in
            guard let self else { return }
            self.gameDelegate?.gameSceneDidGameOver(score: self.state.score)
        }
    }

    // MARK: - Restart

    func restart() {
        state.reset()
        setupScene()
    }
}
