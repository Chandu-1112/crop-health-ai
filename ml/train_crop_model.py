"""Train the crop-health image classifier.

Dataset layout (one directory per class):
    dataset/
      Tomato__Early_blight/
      Tomato__Late_blight/
      ...

Each disease directory must contain labeled JPG/PNG images. The crop is
included in the class name so the mobile app can restrict predictions to the
selected crop.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms


CLASSES = [
    "Tomato__Early_blight",
    "Tomato__Late_blight",
    "Tomato__Bacterial_spot",
    "Tomato__Leaf_mold",
    "Rice__Blast",
    "Rice__Brown_spot",
    "Rice__Bacterial_leaf_blight",
    "Cotton__Bacterial_blight",
    "Cotton__Bollworm_damage",
    "Chilli__Leaf_curl",
    "Chilli__Powdery_mildew",
    "Chilli__Thrips_damage",
    "Groundnut__Tikka_leaf_spot",
    "Groundnut__Rust",
]


def build_model() -> nn.Module:
    model = models.mobilenet_v3_small(weights="DEFAULT")
    model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(CLASSES))
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("artifacts/crop_health.pt"))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    dataset = datasets.ImageFolder(args.data, transform=transform)
    expected = set(CLASSES)
    actual = set(dataset.classes)
    if actual != expected:
        raise ValueError(
            "Dataset classes do not match the 14 supported classes. "
            f"Missing: {sorted(expected - actual)}; unexpected: {sorted(actual - expected)}"
        )

    train_size = max(1, int(len(dataset) * 0.8))
    val_size = len(dataset) - train_size
    if val_size == 0:
        raise ValueError("Each class needs enough images to create a validation split.")
    train_set, val_set = random_split(dataset, [train_size, val_size])
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(args.epochs):
        model.train()
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                predictions = model(images.to(device)).argmax(dim=1).cpu()
                correct += int((predictions == labels).sum())
                total += labels.numel()
        print(f"epoch={epoch + 1}/{args.epochs} validation_accuracy={correct / total:.3f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.cpu().state_dict(), "classes": dataset.classes}, args.output)
    args.output.with_suffix(".json").write_text(
        json.dumps({"classes": dataset.classes, "image_size": 224}, indent=2),
        encoding="utf-8",
    )
    print(f"saved={args.output}")


if __name__ == "__main__":
    main()
