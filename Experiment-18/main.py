
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from PIL import Image
from torchvision.models import VGG19_Weights
import copy
import io

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMAGE_SIZE = 256


def load_image(image, size=IMAGE_SIZE):
    """Resize an image and convert it to a normalized tensor."""
    if isinstance(image, bytes):
        image = Image.open(io.BytesIO(image))

    image = image.convert("RGB")

    transform = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    return transform(image).unsqueeze(0).to(DEVICE)


def gram_matrix(tensor):
    """Calculate the Gram matrix for style representation."""
    batch, channels, height, width = tensor.size()

    features = tensor.view(channels, height * width)
    gram = torch.mm(features, features.t())

    return gram / (channels * height * width)


def get_features(image, model):
    """Extract content and style features from VGG19."""
    style_layers = {
        "0": "style1",
        "5": "style2",
        "10": "style3",
        "19": "style4",
        "28": "style5"
    }

    content_layers = {
        "21": "content"
    }

    features = {}
    x = image

    for name, layer in model._modules.items():
        x = layer(x)

        if name in style_layers:
            features[style_layers[name]] = x

        if name in content_layers:
            features[content_layers[name]] = x

    return features


def generate_stylized_image(
    content_image,
    style_image,
    steps=50,
    style_weight=1000000,
    content_weight=1
):
    """Generate an image combining content and artistic style."""

    content = load_image(content_image)
    style = load_image(style_image)

    weights = VGG19_Weights.DEFAULT
    vgg = models.vgg19(weights=weights).features.to(DEVICE).eval()

    for parameter in vgg.parameters():
        parameter.requires_grad_(False)

    # Extract target features without calculating gradients.
    with torch.no_grad():
        content_features = get_features(content, vgg)
        style_features = get_features(style, vgg)

        style_grams = {
            layer: gram_matrix(style_features[layer])
            for layer in style_features
            if layer.startswith("style")
        }

    # Start with the content image and gradually optimize it.
    generated = content.clone().requires_grad_(True)

    optimizer = optim.Adam([generated], lr=0.02)

    for step in range(steps):
        optimizer.zero_grad()

        generated_features = get_features(generated, vgg)

        content_loss = torch.mean(
            (generated_features["content"] -
             content_features["content"]) ** 2
        )

        style_loss = torch.tensor(0.0, device=DEVICE)

        for layer, target_gram in style_grams.items():
            generated_gram = gram_matrix(generated_features[layer])

            style_loss = style_loss + torch.mean(
                (generated_gram - target_gram) ** 2
            )

        total_loss = (
            content_weight * content_loss
            + style_weight * style_loss
        )

        total_loss.backward()
        optimizer.step()

        # Keep normalized pixel values within a reasonable range.
        with torch.no_grad():
            generated.clamp_(-2.5, 2.5)

    # Convert normalized tensor back into a displayable image.
    mean = torch.tensor(
        [0.485, 0.456, 0.406], device=DEVICE
    ).view(1, 3, 1, 1)

    std = torch.tensor(
        [0.229, 0.224, 0.225], device=DEVICE
    ).view(1, 3, 1, 1)

    with torch.no_grad():
        result = generated.detach() * std + mean
        result = result.clamp(0, 1)
        result = result.squeeze(0).cpu()

    return transforms.ToPILImage()(result)
