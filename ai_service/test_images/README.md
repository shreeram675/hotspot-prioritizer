# AI Severity Analysis - Test Images Directory

This directory contains test images for verifying the AI garbage severity analysis system.

## Expected Test Images

Create or place the following images in this directory:

1. **clean_street.jpg** - Clean street scene
   - Expected: Clean (0-20 score)
   - Should have minimal to no garbage

2. **light_litter.jpg** - Light litter
   - Expected: Low (21-40 score)
   - Few scattered items, low coverage

3. **moderate_garbage.jpg** - Moderate garbage accumulation
   - Expected: Medium (41-60 score)
   - Visible garbage, moderate coverage

4. **heavy_garbage.jpg** - Heavy garbage
   - Expected: High (61-80 score)
   - Significant accumulation, high coverage

5. **extreme_dump.jpg** - Extreme dump/overflow
   - Expected: Extreme (81-100 score)
   - Open dump or severe overflow conditions

## Usage

These images are used by `verify_severity_analysis.py` to test the AI service endpoints.

## Creating Test Images

You can:
1. Use real photos from your device
2. Download sample images from public datasets (TACO, TrashNet)
3. Use AI image generation tools to create test scenarios
4. Take photos specifically for testing

Ensure images are in JPEG or PNG format.
