// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Blockbuster",
    platforms: [.iOS(.v16)],
    targets: [
        .executableTarget(
            name: "Blockbuster",
            path: "Sources/Blockbuster",
            resources: [.process("../../Resources")]
        )
    ]
)
