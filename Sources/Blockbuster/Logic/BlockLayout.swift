import SpriteKit

enum BlockLayout {

    struct BlockDescriptor {
        let column: Int
        let row: Int
        let hp: Int
        let color: UIColor
        let score: Int
    }

    static func descriptors(forLevel level: Int) -> [BlockDescriptor] {
        let rows = min(GameConfig.blockRows + (level - 1), 10)
        let cols = GameConfig.blockColumns
        var result: [BlockDescriptor] = []

        for row in 0 ..< rows {
            let hp: Int
            let score: Int
            let color: UIColor
            switch row {
            case 0:
                hp = level >= 3 ? 2 : 1
                color = UIColor(red: 0.95, green: 0.3,  blue: 0.3,  alpha: 1)
                score = 30
            case 1:
                hp = 1
                color = UIColor(red: 0.95, green: 0.65, blue: 0.1,  alpha: 1)
                score = 20
            case 2:
                hp = 1
                color = UIColor(red: 0.3,  green: 0.85, blue: 0.35, alpha: 1)
                score = 15
            case 3:
                hp = 1
                color = UIColor(red: 0.3,  green: 0.6,  blue: 0.95, alpha: 1)
                score = 10
            default:
                hp = 1
                color = UIColor(red: 0.75, green: 0.35, blue: 0.9,  alpha: 1)
                score = 5
            }
            for col in 0 ..< cols {
                result.append(BlockDescriptor(column: col, row: row, hp: hp, color: color, score: score))
            }
        }
        return result
    }

    static func place(blocks: [Block], in scene: SKScene, level: Int) {
        let sceneWidth = scene.size.width
        let totalWidth = CGFloat(GameConfig.blockColumns) * (GameConfig.blockWidth + GameConfig.blockHorizontalSpacing)
                         - GameConfig.blockHorizontalSpacing
        let startX = (sceneWidth - totalWidth) / 2 + GameConfig.blockWidth / 2

        for (index, block) in blocks.enumerated() {
            let desc = descriptors(forLevel: level)[index]
            let x = startX + CGFloat(desc.column) * (GameConfig.blockWidth + GameConfig.blockHorizontalSpacing)
            let y = scene.size.height - GameConfig.blockTopMargin
                    - CGFloat(desc.row) * (GameConfig.blockHeight + GameConfig.blockVerticalSpacing)
            block.position = CGPoint(x: x, y: y)
            scene.addChild(block)
        }
    }

    static func makeBlocks(forLevel level: Int) -> [Block] {
        return descriptors(forLevel: level).map { desc in
            Block(hp: desc.hp, color: desc.color, scoreValue: desc.score)
        }
    }
}
