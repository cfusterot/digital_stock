# Digital Stock: Negative Generator
_Automatically convert digital images into printable film negatives. Compatible with iPhone HEIC format._

**To run this script, please first execute:**
`pip install -r requirements.txt`



**Project Configuration**</u>
- MODE = "BW", "COLOR"
- FORMAT = "35mm", "120mm", "4x5"
- DPI = 1200 # High-fidelity output resolution



<u>**Exposure & Density Tuning**</u>
- DENSITY_FACTOR: 1.4 - 1.6 is usually the 'sweet spot' for laser-printed negatives.
- CONTRAST_FACTOR: 1.2 - 1.3 keeps the tonal range natural without clipping.
- BASE_FOG: 0.15 prints a layer of gray toner across the entire negative to artificially restrict the flow of light through the enlarger.
