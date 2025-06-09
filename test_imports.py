#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify all required imports for OCT Extractor application
"""

import sys
import os
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Testing PyQt5 imports...")
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon
    logger.info("PyQt5 imports successful")
except ImportError as e:
    logger.error(f"PyQt5 import error: {e}")
    sys.exit(1)

try:
    logger.info("Testing oct-converter imports...")
    from oct_converter.readers import E2E, IMG
    from oct_converter.dicom import create_dicom_from_oct
    logger.info("OCT-Converter imports successful")
except ImportError as e:
    logger.error(f"OCT-Converter import error: {e}")
    sys.exit(1)

try:
    logger.info("Testing other dependencies...")
    import numpy as np
    from PIL import Image
    import io
    import json
    import h5py
    import matplotlib
    logger.info("All other imports successful")
except ImportError as e:
    logger.error(f"Dependency import error: {e}")
    sys.exit(1)

logger.info("All imports verified successfully!")
print("All required modules imported successfully!")
