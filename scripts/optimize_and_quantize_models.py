#!/usr/bin/env python3
"""
VajraNetra — Edge Model Optimization & Quantization Pipeline
Exports and quantizes PyTorch (.pt) models to:
1. FP16 Half-Precision (.pt / .onnx) — 50% VRAM reduction, 2x FPS speedup.
2. ONNX Runtime Engine (.onnx) — Platform-independent high-throughput edge execution.
3. TensorRT Engine (.engine) — Maximum acceleration on NVIDIA Jetson / RTX hardware.
4. OpenVINO IR (.xml / .bin) — Intel NPU / CPU edge optimization.
"""

import os
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "Models"

# Available model weights
MODEL_TARGETS = [
    {
        "name": "PPE Detection (YOLOv8)",
        "path": MODELS_DIR / "PPE-Detection" / "ppe.pt",
        "task": "detect",
    },
    {
        "name": "Fall Detection Pose (YOLOv8s-Pose)",
        "path": MODELS_DIR / "Fall_Detection" / "yolov8s-pose.pt",
        "task": "pose",
    },
    {
        "name": "Fire & Smoke Localization (YOLOv8)",
        "path": MODELS_DIR / "Fire_Smoke" / "last.pt",
        "task": "detect",
    },
    {
        "name": "Skeletal Pose Tracking (YOLOv8)",
        "path": MODELS_DIR / "Pose" / "best.pt",
        "task": "pose",
    },
]


def optimize_models(target_format="onnx", half_precision=True, int8_quant=False):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] Ultralytics package not found. Run: pip install ultralytics onnx onnxruntime")
        return False

    print("=" * 70)
    print("  VAJRANETRA EDGE MODEL QUANTIZATION & OPTIMIZATION PIPELINE")
    print("=" * 70)
    print(f"Target Format    : {target_format.upper()}")
    print(f"Half Precision   : {half_precision} (FP16)")
    print(f"INT8 Quantization: {int8_quant}")
    print("-" * 70)

    success_count = 0
    for target in MODEL_TARGETS:
        model_path = target["path"]
        if not model_path.exists():
            print(f"[SKIP] Model weights not found: {model_path}")
            continue

        print(f"\n[OPTIMIZING] {target['name']} -> {model_path.name}")
        try:
            model = YOLO(str(model_path))
            
            # Export with quantization parameters
            exported_path = model.export(
                format=target_format,
                half=half_precision,
                int8=int8_quant,
                dynamic=False,
                simplify=True,
                opset=12,
            )
            print(f"[SUCCESS] Exported quantized model to: {exported_path}")
            success_count += 1
        except Exception as e:
            print(f"[WARNING] Export skipped for {target['name']}: {e}")

    print("\n" + "=" * 70)
    print(f"Quantization complete! Successfully optimized {success_count} models.")
    print("=" * 70)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VajraNetra Model Quantization Tool")
    parser.add_argument(
        "--format",
        type=str,
        default="onnx",
        choices=["onnx", "engine", "openvino", "torchscript"],
        help="Export target format (default: onnx)",
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        default=True,
        help="Enable FP16 half-precision quantization (default: True)",
    )
    parser.add_argument(
        "--int8",
        action="store_true",
        default=False,
        help="Enable INT8 integer quantization (requires calibration dataset)",
    )

    args = parser.parse_args()
    optimize_models(
        target_format=args.format,
        half_precision=args.fp16,
        int8_quant=args.int8,
    )
