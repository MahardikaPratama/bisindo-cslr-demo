"""
Script to download model weights
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def download_model():
    """
    Download baseline_model_bisindo.pt
    
    Note: For Phase 1, this is a placeholder.
    In production, this would download from S3, Google Cloud, or GitHub Releases.
    """
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / "baseline_model_bisindo.pt"
    
    if model_path.exists():
        print(f"✓ Model already exists at {model_path}")
        return
    
    print("📥 Downloading baseline_model_bisindo.pt...")
    print("Note: Model download not yet implemented.")
    print("Please manually place the model file at: ", model_path)


def create_gloss_dict():
    """
    Create placeholder gloss dictionary
    
    In production, this would be generated from training data.
    """
    configs_dir = Path(__file__).parent.parent / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    
    gloss_dict_path = configs_dir / "bisindo_gloss_dict.json"
    
    if gloss_dict_path.exists():
        print(f"✓ Gloss dictionary exists at {gloss_dict_path}")
        return
    
    # Create placeholder
    gloss_dict = {
        "id2gloss": {
            "0": {"gloss": "<blank>", "frequency": 0},
            "1": {"gloss": "placeholder_1", "frequency": 1},
        },
        "gloss2id": {
            "<blank>": {"index": 0, "frequency": 0},
            "placeholder_1": {"index": 1, "frequency": 1},
        }
    }
    
    with open(gloss_dict_path, 'w', encoding='utf-8') as f:
        json.dump(gloss_dict, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Created placeholder gloss dictionary at {gloss_dict_path}")


if __name__ == "__main__":
    print("BISINDO CSLR Demo - Setup Script")
    print("=" * 50)
    
    download_model()
    create_gloss_dict()
    
    print("\n✅ Setup complete!")
    print("Next steps:")
    print("  1. Place baseline_model_bisindo.pt in models/ directory")
    print("  2. Run: python -m uvicorn app.main:app --reload")
